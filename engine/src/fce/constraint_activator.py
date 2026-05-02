"""ConstraintActivator — activates constraints and produces action buckets."""

from typing import Any, Dict


class ConstraintActivator:
    """Activates constraints based on state and confidence score."""

    def activate(
        self,
        state: str,
        structured_metrics: Dict[str, Any],
        user_declared: Dict[str, Any],
        optional_external: Dict[str, Any],
        pack: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Returns action buckets and applied constraints.
        """
        constraints = pack.get("constraints", [])
        actions = pack.get("actions", [])
        confidence_score = pack.get("_confidence_score", 0.5)

        allowed_actions = []
        blocked_actions = []
        discouraged_actions = []
        priority_actions = []
        applied_constraints = []
        reasoning_parts = []
        flags = []

        for constraint in constraints:
            c_id = constraint.get("id", "unknown")
            condition = constraint.get("condition", "")
            action_type = constraint.get("action", "block")

            applied = {
                "id": c_id,
                "condition": condition,
                "action": action_type,
                "activated": True,
            }
            applied_constraints.append(applied)
            reasoning_parts.append(
                f"Constraint {c_id} ({action_type}) activated: {condition}"
            )

        for action in actions:
            action_id = action.get("id", "unknown")
            risk_level = action.get("risk_level", "medium")
            priority = action.get("priority", False)

            if risk_level == "critical":
                blocked_actions.append(action_id)
            elif risk_level == "high" and confidence_score < 0.7:
                blocked_actions.append(action_id)
            elif state == "unstable" and risk_level == "high":
                discouraged_actions.append(action_id)
            else:
                allowed_actions.append(action_id)

            if priority and action_id not in blocked_actions:
                priority_actions.append(action_id)

        blocked_set = set(blocked_actions)
        allowed_actions = [a for a in allowed_actions if a not in blocked_set]
        discouraged_actions = [a for a in discouraged_actions if a not in blocked_set]
        priority_actions = [a for a in priority_actions if a not in blocked_set]

        if state == "unstable":
            overlap = set(priority_actions) & set(blocked_actions)
            if overlap:
                flags.append(f"priority_blocked_overlap:{','.join(sorted(overlap))}")

        if not reasoning_parts:
            reasoning_parts.append("No constraints activated")

        return {
            "allowed_actions": allowed_actions,
            "blocked_actions": blocked_actions,
            "discouraged_actions": discouraged_actions,
            "priority_actions": priority_actions,
            "applied_constraints": applied_constraints,
            "reasoning": " | ".join(reasoning_parts),
            "flags": flags,
        }
