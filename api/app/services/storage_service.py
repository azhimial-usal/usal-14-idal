"""Azure Storage service for document and data persistence"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class StorageService:
    """Service for Azure Blob Storage operations"""
    
    def __init__(self, connection_string: str = None, account_name: str = None):
        """Initialize storage service"""
        try:
            from azure.storage.blob import BlobServiceClient
            
            if connection_string:
                self.client = BlobServiceClient.from_connection_string(connection_string)
            elif account_name:
                self.client = BlobServiceClient(account_url=f"https://{account_name}.blob.core.windows.net")
            else:
                self.client = None
                logger.warning("Azure Storage not configured")
        
        except ImportError:
            logger.warning("azure-storage-blob not installed")
            self.client = None
    
    async def save_transaction(self, transaction_data: Dict[str, Any], document_id: str) -> Optional[str]:
        """Save extracted transaction to Azure Storage"""
        if not self.client:
            logger.warning("Storage service not configured, skipping save")
            return None
        
        try:
            timestamp = datetime.utcnow()
            container_name = "transactions"
            blob_name = f"{timestamp.year}/{timestamp.month:02d}/{timestamp.day:02d}/{document_id}.json"
            
            container_client = self.client.get_container_client(container_name)
            
            blob_data = json.dumps(transaction_data, indent=2, default=str)
            container_client.upload_blob(blob_name, blob_data, overwrite=True)
            
            logger.info(f"Saved transaction to {blob_name}")
            return f"{container_name}/{blob_name}"
        
        except Exception as e:
            logger.error(f"Error saving transaction to storage: {str(e)}")
            raise
    
    async def save_batch_results(self, batch_data: Dict[str, Any], batch_id: str) -> Optional[str]:
        """Save batch processing results to Azure Storage"""
        if not self.client:
            logger.warning("Storage service not configured, skipping save")
            return None
        
        try:
            timestamp = datetime.utcnow()
            container_name = "batch-results"
            blob_name = f"{timestamp.year}/{timestamp.month:02d}/{timestamp.day:02d}/batch-{batch_id}.json"
            
            container_client = self.client.get_container_client(container_name)
            
            blob_data = json.dumps(batch_data, indent=2, default=str)
            container_client.upload_blob(blob_name, blob_data, overwrite=True)
            
            logger.info(f"Saved batch results to {blob_name}")
            return f"{container_name}/{blob_name}"
        
        except Exception as e:
            logger.error(f"Error saving batch results: {str(e)}")
            raise
    
    async def list_transactions(self, prefix: str = "", max_results: int = 100) -> list:
        """List transactions in storage"""
        if not self.client:
            logger.warning("Storage service not configured")
            return []
        
        try:
            container_name = "transactions"
            container_client = self.client.get_container_client(container_name)
            
            blobs = container_client.list_blobs(name_starts_with=prefix)
            
            transactions = []
            for i, blob in enumerate(blobs):
                if i >= max_results:
                    break
                transactions.append({
                    "name": blob.name,
                    "size": blob.size,
                    "last_modified": blob.last_modified.isoformat() if blob.last_modified else None
                })
            
            return transactions
        
        except Exception as e:
            logger.error(f"Error listing transactions: {str(e)}")
            raise
