"""ConstraintActivator -- activates constraints with rich reasoning and safe priority."""

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
        Safe priority: subset without ranking, never implicit single selection.
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

        # Detect hard constraints
        hard_triggered = False

        for constraint in constraints:
            c_id = constraint.get("id", "unknown")
            condition = constraint.get("condition", "")
            action_type = constraint.get("action", "block")
            is_hard = constraint.get("hard", False)

            if is_hard:
                hard_triggered = True

            applied = {
                "id": c_id,
                "condition": condition,
                "action": action_type,
                "hard": is_hard,
                "activated": True,
            }
            applied_constraints.append(applied)

            # Rich reasoning: explain WHY, not just WHAT
            reason = (
                f"Constraint {c_id} ({action_type}) triggered because '{condition}' "
                f"evaluates true under state={state}, confidence={confidence_score:.2f}"
            )
            if is_hard:
                reason += " [HARD]"
            reasoning_parts.append(reason)

        # Classify actions into buckets
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

            # Safe priority: only explicit priority flag, no ranking
            if priority and action_id not in blocked_actions:
                priority_actions.append(action_id)

        # Deduplicate and ensure disjointness
        blocked_set = set(blocked_actions)
        allowed_actions = [a for a in allowed_actions if a not in blocked_set]
        discouraged_actions = [a for a in discouraged_actions if a not in blocked_set]
        priority_actions = [a for a in priority_actions if a not in blocked_set]

        # Guard: single priority action is flagged to avoid implicit selection
        if len(priority_actions) == 1:
            flags.append("SINGLE_PRIORITY_ACTION")

        if state == "unstable":
            overlap = set(priority_actions) & set(blocked_actions)
            if overlap:
                flags.append(f"PRIORITY_BLOCKED_OVERLAP:{','.join(sorted(overlap))}")

        # Global reasoning summary
        domain = pack.get("domain", "unknown")
        global_reasoning = (
            f"Domain '{domain}' evaluated as {state} (confidence={confidence_score:.2f}). "
            f"Allowed={len(allowed_actions)}, Blocked={len(blocked_actions)}, "
            f"Discouraged={len(discouraged_actions)}, Priority={len(priority_actions)}."
        )
        reasoning_parts.insert(0, global_reasoning)

        if not reasoning_parts:
            reasoning_parts.append("No constraints activated")

        if hard_triggered:
            flags.append("HARD_CONSTRAINT_TRIGGERED")

        return {
            "allowed_actions": allowed_actions,
            "blocked_actions": blocked_actions,
            "discouraged_actions": discouraged_actions,
            "priority_actions": priority_actions,
            "applied_constraints": applied_constraints,
            "reasoning": " | ".join(reasoning_parts),
            "flags": flags,
        }
