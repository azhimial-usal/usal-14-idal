"""Document processing service for transaction extraction"""

import json
import logging
import base64
from typing import Dict, Any, Optional
from datetime import datetime
import aiohttp

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process documents and extract transaction data using OpenAI Vision"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-vision"):
        """Initialize document processor"""
        self.api_key = api_key
        self.model = model
        self.extraction_prompt = self._build_extraction_prompt()
    
    def _build_extraction_prompt(self) -> str:
        """Build the extraction prompt for document analysis"""
        return """Extract transaction information from this document and return ONLY valid JSON:

{
  "type": "invoice|receipt|check|payment|transfer|wire|other",
  "dates": {"received": "YYYY-MM-DD or null", "paid": "YYYY-MM-DD or null"},
  "amount": 0.00,
  "payee": {"name": "string", "address": "string or null"},
  "signature": "string or null"
}

Return ONLY valid JSON, no extra text."""
    
    async def process_document_url(self, document_url: str) -> Dict[str, Any]:
        """Process document from URL and extract transaction data"""
        try:
            logger.info(f"Processing document from URL: {document_url}")
            
            if not self._is_valid_url(document_url):
                raise ValueError(f"Invalid document URL: {document_url}")
            
            image_data = await self._download_image(document_url)
            base64_image = base64.b64encode(image_data).decode('utf-8')
            result = await self._extract_with_vision_api(base64_image)
            
            logger.info(f"Successfully extracted transaction data from {document_url}")
            return result
        
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise
    
    async def process_document_base64(self, base64_data: str) -> Dict[str, Any]:
        """Process document from base64 encoded data"""
        try:
            logger.info("Processing document from base64 data")
            result = await self._extract_with_vision_api(base64_data)
            return result
        
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise
    
    async def _extract_with_vision_api(self, base64_image: str) -> Dict[str, Any]:
        """Call OpenAI Vision API to extract transaction data"""
        try:
            import openai
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": self.extraction_prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    }
                ],
                temperature=0.2,
                max_tokens=500
            )
            
            response_text = response.choices[0].message.content.strip()
            
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            
            transaction_data = json.loads(response_text)
            
            return {
                "data": transaction_data,
                "confidence": 0.95,
                "model": self.model,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse extraction response: {str(e)}")
            raise ValueError(f"Invalid JSON in extraction response: {str(e)}")
        except Exception as e:
            logger.error(f"Error calling Vision API: {str(e)}")
            raise
    
    async def _download_image(self, url: str) -> bytes:
        """Download image from URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise ValueError(f"Failed to download image: HTTP {response.status}")
                    return await response.read()
        
        except Exception as e:
            logger.error(f"Error downloading image: {str(e)}")
            raise
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        return url.startswith(('http://', 'https://', 'data:'))
    
    def validate_transaction_json(self, transaction_data: Dict[str, Any]) -> bool:
        """Validate extracted transaction data against schema"""
        required_fields = ['type', 'dates', 'amount', 'payee']
        
        for field in required_fields:
            if field not in transaction_data:
                logger.error(f"Missing required field: {field}")
                return False
        
        if not isinstance(transaction_data.get('dates'), dict):
            logger.error("Dates must be a dictionary")
            return False
        
        if not isinstance(transaction_data.get('amount'), (int, float)):
            logger.error("Amount must be a number")
            return False
        
        if not isinstance(transaction_data.get('payee'), dict):
            logger.error("Payee must be a dictionary")
            return False
        
        if 'name' not in transaction_data.get('payee', {}):
            logger.error("Payee name is required")
            return False
        
        return True
