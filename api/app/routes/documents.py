"""Document processing and extraction endpoints"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
import logging
import uuid
import base64

from app.models.transaction import (
    TransactionExtractRequest,
    TransactionExtractResponse,
    BatchTransactionRequest,
    BatchTransactionResponse,
    Transaction
)
from app.services.document_processor import DocumentProcessor
from app.services.storage_service import StorageService
from app.config import Settings

router = APIRouter()
logger = logging.getLogger(__name__)
settings = Settings()

doc_processor = None
storage_service = None

@router.on_event("startup")
async def startup_event():
    """Initialize document processing services"""
    global doc_processor, storage_service
    
    doc_processor = DocumentProcessor(
        api_key=settings.openai_api_key,
        model="gpt-4-vision"
    )
    
    storage_service = StorageService(
        connection_string=settings.azure_storage_connection_string
    )

@router.post("/extract", response_model=TransactionExtractResponse)
async def extract_transaction(request: TransactionExtractRequest):
    """Extract transaction data from document URL"""
    try:
        request_id = str(uuid.uuid4())
        logger.info(f"Extracting transaction from document: {request.document_url}")
        
        if not doc_processor:
            raise HTTPException(status_code=503, detail="Document processor not initialized")
        
        extraction_result = await doc_processor.process_document_url(request.document_url)
        
        if not doc_processor.validate_transaction_json(extraction_result['data']):
            raise HTTPException(status_code=400, detail="Extracted data does not match transaction schema")
        
        transaction = Transaction(**extraction_result['data'])
        
        storage_path = None
        if request.save_to_storage and storage_service:
            storage_path = await storage_service.save_transaction(
                extraction_result['data'],
                request.document_id or request_id
            )
        
        logger.info(f"Transaction extraction completed: {request_id}")
        
        return TransactionExtractResponse(
            document_id=request.document_id or request_id,
            transaction=transaction,
            confidence=extraction_result['confidence'],
            storage_path=storage_path
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting transaction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_and_extract(file: UploadFile = File(...), save_to_storage: bool = Form(True)):
    """Upload document and extract transaction data"""
    try:
        request_id = str(uuid.uuid4())
        logger.info(f"Processing uploaded file: {file.filename}")
        
        if not doc_processor:
            raise HTTPException(status_code=503, detail="Document processor not initialized")
        
        file_content = await file.read()
        base64_data = base64.b64encode(file_content).decode('utf-8')
        
        extraction_result = await doc_processor.process_document_base64(base64_data)
        
        if not doc_processor.validate_transaction_json(extraction_result['data']):
            raise HTTPException(status_code=400, detail="Extracted data does not match transaction schema")
        
        transaction = Transaction(**extraction_result['data'])
        
        storage_path = None
        if save_to_storage and storage_service:
            storage_path = await storage_service.save_transaction(extraction_result['data'], request_id)
        
        logger.info(f"File processing completed: {request_id}")
        
        return TransactionExtractResponse(
            document_id=request_id,
            transaction=transaction,
            confidence=extraction_result['confidence'],
            storage_path=storage_path
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing uploaded file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch", response_model=BatchTransactionResponse)
async def batch_extract(request: BatchTransactionRequest):
    """Extract transactions from multiple documents"""
    try:
        batch_id = request.batch_id or str(uuid.uuid4())
        logger.info(f"Starting batch extraction: {batch_id} with {len(request.document_urls)} documents")
        
        if not doc_processor:
            raise HTTPException(status_code=503, detail="Document processor not initialized")
        
        transactions = []
        successful = 0
        failed = 0
        
        for idx, doc_url in enumerate(request.document_urls):
            try:
                logger.info(f"Processing document {idx + 1}/{len(request.document_urls)}")
                
                extraction_result = await doc_processor.process_document_url(doc_url)
                
                if doc_processor.validate_transaction_json(extraction_result['data']):
                    transaction = Transaction(**extraction_result['data'])
                    
                    storage_path = None
                    if request.save_to_storage and storage_service:
                        storage_path = await storage_service.save_transaction(
                            extraction_result['data'],
                            f"{batch_id}-{idx}"
                        )
                    
                    transactions.append(TransactionExtractResponse(
                        document_id=f"{batch_id}-{idx}",
                        transaction=transaction,
                        confidence=extraction_result['confidence'],
                        storage_path=storage_path
                    ))
                    successful += 1
                else:
                    failed += 1
                    logger.warning(f"Validation failed for document {idx}")
            
            except Exception as e:
                failed += 1
                logger.error(f"Error processing document {idx}: {str(e)}")
        
        batch_result = {
            "batch_id": batch_id,
            "total_documents": len(request.document_urls),
            "successful": successful,
            "failed": failed,
            "transactions": [t.dict() for t in transactions]
        }
        
        storage_path = None
        if request.save_to_storage and storage_service:
            storage_path = await storage_service.save_batch_results(batch_result, batch_id)
        
        logger.info(f"Batch extraction completed: {successful} successful, {failed} failed")
        
        return BatchTransactionResponse(
            batch_id=batch_id,
            total_documents=len(request.document_urls),
            successful=successful,
            failed=failed,
            transactions=transactions,
            storage_path=storage_path
        )
    
    except Exception as e:
        logger.error(f"Error in batch extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_transactions(prefix: str = "", max_results: int = 100):
    """List all extracted transactions"""
    try:
        if not storage_service:
            raise HTTPException(status_code=503, detail="Storage service not available")
        
        transactions = await storage_service.list_transactions(prefix, max_results)
        return {"transactions": transactions, "count": len(transactions)}
    
    except Exception as e:
        logger.error(f"Error listing transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
