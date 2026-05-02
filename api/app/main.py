"""FCE API — FastAPI adapter for the Freedom Constraint Engine."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.evaluate import router as evaluate_router
from app.routes.packs import router as packs_router

app = FastAPI(
    title="Freedom Constraint Engine API",
    description="REST adapter for the FCE Python library.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(evaluate_router)
app.include_router(packs_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "fce-api", "version": "1.0.0"}
