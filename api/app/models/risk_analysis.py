"""Risk analysis models for EU customers"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    """Risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Trend(str, Enum):
    """Risk trend direction"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"

class RiskSegment(BaseModel):
    """Customer risk segment"""
    segment: str = Field(..., description="Segment identifier (A, B, C, etc.)")
    count: int = Field(..., description="Number of customers in segment", ge=0)
    avg_risk: float = Field(..., description="Average risk score (0-1)", ge=0, le=1)
    
    @validator('segment')
    def validate_segment(cls, v):
        if not v or len(v) > 10:
            raise ValueError('Segment must be between 1-10 characters')
        return v.upper()

class RiskSummary(BaseModel):
    """EU customer risk summary"""
    segments: List[RiskSegment] = Field(..., description="List of risk segments")
    trend: Trend = Field(..., description="Overall risk trend")
    notes: str = Field(default="All data anonymized per GDPR", description="Additional notes")
    
    @validator('segments')
    def validate_segments(cls, v):
        if not v:
            raise ValueError('At least one segment is required')
        return v

class RiskAnalysisRequest(BaseModel):
    """Request for risk analysis"""
    risk_data: RiskSummary = Field(..., description="Risk summary data")
    country_code: Optional[str] = Field(None, description="EU country code (DE, FR, IT, etc.)")
    analysis_date: Optional[datetime] = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = Field(None, description="Correlation ID for tracking")

class RiskMetrics(BaseModel):
    """Calculated risk metrics"""
    total_customers: int = Field(..., description="Total number of customers")
    avg_risk_score: float = Field(..., description="Average risk across all customers")
    risk_distribution: Dict[str, int] = Field(..., description="Distribution by risk level")
    high_risk_percentage: float = Field(..., description="Percentage of high-risk customers")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_customers": 3086,
                "avg_risk_score": 0.58,
                "risk_distribution": {
                    "low": 1500,
                    "medium": 1200,
                    "high": 300,
                    "critical": 86
                },
                "high_risk_percentage": 12.5
            }
        }

class RiskAnalysisResponse(BaseModel):
    """Response from risk analysis"""
    analysis_id: str = Field(..., description="Unique analysis ID")
    risk_summary: RiskSummary = Field(..., description="Risk summary")
    metrics: RiskMetrics = Field(..., description="Calculated metrics")
    recommendations: List[str] = Field(..., description="Risk management recommendations")
    gdpr_compliant: bool = Field(default=True, description="GDPR compliance status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    storage_path: Optional[str] = Field(None, description="Path where analysis was stored")

class RiskReport(BaseModel):
    """Comprehensive risk report"""
    report_id: str = Field(..., description="Report ID")
    analysis_date: datetime = Field(..., description="Analysis date")
    total_analyses: int = Field(..., description="Number of analyses in report")
    overall_trend: Trend = Field(..., description="Overall trend")
    average_risk: float = Field(..., description="Average risk across all analyses")
    segment_summary: Dict[str, Any] = Field(..., description="Summary by segment")
    recommendations: List[str] = Field(..., description="Key recommendations")
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class ComplianceMetadata(BaseModel):
    """GDPR compliance metadata"""
    anonymized: bool = Field(default=True, description="Data is anonymized")
    pii_removed: bool = Field(default=True, description="PII has been removed")
    retention_days: int = Field(default=90, description="Data retention period")
    last_audit: Optional[datetime] = Field(None, description="Last compliance audit")
    audit_trail: List[str] = Field(default_factory=list, description="Audit trail")
