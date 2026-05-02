"""GET /packs — list available constraint packs."""
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/packs")
def list_packs():
    """Return the list of available built-in constraint packs."""
    try:
        import sys, os
        engine_src = os.environ.get(
            "FCE_ENGINE_PATH",
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "spec-fce-001-cards", "src")
        )
        if engine_src not in sys.path:
            sys.path.insert(0, engine_src)

        from fce.registry import BuiltinPackRegistry
        registry = BuiltinPackRegistry()
        return {"packs": registry.AVAILABLE_PACKS}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
