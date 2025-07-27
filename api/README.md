# Campaign Performance API v2.0 - Authenticated

A FastAPI-based REST API for campaign performance data with **authentication** and **rate limiting**.

## 🔐 Authentication

This API uses **Bearer token authentication** with API keys.

### API Keys

**Test API Key**: `sk-test-1234567890abcdef`
- Rate Limit: 100 requests/minute
- Purpose: Development and testing

**Production API Key**: `sk-prod-abcdef1234567890`
- Rate Limit: 1000 requests/minute
- Purpose: Production applications

### Environment Variables

Add API keys to your `.env` file:
```bash
API_KEYS=sk-your-key-1,sk-your-key-2,sk-your-key-3
```

## 🚀 Features

- **🔐 Bearer Token Authentication**: Secure API key validation
- **⚡ Rate Limiting**: Per-endpoint and per-API-key limits
- **📊 Comprehensive Logging**: Track API usage and errors
- **🛡️ Error Handling**: Proper HTTP status codes and messages
- **📚 Auto Documentation**: Interactive Swagger UI
- **🔍 Request Validation**: Pydantic models for type safety

## 📋 Rate Limits

| Endpoint | Rate Limit | Description |
|----------|------------|-------------|
| `/` | 30/minute | API information |
| `/auth/verify` | No limit | Authentication verification |
| `/campaigns/summary` | 60/minute | Summary statistics |
| `/campaigns/{id}` | 100/minute | Campaign details |
| `/campaigns/top/{metric}` | 50/minute | Top campaigns |
| `/campaigns/topic/{topic}` | 40/minute | Campaigns by topic |
| `/campaigns/segment/{segment}` | 40/minute | Campaigns by segment |
| `/campaigns/compare/{id1}/{id2}` | 30/minute | Campaign comparison |

## 🛠️ Installation

1. **Install dependencies**:
   ```bash
   uv pip install -r requirements.txt
   ```

2. **Set up database** (if not already done):
   ```bash
   cd database
   python database_setup.py
   ```

3. **Configure API keys** (optional):
   ```bash
   # Add to .env file
   API_KEYS=sk-your-custom-key-1,sk-your-custom-key-2
   ```

## 🚀 Running the API

### Development Mode
```bash
cd api
python main_with_auth.py
```

### Production Mode
```bash
cd api
uvicorn main_with_auth:app --host 0.0.0.0 --port 8000
```

## 📖 API Usage Examples

### Authentication

All requests (except `/` and `/auth/verify`) require authentication:

```bash
# Add Authorization header to all requests
curl -H "Authorization: Bearer sk-test-1234567890abcdef" \
     http://localhost:8000/campaigns/summary
```

### Verify Authentication
```bash
curl -H "Authorization: Bearer sk-test-1234567890abcdef" \
     http://localhost:8000/auth/verify
```

### Get Campaign Details
```bash
curl -H "Authorization: Bearer sk-test-1234567890abcdef" \
     http://localhost:8000/campaigns/100
```

### Get Top Campaigns
```bash
curl -H "Authorization: Bearer sk-test-1234567890abcdef" \
     "http://localhost:8000/campaigns/top/conversion_rate?limit=5"
```

### Get Summary Statistics
```bash
curl -H "Authorization: Bearer sk-test-1234567890abcdef" \
     http://localhost:8000/campaigns/summary
```

## 🧪 Testing

### Test Authentication
```bash
cd api
python test_auth_api.py
```

### Test Rate Limiting
```bash
# Make multiple rapid requests to see rate limiting in action
for i in {1..10}; do
  curl -H "Authorization: Bearer sk-test-1234567890abcdef" \
       http://localhost:8000/campaigns/summary
  echo "Request $i completed"
done
```

## 🔧 Configuration

### API Key Management

**In Production:**
- Store API keys in a secure database
- Use environment variables for sensitive data
- Implement key rotation and expiration
- Add key usage analytics

**Current Implementation:**
- API keys stored in memory (for demo)
- Environment variable support
- Basic validation and logging

### Rate Limiting

**Per-Endpoint Limits:**
- Configured in the `@limiter.limit()` decorator
- Different limits for different endpoints
- Based on request frequency

**Per-API-Key Limits:**
- Different rate limits per API key
- Production keys have higher limits
- Easy to customize per client

## 📝 Logging

Logs are written to:
- **File**: `logs/api.log`
- **Rotation**: Weekly
- **Retention**: 4 weeks
- **Level**: INFO

**Logged Events:**
- API key usage and validation
- Rate limit violations
- Database errors
- Request processing

## 🔒 Security Features

### Authentication
- Bearer token validation
- API key verification
- Inactive key rejection
- Secure error messages

### Rate Limiting
- Per-endpoint limits
- Per-API-key limits
- Configurable thresholds
- Graceful degradation

### Error Handling
- Proper HTTP status codes
- Secure error messages
- No sensitive data exposure
- Comprehensive logging

## 🌐 Integration

### With LLM Tools
The `llm_tools.py` has been updated to use the authenticated API:

```python
# API Key for authentication
API_KEY = "sk-test-1234567890abcdef"

# All requests include Authorization header
headers = {"Authorization": f"Bearer {API_KEY}"}
response = requests.get(url, headers=headers)
```

### With Other Applications
```python
import requests

API_KEY = "sk-test-1234567890abcdef"
BASE_URL = "http://localhost:8000"

headers = {"Authorization": f"Bearer {API_KEY}"}

# Get campaign summary
response = requests.get(f"{BASE_URL}/campaigns/summary", headers=headers)
if response.status_code == 200:
    data = response.json()
    print(f"Total campaigns: {data['total_campaigns']}")
```

## 🔄 Migration from v1.0

### Changes Required:
1. **Add Authorization headers** to all requests
2. **Handle 401 errors** for authentication failures
3. **Handle 429 errors** for rate limit violations
4. **Update API key management** in your applications

### Backward Compatibility:
- v1.0 endpoints still available at `/v1/` (if needed)
- Same data models and response formats
- Enhanced security and rate limiting

## 🚀 Next Steps

### Production Deployment
1. **Database Storage**: Move API keys to database
2. **Key Management**: Implement key creation/rotation
3. **Monitoring**: Add usage analytics and alerts
4. **SSL/TLS**: Enable HTTPS
5. **Load Balancing**: Scale across multiple instances

### Advanced Features
1. **JWT Tokens**: Replace API keys with JWT
2. **OAuth2**: Add OAuth2 authentication
3. **Webhooks**: Real-time data updates
4. **Caching**: Redis-based response caching
5. **GraphQL**: Add GraphQL endpoint

## 📚 Documentation

- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

## 🆘 Troubleshooting

### Common Issues

**401 Unauthorized:**
- Check API key format: `Bearer sk-...`
- Verify API key is valid and active
- Ensure Authorization header is present

**429 Too Many Requests:**
- Reduce request frequency
- Use higher-tier API key
- Implement exponential backoff

**500 Internal Server Error:**
- Check database connection
- Verify database schema
- Review server logs

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python main_with_auth.py
``` 