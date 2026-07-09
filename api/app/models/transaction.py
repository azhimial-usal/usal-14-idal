"""Transaction data models"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class TransactionType(str, Enum):
    """Types of transactions"""
    INVOICE = "invoice"
    RECEIPT = "receipt"
    CHECK = "check"
    PAYMENT = "payment"
    TRANSFER = "transfer"
    WIRE = "wire"
    OTHER = "other"

class DateInfo(BaseModel):
    """Date information"""
    received: Optional[str] = Field(None, description="Date received (YYYY-MM-DD)")
    paid: Optional[str] = Field(None, description="Date paid (YYYY-MM-DD)")

class Payee(BaseModel):
    """Payee information"""
    name: str = Field(..., description="Name of the payee")
    address: Optional[str] = Field(None, description="Address of the payee")

class Transaction(BaseModel):
    """Transaction data model"""
    type: TransactionType = Field(..., description="Type of transaction")
    dates: DateInfo = Field(..., description="Date information")
    amount: float = Field(..., description="Total amount paid", gt=0)
    payee: Payee = Field(..., description="Payee information")
    signature: Optional[str] = Field(None, description="Signature of the payer")
    
    @validator('amount')
    def validate_amount(cls, v):
        if v < 0:
            raise ValueError('Amount must be positive')
        return round(v, 2)

class TransactionExtractRequest(BaseModel):
    """Request to extract transaction from document"""
    document_url: str = Field(..., description="URL to document image or PDF")
    document_id: Optional[str] = Field(None, description="Unique document identifier")
    save_to_storage: bool = Field(default=True, description="Save extracted data to Azure Storage")

class TransactionExtractResponse(BaseModel):
    """Response from transaction extraction"""
    document_id: str = Field(..., description="Document ID")
    transaction: Transaction = Field(..., description="Extracted transaction data")
    confidence: float = Field(..., description="Extraction confidence score (0-1)")
    extracted_at: datetime = Field(default_factory=datetime.utcnow)
    storage_path: Optional[str] = Field(None, description="Path in Azure Storage where data was saved")
