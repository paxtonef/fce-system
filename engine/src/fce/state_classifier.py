"""StateClassifier -- classifies domain state with pack-driven thresholds."""

from typing import Any, Dict


class StateClassifier:
    """Classifies pack state with deterministic confidence and pack-driven thresholds."""

    def compute_confidence(self, raw_score: float) -> float:
        """Clamp raw_score dans [0.0, 1.0]."""
        return max(0.0, min(1.0, float(raw_score)))

    def _stable_hash(self, s: str) -> int:
        """Deterministic hash -- immune to PYTHONHASHSEED."""
        h = 0
        for c in s:
            h = (h * 31 + ord(c)) & 0xFFFFFFFF
        return h

    def classify(
        self,
        structured_metrics: Dict[str, Any],
        user_declared: Dict[str, Any],
        optional_external: Dict[str, Any],
        pack: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Returns:
            {
                "state": "unstable" | "stable" | "expansion",
                "confidence_score": float,
                "flags": list[str],
            }
        """
        score = self._compute_score(structured_metrics, user_declared, optional_external, pack)

        # Pack-driven thresholds (SPEC-FCE-001)
        thresholds = pack.get("thresholds", {})
        unstable_max = thresholds.get("unstable_max", 0.35)
        stable_max = thresholds.get("stable_max", 0.75)

        if score < unstable_max:
            state = "unstable"
        elif score < stable_max:
            state = "stable"
        else:
            state = "expansion"

        flags = []
        if state == "unstable":
            flags.append("LOW_CONFIDENCE")
        if not pack.get("constraints"):
            flags.append("EMPTY_CONSTRAINTS")

        # DATA_GAP detection
        if not structured_metrics or not user_declared:
            flags.append("DATA_GAP")

        # UNCERTAIN zone: confidence between unstable_max and (unstable_max + 0.15)
        uncertain_threshold = unstable_max + 0.15
        if unstable_max <= score < uncertain_threshold:
            flags.append("UNCERTAIN")

        return {
            "state": state,
            "confidence_score": self.compute_confidence(score),
            "flags": flags,
        }

    def _compute_score(
        self,
        structured_metrics: Dict[str, Any],
        user_declared: Dict[str, Any],
        optional_external: Dict[str, Any],
        pack: Dict[str, Any],
    ) -> float:
        """Deterministic weighted score computation."""
        score_components = []

        constraints = pack.get("constraints", [])
        constraint_score = min(len(constraints) / 10.0, 0.3)
        score_components.append(("constraints", constraint_score))

        actions = pack.get("actions", [])
        action_score = min(len(actions) / 10.0, 0.3)
        score_components.append(("actions", action_score))

        context = {**structured_metrics, **user_declared, **optional_external}
        context_score = self._compute_context_score(context)
        score_components.append(("context", context_score))

        domain = pack.get("domain", "")
        domain_score = self._compute_domain_score(domain)
        score_components.append(("domain", domain_score))

        weights = {
            "constraints": 0.3,
            "actions": 0.2,
            "context": 0.2,
            "domain": 0.3,
        }

        total_weight = 0.0
        weighted_sum = 0.0
        for name, value in score_components:
            w = weights.get(name, 0.1)
            weighted_sum += value * w
            total_weight += w

        if total_weight == 0:
            return 0.5

        return weighted_sum / total_weight

    def _compute_context_score(self, context: Dict[str, Any]) -> float:
        """Deterministic context scoring -- no hash() randomization."""
        if not context:
            return 0.0

        key_hash_sum = 0
        for key in sorted(context.keys()):
            value = context[key]
            key_hash = self._stable_hash(key)
            if isinstance(value, (int, float)):
                key_hash_sum += key_hash + int(value * 1000)
            elif isinstance(value, str):
                key_hash_sum += key_hash + sum(ord(c) for c in value)
            elif isinstance(value, bool):
                key_hash_sum += key_hash + (1 if value else 0)
            else:
                key_hash_sum += key_hash

        return (abs(key_hash_sum) % 1000) / 1000.0 * 0.2

    def _compute_domain_score(self, domain: str) -> float:
        """Fixed baseline score per domain."""
        domain_scores = {
            "finance": 0.8,
            "health": 0.75,
            "career": 0.7,
            "test": 0.5,
        }
        return domain_scores.get(domain.lower(), 0.5)
