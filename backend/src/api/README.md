# GramSaarthi AI API

FastAPI-based REST API for the GramSaarthi AI platform.

## Features

- Enterprise profile management (CRUD operations)
- Request/response validation with Pydantic
- CORS support for web applications
- Standardized error handling
- OpenAPI documentation

## Running the API

### Development Server

```bash
# From project root
python run_api.py
```

Or using uvicorn directly:

```bash
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

### Access Documentation

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- OpenAPI JSON: http://localhost:8000/api/openapi.json

## API Endpoints

### Health Check

- `GET /health` - Basic health check
- `GET /api/v1/health` - API health check with version info

### Enterprise Profile Management

- `POST /api/v1/enterprises` - Register new enterprise
- `GET /api/v1/enterprises/{enterprise_id}` - Get enterprise profile
- `PUT /api/v1/enterprises/{enterprise_id}` - Update enterprise profile
- `DELETE /api/v1/enterprises/{enterprise_id}` - Delete enterprise profile

## Request Examples

### Create Enterprise

```bash
curl -X POST "http://localhost:8000/api/v1/enterprises" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "SHG",
    "name": "Women Farmers Collective",
    "products": ["tomato", "onion"],
    "location": {
      "state": "Karnataka",
      "district": "Bangalore Rural",
      "block": "Devanahalli",
      "village": "Sadahalli",
      "coordinates": {
        "lat": 13.2443,
        "lon": 77.7074
      }
    },
    "contact": {
      "phone": "+919876543210",
      "preferred_language": "hi"
    }
  }'
```

### Get Enterprise

```bash
curl -X GET "http://localhost:8000/api/v1/enterprises/{enterprise_id}"
```

### Update Enterprise

```bash
curl -X PUT "http://localhost:8000/api/v1/enterprises/{enterprise_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Enterprise Name",
    "products": ["tomato", "onion", "potato"]
  }'
```

### Delete Enterprise

```bash
curl -X DELETE "http://localhost:8000/api/v1/enterprises/{enterprise_id}"
```

## Error Handling

All errors follow a standardized format:

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {},
  "request_id": "uuid",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Error Codes

- `VALIDATION_ERROR` - Invalid request data (400)
- `NOT_FOUND` - Resource not found (404)
- `VERSION_CONFLICT` - Concurrent update conflict (409)
- `SERVICE_ERROR` - Service operation failed (500)
- `INTERNAL_ERROR` - Unexpected error (500)

## CORS Configuration

The API is configured to allow requests from:
- `http://localhost:3000` (React dev server)
- `http://localhost:5173` (Vite dev server)
- `http://localhost:8000` (Local API testing)
- All origins (`*`) for hackathon demo

## Environment Variables

The API uses the following environment variables (configured in `.env`):

- `AWS_REGION` - AWS region for DynamoDB
- `AWS_ACCESS_KEY_ID` - AWS access key (optional for local development)
- `AWS_SECRET_ACCESS_KEY` - AWS secret key (optional for local development)
- `DYNAMODB_ENDPOINT_URL` - DynamoDB endpoint (for local testing)

## Testing

Run API tests:

```bash
# Run all tests
pytest tests/

# Run API-specific tests
pytest tests/unit/api/

# Run with coverage
pytest --cov=src/api tests/
```
