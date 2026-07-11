# API Testing Guide

## Quick Start

### Local Testing

```bash
# Start API locally
docker-compose up -d

# Run smoke tests
python tests/smoke_tests.py --api-url http://localhost:8000

# Run bash test script
bash tests/test_api.sh

# Run pytest tests
pytest tests/test_endpoints.py -v
pytest tests/test_performance.py -v -s
```

### Azure Testing

```bash
# After deployment
API_URL="https://gpt-56-api-prod-123.azurewebsites.net"
python tests/smoke_tests.py --api-url $API_URL
```

---

## Available Test Files

### 1. `test_endpoints.py` - Unit Tests
Comprehensive pytest tests for all endpoints

```bash
pytest tests/test_endpoints.py -v
```

**Tests:**
- Health check endpoints (3 tests)
- Risk analysis endpoints (5 tests)
- Document extraction endpoints (3 tests)
- Analysis endpoints (1 test)
- Transcription endpoints (1 test)
- Chat endpoints (1 test)
- Error handling (3 tests)

### 2. `smoke_tests.py` - Integration Tests
Quick validation tests for deployed API

```bash
python tests/smoke_tests.py --api-url http://localhost:8000
```

**Tests:**
- Health check
- Risk analysis
- Compliance check
- Swagger documentation

### 3. `test_performance.py` - Performance Tests
Measure response times

```bash
pytest tests/test_performance.py -v -s
```

**Tests:**
- Health check performance
- Risk analysis performance

### 4. `test_api.sh` - Bash Script
CURL-based endpoint testing

```bash
bash tests/test_api.sh
# or with custom URL
API_URL=https://your-api.com bash tests/test_api.sh
```

---

## Test Coverage

### Health Endpoints ✅
```bash
GET /api/v1/health
GET /api/v1/health/live
GET /api/v1/health/ready
```

### Risk Analysis Endpoints ✅
```bash
POST /api/v1/analyze-risk
GET  /api/v1/risk-report
GET  /api/v1/compliance-check
POST /api/v1/bulk-analyze
```

### Document Extraction Endpoints ✅
```bash
POST /api/v1/extract
POST /api/v1/upload
POST /api/v1/batch
GET  /api/v1/list
```

### Analysis Endpoints ✅
```bash
POST /api/v1/analyze
```

### Transcription Endpoints ✅
```bash
POST /api/v1/transcribe
```

### Chat Endpoints ✅
```bash
POST /api/v1/chat
```

---

## Manual Testing with cURL

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### Risk Analysis
```bash
curl -X POST http://localhost:8000/api/v1/analyze-risk \
  -H "Content-Type: application/json" \
  -d '{
    "risk_data": {
      "segments": [
        {"segment": "A", "count": 1823, "avg_risk": 0.42},
        {"segment": "B", "count": 951, "avg_risk": 0.67},
        {"segment": "C", "count": 312, "avg_risk": 0.81}
      ],
      "trend": "increasing",
      "notes": "All data anonymized per GDPR."
    }
  }'
```

### Compliance Check
```bash
curl http://localhost:8000/api/v1/compliance-check
```

### Bulk Risk Analysis
```bash
curl -X POST http://localhost:8000/api/v1/bulk-analyze \
  -H "Content-Type: application/json" \
  -d '[
    {
      "segments": [{"segment": "A", "count": 100, "avg_risk": 0.4}],
      "trend": "stable",
      "notes": "Test"
    }
  ]'
```

---

## Testing Workflow

### 1. Local Development
```bash
# Start containers
docker-compose up -d

# Run tests
pytest tests/ -v

# Check coverage
pytest tests/ --cov=app --cov-report=html
```

### 2. Pre-Deployment
```bash
# Build image
docker build -t gpt-56-api:test ./api

# Test image
docker run -p 8000:8000 gpt-56-api:test

# Run smoke tests
python tests/smoke_tests.py
```

### 3. Post-Deployment
```bash
# Test deployed API
API_URL="https://your-deployed-api.com"
python tests/smoke_tests.py --api-url $API_URL

# Run performance tests
pytest tests/test_performance.py -v -s
```

---

## CI/CD Integration

### GitHub Actions
Tests run automatically on:
- Push to main/develop
- Pull requests
- Manual trigger

```yaml
# Runs in .github/workflows/api-tests.yml
- pytest tests/ --cov=app
- bash tests/test_api.sh
```

### Azure DevOps
Tests included in deployment pipeline

```yaml
# Runs in azure-devops/azure-pipelines.yml
- task: pytest
  inputs:
    testDirectory: 'tests'
```

---

## Expected Results

### Successful Run
```
✓ Health check passed
✓ Risk analysis endpoint passed
✓ Compliance check endpoint passed
✓ Swagger docs endpoint passed

📊 Results: 4/4 tests passed
✅ All smoke tests passed!
```

### With Failures
```
✗ Health check failed: Connection refused
✗ Risk analysis endpoint failed: 503 Service Unavailable

📊 Results: 0/4 tests passed
⚠️  Some tests failed. Check output above.
```

---

## Troubleshooting

### Connection Refused
```bash
# API not running
# Solution: Start containers
docker-compose up -d
```

### 503 Service Unavailable
```bash
# Service not initialized
# Solution: Wait 10 seconds and retry
sleep 10
python tests/smoke_tests.py
```

### Timeout
```bash
# API slow to respond
# Solution: Increase timeout
python tests/smoke_tests.py --timeout 60
```

### Invalid Response
```bash
# API returning unexpected format
# Solution: Check logs
docker logs {CONTAINER_ID}
az webapp log tail --name {APP_NAME} --resource-group {RG}
```

---

## Performance Benchmarks

Expected response times:

| Endpoint | Local | Azure |
|----------|-------|-------|
| Health | <50ms | <100ms |
| Risk Analysis | <500ms | <1000ms |
| Compliance Check | <100ms | <300ms |
| Document Extract | <5s | <10s |

---

## Next Steps

1. ✅ Run local tests
2. ✅ Run smoke tests
3. ✅ Check performance
4. ✅ Deploy to Azure
5. ✅ Run remote tests

**All tests passing?** 🎉 Your API is production-ready!
