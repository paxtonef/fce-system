"""PackValidator module for FCE."""
import datetime


class PackValidator:
    """Validates pack data."""

    def validate(self, pack_data: dict) -> dict:
        """
        Champs obligatoires : pack_id (str), domain (str),
                              constraints (list), actions (list)
        Raise ValueError avec le nom du champ manquant si invalide.
        Retourne pack_data enrichi (+ validated_at) si valide.
        """
        if not isinstance(pack_data, dict):
            raise ValueError("pack_data must be a dict")

        required_fields = {
            "pack_id": str,
            "domain": str,
            "constraints": list,
            "actions": list,
        }

        for field, expected_type in required_fields.items():
            if field not in pack_data:
                raise ValueError(f"Missing required field: '{field}'")
            if not isinstance(pack_data[field], expected_type):
                raise ValueError(
                    f"Field '{field}' must be of type {expected_type.__name__}"
                )

        validated = dict(pack_data)
        validated["_validated"] = True
        validated["_validation_version"] = "1.0"
        validated["validated_at"] = datetime.datetime.utcnow().isoformat() + "Z"

        return validated
