"""Risk analysis service for EU customers"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import statistics

from app.models.risk_analysis import (
    RiskSummary, RiskMetrics, RiskLevel, Trend,
    RiskAnalysisResponse, RiskReport, ComplianceMetadata
)

logger = logging.getLogger(__name__)

class RiskAnalyzer:
    """Service for analyzing EU customer risk data"""
    
    def __init__(self):
        """Initialize risk analyzer"""
        self.compliance_metadata = ComplianceMetadata()
    
    def analyze_risk_data(self, risk_summary: RiskSummary) -> RiskMetrics:
        """Analyze risk data and calculate metrics"""
        try:
            logger.info("Analyzing risk data")
            
            # Calculate total customers
            total_customers = sum(segment.count for segment in risk_summary.segments)
            
            # Calculate average risk score
            weighted_risks = [
                segment.avg_risk * segment.count 
                for segment in risk_summary.segments
            ]
            avg_risk_score = sum(weighted_risks) / total_customers if total_customers > 0 else 0
            
            # Categorize by risk level
            risk_distribution = self._categorize_risk(risk_summary.segments, total_customers)
            
            # Calculate high-risk percentage
            high_risk_count = risk_distribution.get('high', 0) + risk_distribution.get('critical', 0)
            high_risk_percentage = (high_risk_count / total_customers * 100) if total_customers > 0 else 0
            
            metrics = RiskMetrics(
                total_customers=total_customers,
                avg_risk_score=round(avg_risk_score, 4),
                risk_distribution=risk_distribution,
                high_risk_percentage=round(high_risk_percentage, 2)
            )
            
            logger.info(f"Analysis complete: {total_customers} customers, avg risk: {avg_risk_score}")
            return metrics
        
        except Exception as e:
            logger.error(f"Error analyzing risk data: {str(e)}")
            raise
    
    def _categorize_risk(self, segments: List, total_customers: int) -> Dict[str, int]:
        """Categorize customers by risk level"""
        distribution = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        
        for segment in segments:
            risk_score = segment.avg_risk
            
            if risk_score < 0.25:
                risk_level = 'low'
            elif risk_score < 0.50:
                risk_level = 'medium'
            elif risk_score < 0.75:
                risk_level = 'high'
            else:
                risk_level = 'critical'
            
            distribution[risk_level] += segment.count
        
        return distribution
    
    def generate_recommendations(self, metrics: RiskMetrics, trend: Trend) -> List[str]:
        """Generate risk management recommendations"""
        recommendations = []
        
        # Based on average risk score
        if metrics.avg_risk_score > 0.7:
            recommendations.append(
                "High average risk score detected. Implement enhanced monitoring and review policies."
            )
        
        if metrics.avg_risk_score > 0.5:
            recommendations.append(
                "Consider conducting comprehensive risk assessments across customer base."
            )
        
        # Based on trend
        if trend == Trend.INCREASING:
            recommendations.append(
                "Risk trend is increasing. Investigate root causes and implement preventive measures."
            )
            recommendations.append(
                "Accelerate compliance audits and customer due diligence processes."
            )
        
        elif trend == Trend.DECREASING:
            recommendations.append(
                "Positive trend observed. Continue current risk mitigation strategies."
            )
        
        # Based on high-risk percentage
        if metrics.high_risk_percentage > 15:
            recommendations.append(
                "Critical: More than 15% of customers are high-risk. Immediate action required."
            )
        
        if metrics.high_risk_percentage > 5:
            recommendations.append(
                "Increase frequency of risk reviews for high-risk customer segment."
            )
        
        # GDPR recommendations
        recommendations.append(
            "Ensure all data processing complies with GDPR regulations."
        )
        recommendations.append(
            "Maintain audit trail of all risk assessments for compliance purposes."
        )
        
        return recommendations
    
    def calculate_segment_metrics(self, segments: List) -> Dict[str, Any]:
        """Calculate metrics for each segment"""
        segment_metrics = {}
        
        for segment in segments:
            segment_metrics[segment.segment] = {
                "count": segment.count,
                "avg_risk": segment.avg_risk,
                "risk_level": self._get_risk_level(segment.avg_risk),
                "percentage": f"{(segment.count / sum(s.count for s in segments) * 100):.1f}%"
            }
        
        return segment_metrics
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Get risk level from score"""
        if risk_score < 0.25:
            return "LOW"
        elif risk_score < 0.50:
            return "MEDIUM"
        elif risk_score < 0.75:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def audit_compliance(self) -> ComplianceMetadata:
        """Audit GDPR compliance"""
        logger.info("Conducting GDPR compliance audit")
        
        self.compliance_metadata.last_audit = datetime.utcnow()
        self.compliance_metadata.audit_trail.append(
            f"Audit conducted at {datetime.utcnow().isoformat()}"
        )
        
        return self.compliance_metadata
    
    def validate_gdpr_compliance(self, risk_summary: RiskSummary) -> bool:
        """Validate GDPR compliance of risk data"""
        logger.info("Validating GDPR compliance")
        
        # Check if data contains anonymization note
        if "anonymized" not in risk_summary.notes.lower() and \
           "gdpr" not in risk_summary.notes.lower():
            logger.warning("Risk summary does not mention anonymization or GDPR")
        
        # Check that we have no PII in segment names
        for segment in risk_summary.segments:
            if any(pii_indicator in segment.segment.lower() 
                   for pii_indicator in ['name', 'email', 'phone', 'id']):
                logger.error(f"Potential PII detected in segment: {segment.segment}")
                return False
        
        logger.info("GDPR compliance validation passed")
        return True
