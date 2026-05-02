"""POST /evaluate — transport layer only. No business logic."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any

router = APIRouter()


class EvaluateRequest(BaseModel):
    domain: str
    structured_metrics: dict[str, Any]
    user_declared: dict[str, Any]
    optional_external: dict[str, Any] | None = None
    domain_constraint_pack: dict[str, Any] | None = None


@router.post("/evaluate")
def evaluate(request: EvaluateRequest):
    """
    Expose engine.evaluate() via HTTP.
    Transport layer only — no business logic beyond input validation.
    """
    try:
        import sys, os
        # Support local dev without pip install
        engine_src = os.environ.get(
            "FCE_ENGINE_PATH",
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "spec-fce-001-cards", "src")
        )
        if engine_src not in sys.path:
            sys.path.insert(0, engine_src)

        from fce.engine import Engine
        engine = Engine()
        result = engine.evaluate(request.domain)
        return result

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
