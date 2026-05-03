"""OutputAssembler — assembles final output conforming to SPEC-FCE-001."""

from datetime import datetime, timezone
from typing import Any, Dict, List


class OutputAssembler:
    """Assembles final output with full schema validation."""

    def assemble(self, raw_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        raw_output must contain all required keys.
        Returns validated and enriched output dict.
        """
        required_keys = [
            "state",
            "confidence_score",
            "allowed_actions",
            "blocked_actions",
            "discouraged_actions",
            "priority_bucket",
            "evaluated_constraints",
            "reasoning",
            "flags",
        ]

        for key in required_keys:
            if key not in raw_output:
                raise ValueError(f"Missing required output key: '{key}'")

        for list_key in ("allowed_actions", "blocked_actions", "discouraged_actions",
                         "priority_bucket", "evaluated_constraints", "flags"):
            if not isinstance(raw_output[list_key], list):
                raw_output[list_key] = list(raw_output[list_key])

        if not isinstance(raw_output["reasoning"], str):
            raw_output["reasoning"] = str(raw_output["reasoning"])

        self.check_mutual_exclusion(
            raw_output["blocked_actions"],
            raw_output["allowed_actions"],
        )

        self.assert_completeness(raw_output)

        raw_output["metadata"] = {
            "domain": raw_output.get("_domain", "unknown"),
            "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        }

        raw_output.pop("_domain", None)
        raw_output.pop("_confidence_score", None)

        return raw_output

    def check_mutual_exclusion(
        self, blocked_actions: List[str], allowed_actions: List[str]
    ) -> bool:
        intersection = set(blocked_actions) & set(allowed_actions)
        if intersection:
            raise ValueError(
                f"Mutual exclusion violated: actions {sorted(intersection)} "
                f"are in both blocked_actions and allowed_actions"
            )
        return True

    def assert_completeness(self, output: Dict[str, Any]) -> None:
        applied = output.get("evaluated_constraints")
        reasoning = output.get("reasoning")

        if not applied:
            raise ValueError("output['evaluated_constraints'] is empty or None")

        if not reasoning:
            raise ValueError("output['reasoning'] is empty or None")
