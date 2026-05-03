import re
from typing import Any, Dict, Tuple


class ConstraintActivator:
    def activate(self, state, structured_metrics, user_declared, optional_external, pack):
        constraints = pack.get("constraints", [])
        actions = pack.get("actions", [])
        confidence_score = pack.get("_confidence_score", 0.5)
        allowed_actions, blocked_actions, discouraged_actions, priority_bucket = [], [], [], []
        evaluated_constraints, reasoning_parts, flags = [], [], []
        context = {**structured_metrics, **user_declared, **optional_external}
        hard_triggered = False

        for constraint in constraints:
            c_id = constraint.get("id", "unknown")
            condition = constraint.get("condition", "")
            action_type = constraint.get("action", "block")
            is_hard = constraint.get("hard", False)
            condition_met, error = self._evaluate_condition(condition, context)
            evaluated_constraints.append({"id": c_id, "condition": condition, "action": action_type, "hard": is_hard, "activated": condition_met})

            if condition_met:
                if is_hard: hard_triggered = True
                reasoning_parts.append(f"Constraint {c_id} ACTIVATED: '{condition}' is TRUE")
            else:
                if error == "DATA_GAP": flags.append("DATA_GAP")
                reasoning_parts.append(f"Constraint {c_id} NOT activated: '{condition}' is FALSE or metric missing")

        for action in actions:
            action_id = action.get("id", "unknown")
            risk_level = action.get("risk_level", "medium")
            priority = action.get("priority", False)
            if risk_level == "critical": blocked_actions.append(action_id)
            elif risk_level == "high" and confidence_score < 0.7: blocked_actions.append(action_id)
            elif state == "unstable" and risk_level == "high": discouraged_actions.append(action_id)
            else: allowed_actions.append(action_id)
            if priority and action_id not in blocked_actions: priority_bucket.append(action_id)

        blocked_set = set(blocked_actions)
        allowed_actions = [a for a in allowed_actions if a not in blocked_set]
        priority_bucket = [a for a in priority_bucket if a not in blocked_set]
        if hard_triggered: flags.append("HARD_CONSTRAINT_TRIGGERED")

        activated_count = sum(1 for c in evaluated_constraints if c["activated"])
        reasoning_parts.insert(0, f"Domain '{pack.get('domain', 'unknown')}' state={state} confidence={confidence_score:.2f}. Activated={activated_count}/{len(evaluated_constraints)}")

        return {"allowed_actions": allowed_actions, "blocked_actions": blocked_actions, "discouraged_actions": discouraged_actions, "priority_bucket": priority_bucket, "evaluated_constraints": evaluated_constraints, "reasoning": " | ".join(reasoning_parts), "flags": flags}

    def _evaluate_condition(self, condition, context):
        if not condition or not isinstance(condition, str): return False, "MALFORMED"
        cl = condition.strip().lower()
        if cl in ("true", "1", "yes"): return True, None
        if cl in ("false", "0", "no"): return False, None
        match = re.match(r"^\s*(\w+)\s*([><=!]+)\s*([0-9.]+)\s*$", condition)
        if not match: return False, "UNKNOWN_OPERATOR"
        field, operator, threshold_str = match.groups()
        if field not in context: return False, "DATA_GAP"
        try:
            threshold = float(threshold_str)
            value = float(context[field])
        except (ValueError, TypeError): return False, "MALFORMED"
        if operator == ">": return value > threshold, None
        elif operator == "<": return value < threshold, None
        elif operator == ">=": return value >= threshold, None
        elif operator == "<=": return value <= threshold, None
        elif operator == "==": return value == threshold, None
        return False, "UNKNOWN_OPERATOR"