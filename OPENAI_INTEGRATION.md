# OpenAI Integration Guide

## Overview

The GPT-5.6 Multimodal API integrates OpenAI's powerful models for advanced AI capabilities:

- **GPT-4 Turbo** - Multimodal analysis, chat, reasoning
- **GPT-4 Vision** - Document analysis, image understanding
- **Whisper** - Audio transcription

---

## Supported Models

| Model | Capabilities | Use Case |
|-------|--------------|----------|
| `gpt-4-turbo` | Text, image input | Chat, analysis, reasoning |
| `gpt-4-vision` | Image analysis | Document extraction, vision tasks |
| `gpt-3.5-turbo` | Text input | Fast, cost-effective responses |
| `whisper-1` | Audio input | Speech-to-text transcription |

---

## Setup

### 1. Get OpenAI API Key

1. Visit [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key (you won't see it again)

### 2. Configure Environment

```bash
# In .env file
OPENAI_API_KEY=sk-...
MODEL_NAME=gpt-4-turbo
```

### 3. Store Securely in Azure

```bash
# Option 1: Azure Key Vault
az keyvault secret set \
  --vault-name {KEYVAULT_NAME} \
  --name openai-api-key \
  --value {YOUR_API_KEY}

# Option 2: App Service Environment Variables
az webapp config appsettings set \
  --resource-group {RG_NAME} \
  --name {APP_NAME} \
  --settings OPENAI_API_KEY={YOUR_API_KEY}
```

---

## API Endpoints

### 1. Multimodal Analysis

**POST** `/api/v1/analyze`

Analyze content combining text, images, and audio.

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Analyze this content",
    "image_url": "https://example.com/image.jpg",
    "audio_url": "https://example.com/audio.mp3",
    "task": "sentiment"
  }'
```

**Response:**
```json
{
  "id": "req-123",
  "analysis": "The sentiment analysis shows...",
  "confidence": 0.95,
  "task": "sentiment",
  "timestamp": "2024-01-22T10:30:00Z"
}
```

---

### 2. Document Extraction

**POST** `/api/v1/extract`

Extract structured transaction data from documents using Vision.

```bash
curl -X POST http://localhost:8000/api/v1/extract \
  -H "Content-Type: application/json" \
  -d '{
    "document_url": "https://example.com/invoice.jpg",
    "document_id": "INV-2024-001",
    "save_to_storage": true
  }'
```

**Response:**
```json
{
  "document_id": "INV-2024-001",
  "transaction": {
    "type": "invoice",
    "dates": {
      "received": "2024-01-15",
      "paid": "2024-01-20"
    },
    "amount": 1500.50,
    "payee": {
      "name": "Acme Corporation",
      "address": "123 Business Ave, New York, NY"
    },
    "signature": "J. Smith"
  },
  "confidence": 0.95,
  "storage_path": "transactions/2024/01/22/INV-2024-001.json"
}
```

---

### 3. Batch Processing

**POST** `/api/v1/batch`

Process multiple documents in one request.

```bash
curl -X POST http://localhost:8000/api/v1/batch \
  -H "Content-Type: application/json" \
  -d '{
    "document_urls": [
      "https://example.com/invoice1.jpg",
      "https://example.com/invoice2.jpg",
      "https://example.com/invoice3.jpg"
    ],
    "batch_id": "BATCH-2024-001",
    "save_to_storage": true
  }'
```

**Response:**
```json
{
  "batch_id": "BATCH-2024-001",
  "total_documents": 3,
  "successful": 3,
  "failed": 0,
  "transactions": [/* ... */],
  "storage_path": "batch-results/2024/01/22/batch-BATCH-2024-001.json"
}
```

---

### 4. Audio Transcription

**POST** `/api/v1/transcribe`

Transcribe audio using Whisper API.

```bash
curl -X POST http://localhost:8000/api/v1/transcribe \
  -H "Content-Type: application/json" \
  -d '{
    "audio_url": "https://example.com/audio.mp3",
    "language": "en"
  }'
```

**Response:**
```json
{
  "id": "req-456",
  "transcription": "The transcribed text from the audio...",
  "language": "en",
  "duration": 45.5,
  "timestamp": "2024-01-22T10:35:00Z"
}
```

---

### 5. Chat with Context

**POST** `/api/v1/chat`

Chat with GPT-4 including image context.

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "What is in this image?",
        "image_url": "https://example.com/image.jpg"
      }
    ],
    "system_prompt": "You are a helpful assistant.",
    "stream": false
  }'
```

**Response:**
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

## Transaction Schema

The API extracts transactions into this schema:

```json
{
  "type": "invoice|receipt|check|payment|transfer|wire|other",
  "dates": {
    "received": "YYYY-MM-DD or null",
    "paid": "YYYY-MM-DD or null"
  },
  "amount": 0.00,
  "payee": {
    "name": "string",
    "address": "string or null"
  },
  "signature": "string or null"
}
```

---

## Model-Specific Configurations

### GPT-4 Vision (Document Processing)

```python
openai.ChatCompletion.create(
    model="gpt-4-vision",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Extract transaction data"},
            {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
        ]
    }],
    temperature=0.2,      # Low temp for consistent extraction
    max_tokens=500
)
```

### GPT-4 Turbo (Chat & Analysis)

```python
openai.ChatCompletion.create(
    model="gpt-4-turbo",
    messages=[{"role": "user", "content": "Your prompt"}],
    temperature=0.7,      # Balanced for creative responses
    max_tokens=2048
)
```

### Whisper (Audio Transcription)

```python
openai.Audio.transcribe(
    model="whisper-1",
    file=audio_file,
    language="en"
)
```

---

## Rate Limiting & Costs

### Free Trial
- $5 free credits
- Expires after 3 months

### Paid Plans

| Model | Cost (per 1K tokens) |
|-------|----------------------|
| GPT-4 Turbo Input | $0.01 |
| GPT-4 Turbo Output | $0.03 |
| GPT-4 Vision | $0.01-0.03 |
| Whisper | $0.02 per minute |

### Rate Limits (Free Tier)
- 3 requests per minute
- 200 requests per day

### Rate Limits (Paid Tier)
- 3,500 requests per minute (default)
- Can be increased by contacting OpenAI

---

## Error Handling

### Common Errors

**Invalid API Key**
```json
{
  "error": {
    "message": "Incorrect API key provided",
    "type": "invalid_request_error"
  }
}
```

**Rate Limited**
```json
{
  "error": {
    "message": "Rate limit exceeded",
    "type": "server_error"
  }
}
```

**Insufficient Quota**
```json
{
  "error": {
    "message": "You exceeded your current quota",
    "type": "server_error"
  }
}
```

### Retry Strategy

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def call_openai_api():
    # Your API call here
    pass
```

---

## Best Practices

### 1. Security
- ✅ Store API keys in Azure Key Vault
- ✅ Never commit API keys to Git
- ✅ Use separate keys for dev/prod
- ✅ Rotate keys regularly

### 2. Performance
- ✅ Use lower temperature (0.2-0.3) for extraction tasks
- ✅ Use higher temperature (0.7-0.9) for creative tasks
- ✅ Set appropriate max_tokens to control costs
- ✅ Cache results for repeated queries

### 3. Cost Optimization
- ✅ Use GPT-3.5-turbo for simple tasks
- ✅ Batch requests when possible
- ✅ Monitor token usage via dashboard
- ✅ Set budget alerts in OpenAI account

### 4. Reliability
- ✅ Implement exponential backoff for retries
- ✅ Set request timeouts
- ✅ Log all API calls
- ✅ Monitor error rates

---

## Monitoring

### Track Usage

```bash
# View in OpenAI Dashboard
https://platform.openai.com/account/usage/overview

# Monitor in Azure
az monitor metrics list --resource {RESOURCE_ID}
```

### Alert on High Usage

```bash
# Set budget alert in OpenAI
# Settings → Billing → Usage Limits
```

---

## Troubleshooting

### Issue: "Invalid JSON in extraction response"

**Solution:** Document quality is poor. Try:
- Higher resolution images (300+ DPI)
- Well-lit, straight-on photos
- Clear, legible text

### Issue: "Rate limit exceeded"

**Solution:** Implement backoff strategy
```python
import time
for attempt in range(3):
    try:
        response = openai.ChatCompletion.create(...)
        break
    except RateLimitError:
        wait_time = 2 ** attempt
        time.sleep(wait_time)
```

### Issue: "Timeout"

**Solution:** Increase timeout in config
```bash
REQUEST_TIMEOUT=120  # seconds
```

---

## Example Applications

### Invoice Processing Pipeline

```python
# 1. Upload invoice
response = await client.extract_from_url(
    document_url="s3://bucket/invoice.pdf"
)

# 2. Extract structured data
transaction = response.transaction

# 3. Store in database
await db.transactions.insert(transaction.dict())

# 4. Generate report
report = await generate_accounting_report([transaction])
```

### Multi-Document Analysis

```python
# Process batch of documents
response = await client.batch_extract(
    document_urls=invoice_list,
    save_to_storage=True
)

# Analyze results
print(f"Processed: {response.successful}/{response.total_documents}")
for tx in response.transactions:
    print(f"{tx.transaction.payee.name}: ${tx.transaction.amount}")
```

---

## Support & Resources

- **OpenAI Docs:** https://platform.openai.com/docs
- **API Reference:** https://platform.openai.com/docs/api-reference
- **Community:** https://community.openai.com
- **Status:** https://status.openai.com

---

## Next Steps

1. ✅ Get OpenAI API key
2. ✅ Configure environment
3. ✅ Test endpoints locally
4. ✅ Deploy to Azure
5. ✅ Set up monitoring
6. ✅ Configure alerts

**Ready to integrate?** Start with the [Quick Start](#setup) section above!
