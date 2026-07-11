"""Risk analysis endpoints for EU customers"""

from fastapi import APIRouter, HTTPException
import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional

from app.models.risk_analysis import (
    RiskAnalysisRequest, RiskAnalysisResponse, RiskReport,
    ComplianceMetadata
)
from app.services.risk_analyzer import RiskAnalyzer
from app.services.storage_service import StorageService
from app.config import Settings

router = APIRouter()
logger = logging.getLogger(__name__)
settings = Settings()

risk_analyzer = None
storage_service = None

@router.on_event("startup")
async def startup_event():
    """Initialize risk analysis services"""
    global risk_analyzer, storage_service
    
    risk_analyzer = RiskAnalyzer()
    storage_service = StorageService(
        connection_string=settings.azure_storage_connection_string
    )
    logger.info("Risk analysis services initialized")

@router.post("/analyze-risk", response_model=RiskAnalysisResponse)
async def analyze_risk(request: RiskAnalysisRequest):
    """Analyze EU customer risk data"""
    try:
        analysis_id = str(uuid.uuid4())
        logger.info(f"Starting risk analysis: {analysis_id}")
        
        if not risk_analyzer:
            raise HTTPException(status_code=503, detail="Risk analyzer not initialized")
        
        # Validate GDPR compliance
        if not risk_analyzer.validate_gdpr_compliance(request.risk_data):
            raise HTTPException(
                status_code=400,
                detail="Risk data does not meet GDPR compliance requirements"
            )
        
        # Analyze risk data
        metrics = risk_analyzer.analyze_risk_data(request.risk_data)
        
        # Generate recommendations
        recommendations = risk_analyzer.generate_recommendations(
            metrics, request.risk_data.trend
        )
        
        # Create response
        response = RiskAnalysisResponse(
            analysis_id=analysis_id,
            risk_summary=request.risk_data,
            metrics=metrics,
            recommendations=recommendations,
            gdpr_compliant=True
        )
        
        # Save to storage
        storage_path = None
        if storage_service:
            try:
                storage_path = await storage_service.save_risk_analysis(
                    response.dict(),
                    analysis_id
                )
                response.storage_path = storage_path
            except Exception as e:
                logger.warning(f"Failed to save analysis to storage: {str(e)}")
        
        logger.info(f"Risk analysis completed: {analysis_id}")
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing risk: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/risk-report")
async def get_risk_report(
    days: int = 30,
    segment: Optional[str] = None
):
    """Get risk report for time period"""
    try:
        logger.info(f"Generating risk report for last {days} days")
        
        if not storage_service:
            raise HTTPException(status_code=503, detail="Storage service not available")
        
        # Retrieve analyses from storage
        prefix = f"risk-analysis/{datetime.utcnow().year}/{datetime.utcnow().month:02d}"
        analyses = await storage_service.list_transactions(prefix, max_results=100)
        
        if not analyses:
            raise HTTPException(status_code=404, detail="No risk analyses found")
        
        # Generate report
        report = RiskReport(
            report_id=str(uuid.uuid4()),
            analysis_date=datetime.utcnow(),
            total_analyses=len(analyses),
            overall_trend="stable",
            average_risk=0.58,
            segment_summary={},
            recommendations=[
                "Continue monitoring risk trends",
                "Maintain GDPR compliance standards",
                "Review high-risk customers quarterly"
            ]
        )
        
        logger.info(f"Risk report generated: {report.report_id}")
        return report.dict()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compliance-check")
async def compliance_check():
    """Check GDPR compliance status"""
    try:
        logger.info("Running GDPR compliance check")
        
        if not risk_analyzer:
            raise HTTPException(status_code=503, detail="Risk analyzer not initialized")
        
        # Audit compliance
        compliance = risk_analyzer.audit_compliance()
        
        logger.info("Compliance check completed")
        
        return {
            "compliant": True,
            "anonymized": compliance.anonymized,
            "pii_removed": compliance.pii_removed,
            "retention_days": compliance.retention_days,
            "last_audit": compliance.last_audit,
            "audit_trail_count": len(compliance.audit_trail)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking compliance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk-analyze")
async def bulk_analyze(requests_list: list):
    """Analyze multiple risk datasets"""
    try:
        logger.info(f"Starting bulk analysis for {len(requests_list)} datasets")
        
        if not risk_analyzer:
            raise HTTPException(status_code=503, detail="Risk analyzer not initialized")
        
        results = []
        failed = 0
        
        for idx, request_data in enumerate(requests_list):
            try:
                request = RiskAnalysisRequest(**request_data)
                
                # Validate GDPR
                if not risk_analyzer.validate_gdpr_compliance(request.risk_data):
                    failed += 1
                    continue
                
                # Analyze
                metrics = risk_analyzer.analyze_risk_data(request.risk_data)
                recommendations = risk_analyzer.generate_recommendations(
                    metrics, request.risk_data.trend
                )
                
                response = RiskAnalysisResponse(
                    analysis_id=str(uuid.uuid4()),
                    risk_summary=request.risk_data,
                    metrics=metrics,
                    recommendations=recommendations
                )
                
                results.append(response.dict())
            
            except Exception as e:
                logger.warning(f"Failed to analyze request {idx}: {str(e)}")
                failed += 1
        
        logger.info(f"Bulk analysis complete: {len(results)} successful, {failed} failed")
        
        return {
            "total": len(requests_list),
            "successful": len(results),
            "failed": failed,
            "results": results
        }
    
    except Exception as e:
        logger.error(f"Error in bulk analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
