# API Endpoints Reference

## Base URL

```
Local:  http://localhost:8000/api/v1
Azure:  https://{app-name}.azurewebsites.net/api/v1
```

## Health Endpoints

### Health Check

```http
GET /health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "model": "gpt-4-turbo",
  "timestamp": "2024-01-22T10:00:00Z"
}
```

### Live Probe (Kubernetes)

```http
GET /health/live
```

**Response (200 OK):**
```json
{"status": "alive"}
```

### Ready Probe (Kubernetes)

```http
GET /health/ready
```

**Response (200 OK):**
```json
{"status": "ready"}
```

---

## Document Extraction Endpoints

### Extract from URL

```http
POST /extract
Content-Type: application/json
```

**Request:**
```json
{
  "document_url": "https://example.com/invoice.jpg",
  "document_id": "INV-2024-001",
  "save_to_storage": true
}
```

**Response (200 OK):**
```json
{
  "document_id": "INV-2024-001",
  "transaction": {
    "type": "invoice",
    "dates": {"received": "2024-01-15", "paid": "2024-01-20"},
    "amount": 1500.50,
    "payee": {"name": "Acme Corp", "address": "123 Main St"},
    "signature": "J. Doe"
  },
  "confidence": 0.95,
  "extracted_at": "2024-01-22T10:30:00Z",
  "storage_path": "transactions/2024/01/22/INV-2024-001.json"
}
```

---

### Upload and Extract

```http
POST /upload
Content-Type: multipart/form-data
```

**Request:**
```
file: <binary>
save_to_storage: true
```

**Response (200 OK):**
```json
{
  "document_id": "req-abc123",
  "transaction": { /* ... */ },
  "confidence": 0.95,
  "storage_path": "transactions/2024/01/22/req-abc123.json"
}
```

---

### Batch Extraction

```http
POST /batch
Content-Type: application/json
```

**Request:**
```json
{
  "document_urls": [
    "https://example.com/invoice1.jpg",
    "https://example.com/invoice2.jpg",
    "https://example.com/invoice3.jpg"
  ],
  "batch_id": "BATCH-2024-001",
  "save_to_storage": true
}
```

**Response (200 OK):**
```json
{
  "batch_id": "BATCH-2024-001",
  "total_documents": 3,
  "successful": 3,
  "failed": 0,
  "transactions": [
    { /* transaction 1 */ },
    { /* transaction 2 */ },
    { /* transaction 3 */ }
  ],
  "storage_path": "batch-results/2024/01/22/batch-BATCH-2024-001.json"
}
```

---

### List Transactions

```http
GET /list?prefix=2024/01&max_results=50
```

**Response (200 OK):**
```json
{
  "transactions": [
    {
      "name": "transactions/2024/01/22/INV-2024-001.json",
      "size": 512,
      "last_modified": "2024-01-22T10:30:00Z"
    }
  ],
  "count": 1
}
```

---

## Analysis Endpoints

### Multimodal Analysis

```http
POST /analyze
Content-Type: application/json
```

**Request:**
```json
{
  "text": "Analyze this",
  "audio_url": "https://example.com/audio.mp3",
  "image_url": "https://example.com/image.jpg",
  "task": "sentiment",
  "custom_prompt": null
}
```

**Response (200 OK):**
```json
{
  "id": "req-123",
  "analysis": "The sentiment analysis shows...",
  "confidence": 0.95,
  "task": "sentiment",
  "timestamp": "2024-01-22T10:30:00Z",
  "metadata": {}
}
```

---

## Transcription Endpoints

### Audio Transcription

```http
POST /transcribe
Content-Type: application/json
```

**Request:**
```json
{
  "audio_url": "https://example.com/audio.mp3",
  "language": "en"
}
```

**Response (200 OK):**
```json
{
  "id": "req-456",
  "transcription": "The transcribed text from audio",
  "language": "en",
  "duration": 45.5,
  "timestamp": "2024-01-22T10:35:00Z"
}
```

---

## Chat Endpoints

### Chat with Context

```http
POST /chat
Content-Type: application/json
```

**Request:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "What's in this image?",
      "image_url": "https://example.com/image.jpg"
    }
  ],
  "system_prompt": "You are helpful",
  "stream": false
}
```

**Response (200 OK):**
```json
{
  "id": "req-789",
  "message": "The image shows...",
  "timestamp": "2024-01-22T10:40:00Z",
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 200,
    "total_tokens": 350
  }
}
```

---

## Error Responses

### 400 Bad Request

```json
{
  "error": "Invalid input",
  "timestamp": "2024-01-22T10:00:00Z"
}
```

### 401 Unauthorized

```json
{
  "error": "Missing or invalid authentication",
  "timestamp": "2024-01-22T10:00:00Z"
}
```

### 403 Forbidden

```json
{
  "error": "Access denied",
  "timestamp": "2024-01-22T10:00:00Z"
}
```

### 404 Not Found

```json
{
  "error": "Resource not found",
  "timestamp": "2024-01-22T10:00:00Z"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error",
  "timestamp": "2024-01-22T10:00:00Z"
}
```

### 503 Service Unavailable

```json
{
  "error": "Service not initialized",
  "timestamp": "2024-01-22T10:00:00Z"
}
```

---

## Rate Limits

All endpoints are rate limited to prevent abuse:

- **Free Tier:** 3 requests/minute
- **Pro Tier:** 100 requests/minute
- **Enterprise:** Custom limits

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1704340200
```

---

## Testing

### Using cURL

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Extract from URL
curl -X POST http://localhost:8000/api/v1/extract \
  -H "Content-Type: application/json" \
  -d '{"document_url": "https://example.com/invoice.jpg"}'

# Batch processing
curl -X POST http://localhost:8000/api/v1/batch \
  -H "Content-Type: application/json" \
  -d '{"document_urls": ["https://example.com/doc1.jpg", "https://example.com/doc2.jpg"]}'
```

### Using Python

```python
import requests

API_URL = "http://localhost:8000/api/v1"

# Health check
response = requests.get(f"{API_URL}/health")
print(response.json())

# Extract
response = requests.post(
    f"{API_URL}/extract",
    json={"document_url": "https://example.com/invoice.jpg"}
)
print(response.json())
```

### Using JavaScript

```javascript
const API_URL = 'http://localhost:8000/api/v1';

// Health check
const response = await fetch(`${API_URL}/health`);
const data = await response.json();
console.log(data);

// Extract
const extractResponse = await fetch(`${API_URL}/extract`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({document_url: 'https://example.com/invoice.jpg'})
});
const extractData = await extractResponse.json();
console.log(extractData);
```

---

## Swagger Documentation

Interactive API documentation available at:

```
http://localhost:8000/docs
```

Alternative documentation:

```
http://localhost:8000/redoc
```
