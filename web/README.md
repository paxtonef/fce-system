# fce-web — React Web Interface
**layer**: web | **version**: 0.1.0

> Interface only. Calls fce-api. No engine logic.

## Quick start

```bash
git clone https://github.com/paxtonef/fce-web
cd fce-web
npm install
npm run dev
```

Open: `http://localhost:5173`

> **Requires fce-api running on :8000**

## Features

- Domain selector (finance_v1, health_v1, career_v1)
- Confidence score display
- Allowed / blocked actions summary
- Full JSON result

## Dependencies

- [fce-api](https://github.com/paxtonef/fce-api) — REST API
- React 18 + Vite

## Full system startup

```bash
# Terminal 1 — API
cd fce-api
source .venv/bin/activate
export FCE_ENGINE_PATH=../spec-fce-001-cards/src
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Web
cd fce-web
npm run dev
```
