from fastapi import APIRouter, HTTPException
from app.schemas.evaluate import EvaluateInput
from app.dependencies.engine import get_engine

router = APIRouter()

# Map FCE error types to HTTP status codes
_ERROR_STATUS = {
    "validation_error": 422,
    "unsupported_domain_error": 404,
    "pack_validation_error": 422,
    "coherence_error": 500,
    "domain_hard_constraint_triggered": 409,
    "output_assembly_error": 500,
    "system_rule_violation": 500,
}


@router.post("/evaluate")
def evaluate(request: EvaluateInput):
    """Evaluate input_data against FCE engine and return decision space."""
    engine = get_engine()
    result = engine.evaluate(request.model_dump())

    if "error" in result:
        err = result["error"]
        status = _ERROR_STATUS.get(err["type"], 400)
        raise HTTPException(status_code=status, detail=err)

    return result
