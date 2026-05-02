"""PackValidator — validates constraint packs."""

import datetime
from typing import Any, Dict


class PackValidator:
    """Validates pack data and returns structured result."""

    def validate(self, pack_data: Any) -> Dict[str, Any]:
        if not isinstance(pack_data, dict):
            return {"valid": False, "message": "pack_data must be a dict", "field": None}

        required_fields = {
            "pack_id": str,
            "domain": str,
            "constraints": list,
            "actions": list,
        }

        for field, expected_type in required_fields.items():
            if field not in pack_data:
                return {"valid": False, "message": f"Missing required field: '{field}'", "field": field}
            if not isinstance(pack_data[field], expected_type):
                return {"valid": False, "message": f"Field '{field}' must be of type {expected_type.__name__}", "field": field}

        validated = dict(pack_data)
        validated["_validated"] = True
        validated["_validation_version"] = "1.0"
        validated["validated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

        return {"valid": True, "data": validated}
