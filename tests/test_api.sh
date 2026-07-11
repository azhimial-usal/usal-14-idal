#!/bin/bash
# Test script for local API testing

set -e

API_URL="${API_URL:-http://localhost:8000}"
API_ENDPOINT="$API_URL/api/v1"

echo "🧪 Testing GPT-5.6 API Endpoints"
echo "================================="
echo "Base URL: $API_URL"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Helper function for testing
test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local expected_status=$5
    
    echo -n "Testing $name... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$API_ENDPOINT$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$API_ENDPOINT$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "$expected_status" ] || echo "$http_code" | grep -q "$expected_status"; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $http_code)"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} (Expected $expected_status, got $http_code)"
        echo "Response: $body"
        ((FAILED++))
    fi
}

# Test 1: Health Check
echo -e "\n${YELLOW}Health Endpoints:${NC}"
test_endpoint "Health Check" "GET" "/health" "" "200"
test_endpoint "Live Probe" "GET" "/health/live" "" "200"
test_endpoint "Ready Probe" "GET" "/health/ready" "" "200"

# Test 2: Risk Analysis
echo -e "\n${YELLOW}Risk Analysis Endpoints:${NC}"

RISK_DATA='{
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

test_endpoint "Analyze Risk" "POST" "/analyze-risk" "$RISK_DATA" "200"
test_endpoint "Compliance Check" "GET" "/compliance-check" "" "200"
test_endpoint "Risk Report" "GET" "/risk-report?days=30" "" "200|404|503"

# Test 3: Document Extraction
echo -e "\n${YELLOW}Document Extraction Endpoints:${NC}"

DOC_DATA='{
  "document_url": "https://example.com/invoice.jpg",
  "document_id": "TEST-001",
  "save_to_storage": false
}'

test_endpoint "Extract Endpoint" "POST" "/extract" "$DOC_DATA" "200|400|503"
test_endpoint "List Documents" "GET" "/list?max_results=10" "" "200|503"

# Test 4: Error Handling
echo -e "\n${YELLOW}Error Handling:${NC}"
test_endpoint "Invalid Endpoint" "GET" "/invalid-endpoint" "" "404"
test_endpoint "Invalid JSON" "POST" "/analyze-risk" "{invalid}" "400|422"
test_endpoint "Missing Fields" "POST" "/analyze-risk" "{}" "422"

# Test 5: Other Endpoints
echo -e "\n${YELLOW}Other Endpoints:${NC}"
test_endpoint "Analyze" "POST" "/analyze" '{"text":"test"}' "200|400|503"
test_endpoint "Transcribe" "POST" "/transcribe" '{"audio_url":"test"}' "200|400|503"
test_endpoint "Chat" "POST" "/chat" '{"messages":[]}' "200|400|503"

# Summary
echo -e "\n${YELLOW}================================="
echo "Test Results Summary"
echo "=================================${NC}"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}\n"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed${NC}\n"
    exit 1
fi
