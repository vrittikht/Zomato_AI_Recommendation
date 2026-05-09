# Phase 7 Implementation (Backend API)

This phase transitions the system into a live service using **FastAPI**.

## Implemented in `src/api/`

- `main.py`: Application lifecycle, environment loading, and CORS configuration.
- `routes.py`: Orchestrates the recommendation process (Phase 3 -> 4 -> 5).
- `models.py`: Pydantic schemas for data validation and OpenAPI documentation.

## Key Features

- **Standard REST API**: Exposes a `POST /api/v1/recommend` endpoint.
- **Auto-Documentation**: Provides Swagger UI at `/docs`.
- **Pre-Integrated Logic**: Reuses verified services from previous phases.
- **Validation**: Automatic request validation using Pydantic.

## How to Run

```bash
python scripts/run_phase7.py
```

The API will be available at `http://localhost:8000`.

## Testing the API

### Sample Request (JSON)
URL: `POST http://localhost:8000/api/v1/recommend`

Payload:
```json
{
  "location": "Indiranagar",
  "budget": "high",
  "cuisine": "Italian",
  "rating": "4.0",
  "top_k": 3
}
```
