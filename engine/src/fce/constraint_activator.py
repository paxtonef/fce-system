"""ConstraintActivator module for FCE."""


class ConstraintActivator:
    """Activates constraints based on confidence score."""

    def activate(self, pack_data: dict, confidence_score: float) -> list[dict]:
        """Retourne la liste des contraintes appliquées."""
        constraints = pack_data.get("constraints", [])
        activated = []

        for constraint in constraints:
            # Logique d'activation basique
            activated_constraint = {
                "id": constraint.get("id", "unknown"),
                "condition": constraint.get("condition", ""),
                "action": constraint.get("action", "block"),
                "activated": True,
                "confidence_threshold": confidence_score,
            }
            activated.append(activated_constraint)

        return activated
