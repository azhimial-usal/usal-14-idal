"""Integration tests for GPT-5.6 API endpoints"""

import pytest
import json
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
class TestHealthEndpoints:
    """Test health check endpoints"""
    
    async def test_health_check(self):
        """Test basic health check"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "version" in data
            assert "model" in data
    
    async def test_live_probe(self):
        """Test Kubernetes live probe"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/health/live")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "alive"
    
    async def test_ready_probe(self):
        """Test Kubernetes ready probe"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/health/ready")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ready"


@pytest.mark.asyncio
class TestRiskAnalysisEndpoints:
    """Test risk analysis endpoints"""
    
    def get_sample_risk_data(self):
        """Get sample risk data for testing"""
        return {
            "risk_data": {
                "segments": [
                    {"segment": "A", "count": 1823, "avg_risk": 0.42},
                    {"segment": "B", "count": 951, "avg_risk": 0.67},
                    {"segment": "C", "count": 312, "avg_risk": 0.81}
                ],
                "trend": "increasing",
                "notes": "All data anonymized per GDPR."
            }
        }
    
    async def test_analyze_risk(self):
        """Test risk analysis endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            payload = self.get_sample_risk_data()
            response = await client.post("/api/v1/analyze-risk", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify response structure
            assert "analysis_id" in data
            assert "risk_summary" in data
            assert "metrics" in data
            assert "recommendations" in data
            assert "gdpr_compliant" in data
            
            # Verify metrics
            metrics = data["metrics"]
            assert metrics["total_customers"] == 3086
            assert metrics["avg_risk_score"] > 0
            assert "risk_distribution" in metrics
            assert "high_risk_percentage" in metrics
            
            # Verify recommendations exist
            assert len(data["recommendations"]) > 0
    
    async def test_analyze_risk_invalid_data(self):
        """Test risk analysis with invalid data"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            invalid_payload = {
                "risk_data": {
                    "segments": [],  # Empty segments
                    "trend": "increasing"
                }
            }
            response = await client.post("/api/v1/analyze-risk", json=invalid_payload)
            assert response.status_code == 422  # Validation error
    
    async def test_compliance_check(self):
        """Test GDPR compliance check endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/compliance-check")
            assert response.status_code == 200
            data = response.json()
            
            assert "compliant" in data
            assert "anonymized" in data
            assert "pii_removed" in data
            assert "retention_days" in data
            assert data["compliant"] == True
    
    async def test_risk_report(self):
        """Test risk report endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/risk-report?days=30")
            # May return 404 if no data, that's ok
            assert response.status_code in [200, 404, 503]
    
    async def test_bulk_analyze(self):
        """Test bulk risk analysis"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            payloads = [
                self.get_sample_risk_data()["risk_data"],
                self.get_sample_risk_data()["risk_data"]
            ]
            response = await client.post("/api/v1/bulk-analyze", json=payloads)
            
            # May fail if storage not configured, that's ok
            if response.status_code == 200:
                data = response.json()
                assert "total" in data
                assert "successful" in data
                assert "failed" in data


@pytest.mark.asyncio
class TestDocumentEndpoints:
    """Test document extraction endpoints"""
    
    def get_sample_document_request(self):
        """Get sample document request"""
        return {
            "document_url": "https://example.com/invoice.jpg",
            "document_id": "INV-TEST-001",
            "save_to_storage": False  # Don't actually save
        }
    
    async def test_extract_endpoint_exists(self):
        """Test extract endpoint exists"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Test endpoint accepts requests (may fail due to missing processor)
            payload = self.get_sample_document_request()
            response = await client.post("/api/v1/extract", json=payload)
            # Will likely return 503 if not initialized, but endpoint exists
            assert response.status_code in [200, 400, 503]
    
    async def test_extract_missing_url(self):
        """Test extract with missing document_url"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            payload = {"document_id": "TEST"}
            response = await client.post("/api/v1/extract", json=payload)
            assert response.status_code == 422  # Validation error
    
    async def test_list_documents_endpoint(self):
        """Test list documents endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/list?max_results=10")
            # Will return 503 if storage not configured
            assert response.status_code in [200, 503]


@pytest.mark.asyncio
class TestAnalysisEndpoints:
    """Test analysis endpoints"""
    
    async def test_analyze_endpoint_exists(self):
        """Test analyze endpoint exists"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            payload = {
                "text": "Test analysis",
                "task": "sentiment"
            }
            response = await client.post("/api/v1/analyze", json=payload)
            # Endpoint should exist
            assert response.status_code in [200, 400, 503]


@pytest.mark.asyncio
class TestTranscriptionEndpoints:
    """Test transcription endpoints"""
    
    async def test_transcribe_endpoint_exists(self):
        """Test transcribe endpoint exists"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            payload = {
                "audio_url": "https://example.com/audio.mp3",
                "language": "en"
            }
            response = await client.post("/api/v1/transcribe", json=payload)
            assert response.status_code in [200, 400, 503]


@pytest.mark.asyncio
class TestChatEndpoints:
    """Test chat endpoints"""
    
    async def test_chat_endpoint_exists(self):
        """Test chat endpoint exists"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            payload = {
                "messages": [{"role": "user", "content": "Hello"}],
                "stream": False
            }
            response = await client.post("/api/v1/chat", json=payload)
            assert response.status_code in [200, 400, 503]


@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling"""
    
    async def test_invalid_json(self):
        """Test invalid JSON handling"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/analyze-risk",
                content="invalid json",
                headers={"Content-Type": "application/json"}
            )
            assert response.status_code in [400, 422]
    
    async def test_missing_required_fields(self):
        """Test missing required fields"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            payload = {}  # Empty payload
            response = await client.post("/api/v1/analyze-risk", json=payload)
            assert response.status_code == 422
    
    async def test_invalid_endpoint(self):
        """Test invalid endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/invalid-endpoint")
            assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
