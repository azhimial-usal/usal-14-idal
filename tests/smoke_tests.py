"""Smoke tests for API endpoints"""

import pytest
import requests
import time
from typing import Optional

class SmokeTests:
    """Smoke tests for deployed API"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.api_url = f"{self.base_url}/api/v1"
    
    def test_health_check(self) -> bool:
        """Test health endpoint"""
        try:
            response = requests.get(
                f"{self.api_url}/health",
                timeout=self.timeout
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            print("✓ Health check passed")
            return True
        except Exception as e:
            print(f"✗ Health check failed: {str(e)}")
            return False
    
    def test_risk_analysis(self) -> bool:
        """Test risk analysis endpoint"""
        try:
            payload = {
                "risk_data": {
                    "segments": [
                        {"segment": "A", "count": 1823, "avg_risk": 0.42},
                        {"segment": "B", "count": 951, "avg_risk": 0.67},
                        {"segment": "C", "count": 312, "avg_risk": 0.81}
                    ],
                    "trend": "increasing",
                    "notes": "Test data"
                }
            }
            response = requests.post(
                f"{self.api_url}/analyze-risk",
                json=payload,
                timeout=self.timeout
            )
            assert response.status_code == 200
            data = response.json()
            assert "analysis_id" in data
            assert "metrics" in data
            print("✓ Risk analysis endpoint passed")
            return True
        except Exception as e:
            print(f"✗ Risk analysis endpoint failed: {str(e)}")
            return False
    
    def test_compliance_check(self) -> bool:
        """Test compliance check endpoint"""
        try:
            response = requests.get(
                f"{self.api_url}/compliance-check",
                timeout=self.timeout
            )
            assert response.status_code == 200
            data = response.json()
            assert "compliant" in data
            print("✓ Compliance check endpoint passed")
            return True
        except Exception as e:
            print(f"✗ Compliance check endpoint failed: {str(e)}")
            return False
    
    def test_swagger_docs(self) -> bool:
        """Test Swagger documentation endpoint"""
        try:
            response = requests.get(
                f"{self.base_url}/docs",
                timeout=self.timeout
            )
            assert response.status_code == 200
            print("✓ Swagger docs endpoint passed")
            return True
        except Exception as e:
            print(f"✗ Swagger docs endpoint failed: {str(e)}")
            return False
    
    def run_all_tests(self) -> dict:
        """Run all smoke tests"""
        print(f"\n🧪 Running smoke tests against {self.base_url}\n")
        
        results = {
            "health_check": self.test_health_check(),
            "risk_analysis": self.test_risk_analysis(),
            "compliance_check": self.test_compliance_check(),
            "swagger_docs": self.test_swagger_docs()
        }
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        print(f"\n📊 Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("✅ All smoke tests passed!\n")
        else:
            print("⚠️  Some tests failed. Check output above.\n")
        
        return results


if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Smoke tests for API")
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="API base URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)"
    )
    
    args = parser.parse_args()
    
    tester = SmokeTests(args.api_url, args.timeout)
    results = tester.run_all_tests()
    
    # Exit with error if any test failed
    if not all(results.values()):
        sys.exit(1)
