"""OutputAssembler module for FCE."""


class OutputAssembler:
    """Assembles final output from pack data and constraints."""

    def check_mutual_exclusion(self, blocked_actions: list[str], allowed_actions: list[str]) -> bool:
        """
        Vérifie que blocked_actions et allowed_actions sont disjoints.
        Retourne True si disjoints.
        Lève ValueError avec message explicite si intersection non vide.
        """
        blocked_set = set(blocked_actions)
        allowed_set = set(allowed_actions)
        intersection = blocked_set & allowed_set

        if intersection:
            raise ValueError(
                f"Mutual exclusion violated: actions {sorted(intersection)} "
                f"are in both blocked_actions and allowed_actions"
            )

        return True

    def assert_completeness(self, output: dict) -> None:
        """
        Vérifie que output['applied_constraints'] et output['reasoning']
        sont non-None et non-vides.
        Lève ValueError avec message explicite sinon.
        """
        applied_constraints = output.get("applied_constraints")
        reasoning = output.get("reasoning")

        if applied_constraints is None:
            raise ValueError("output['applied_constraints'] is None")

        if len(applied_constraints) == 0:
            raise ValueError("output['applied_constraints'] is empty")

        if reasoning is None:
            raise ValueError("output['reasoning'] is None")

        if len(reasoning) == 0:
            raise ValueError("output['reasoning'] is empty")

    def assemble(self, pack_data: dict, constraints: list[dict], score: float) -> dict:
        """
        Retourne obligatoirement :
        {
            "applied_constraints": [...],
            "reasoning": [...],
            "blocked_actions": [...],
            "allowed_actions": [...],
            "confidence_score": float
        }
        Appelle check_mutual_exclusion() avant de retourner.
        """
        actions = pack_data.get("actions", [])

        # Classification des actions en blocked/allowed
        blocked_actions = []
        allowed_actions = []

        for action in actions:
            action_id = action.get("id", "unknown")
            risk_level = action.get("risk_level", "medium")

            # Actions à haut risque sont bloquées si score < 0.7
            if risk_level == "high" and score < 0.7:
                blocked_actions.append(action_id)
            elif risk_level == "critical":
                blocked_actions.append(action_id)
            else:
                allowed_actions.append(action_id)

        # Garantir disjointure par filtrage
        blocked_set = set(blocked_actions)
        allowed_actions = [a for a in allowed_actions if a not in blocked_set]

        # Construction du reasoning
        reasoning = []
        for constraint in constraints:
            reasoning.append({
                "constraint_id": constraint.get("id"),
                "reason": f"Constraint {constraint.get('id')} activated with confidence {score:.4f}",
            })

        # Vérifier exclusion mutuelle avant retour
        self.check_mutual_exclusion(blocked_actions, allowed_actions)

        output = {
            "applied_constraints": constraints,
            "reasoning": reasoning if reasoning else [{"reason": "No constraints to apply"}],
            "blocked_actions": blocked_actions,
            "allowed_actions": allowed_actions,
            "confidence_score": float(score),
        }

        # Vérifier complétude avant retour
        self.assert_completeness(output)

        return output
