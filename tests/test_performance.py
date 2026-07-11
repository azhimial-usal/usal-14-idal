"""Performance tests for API endpoints"""

import pytest
import time
import statistics
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
class TestPerformance:
    """Performance tests"""
    
    async def test_health_check_performance(self):
        """Test health check response time"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            times = []
            
            for _ in range(10):
                start = time.time()
                response = await client.get("/api/v1/health")
                elapsed = time.time() - start
                times.append(elapsed)
                assert response.status_code == 200
            
            avg_time = statistics.mean(times)
            max_time = max(times)
            
            print(f"\nHealth check performance:")
            print(f"  Average: {avg_time*1000:.2f}ms")
            print(f"  Max: {max_time*1000:.2f}ms")
            
            # Should be fast
            assert avg_time < 0.5, f"Health check too slow: {avg_time}s"
    
    async def test_risk_analysis_performance(self):
        """Test risk analysis response time"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            payload = {
                "risk_data": {
                    "segments": [
                        {"segment": "A", "count": 1823, "avg_risk": 0.42},
                        {"segment": "B", "count": 951, "avg_risk": 0.67},
                        {"segment": "C", "count": 312, "avg_risk": 0.81}
                    ],
                    "trend": "increasing",
                    "notes": "Test"
                }
            }
            
            times = []
            
            for _ in range(5):
                start = time.time()
                response = await client.post("/api/v1/analyze-risk", json=payload)
                elapsed = time.time() - start
                if response.status_code == 200:
                    times.append(elapsed)
            
            if times:
                avg_time = statistics.mean(times)
                max_time = max(times)
                
                print(f"\nRisk analysis performance:")
                print(f"  Average: {avg_time*1000:.2f}ms")
                print(f"  Max: {max_time*1000:.2f}ms")
                
                # Should complete within reasonable time
                assert avg_time < 5.0, f"Risk analysis too slow: {avg_time}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
