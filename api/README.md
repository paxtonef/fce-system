# fce-api — REST API Adapter
**layer**: api | **version**: 1.0.0

> Transport layer only. No business logic. Wraps the FCE engine via HTTP.

## Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/health` | Health check |
| GET | `/packs` | List available packs |
| POST | `/evaluate` | Evaluate constraints |

## Quick start

```bash
git clone https://github.com/paxtonef/fce-api
cd fce-api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Point to local engine
export FCE_ENGINE_PATH=../spec-fce-001-cards/src

uvicorn app.main:app --reload --port 8000
```

## Test

```bash
# Health
curl http://127.0.0.1:8000/health

# Packs
curl http://127.0.0.1:8000/packs

# Evaluate
curl -s -X POST http://127.0.0.1:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "finance_v1",
    "structured_metrics": {"cash_months": 0.5, "debt_ratio": 0.4},
    "user_declared": {"stress_level": 8}
  }' | python -m json.tool
```

## API docs

```
http://127.0.0.1:8000/docs
```

## Dependencies

- [spec-fce-001-cards](https://github.com/paxtonef/spec-fce-001-cards) — FCE engine
- FastAPI + Uvicorn + Pydantic
