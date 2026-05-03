from pydantic import BaseModel, Field
from typing import Dict, Any, Optional


class EvaluateInput(BaseModel):
    """Input schema for FCE evaluate endpoint -- matches engine.evaluate(input_data)."""

    domain: str = Field(..., description="Domain identifier (e.g. finance_v1)")
    structured_metrics: Dict[str, Any]
    user_declared: Dict[str, Any]
    optional_external: Dict[str, Any] = Field(default_factory=dict)
    domain_constraint_pack: Optional[Dict[str, Any]] = Field(default=None)
