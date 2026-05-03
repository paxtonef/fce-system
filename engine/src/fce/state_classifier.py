import re
from typing import Any, Dict


class StateClassifier:
    def compute_confidence(self, raw_score): return max(0.0, min(1.0, float(raw_score)))
    def _stable_hash(self, s):
        h = 0
        for c in s: h = (h * 31 + ord(c)) & 0xFFFFFFFF
        return h

    def classify(self, structured_metrics, user_declared, optional_external, pack):
        score = self._compute_score(structured_metrics, user_declared, optional_external, pack)
        thresholds = pack.get("thresholds", {})
        unstable_max = thresholds.get("unstable_max", 0.35)
        stable_max = thresholds.get("stable_max", 0.75)
        if score < unstable_max: state = "unstable"
        elif score < stable_max: state = "stable"
        else: state = "expansion"
        flags = []
        if state == "unstable": flags.append("LOW_CONFIDENCE")
        if not pack.get("constraints"): flags.append("EMPTY_CONSTRAINTS")
        if not structured_metrics or not user_declared: flags.append("DATA_GAP")
        uncertain_threshold = unstable_max + 0.15
        if unstable_max <= score < uncertain_threshold: flags.append("UNCERTAIN")
        return {"state": state, "confidence_score": self.compute_confidence(score), "flags": flags}

    def _compute_score(self, structured_metrics, user_declared, optional_external, pack):
        score_components = []
        context = {**structured_metrics, **user_declared, **optional_external}
        metric_score = self._compute_metric_score(context, pack)
        score_components.append(("metrics", metric_score))
        constraints = pack.get("constraints", [])
        score_components.append(("constraints", min(len(constraints) / 10.0, 0.3)))
        actions = pack.get("actions", [])
        score_components.append(("actions", min(len(actions) / 10.0, 0.3)))
        score_components.append(("context", self._compute_context_score(context)))
        score_components.append(("domain", self._compute_domain_score(pack.get("domain", ""))))
        weights = {"metrics": 0.50, "constraints": 0.15, "actions": 0.15, "context": 0.10, "domain": 0.10}
        total_weight = 0.0
        weighted_sum = 0.0
        for name, value in score_components:
            w = weights.get(name, 0.1)
            weighted_sum += value * w
            total_weight += w
        if total_weight == 0: return 0.5
        return weighted_sum / total_weight

    def _compute_metric_score(self, context, pack):
        metric_thresholds = pack.get("metric_thresholds", {})
        if not metric_thresholds: return 0.5
        risk_sum = 0.0
        total_weight = 0.0
        for metric_name, config in metric_thresholds.items():
            raw_value = context.get(metric_name)
            if raw_value is None: continue
            try: value = float(raw_value)
            except (ValueError, TypeError): continue
            weight = config.get("weight", 0.1)
            critical_max = config.get("critical_max")
            critical_min = config.get("critical_min")
            warning_max = config.get("warning_max")
            warning_min = config.get("warning_min")
            metric_risk = 0.0
            if critical_max is not None and value < critical_max: metric_risk = 1.0
            elif critical_min is not None and value > critical_min: metric_risk = 1.0
            elif warning_max is not None and value < warning_max: metric_risk = 0.5
            elif warning_min is not None and value > warning_min: metric_risk = 0.5
            risk_sum += metric_risk * weight
            total_weight += weight
        if total_weight == 0: return 0.5
        return 1.0 - (risk_sum / total_weight)

    def _compute_context_score(self, context):
        if not context: return 0.0
        key_hash_sum = 0
        for key in sorted(context.keys()):
            value = context[key]
            key_hash = self._stable_hash(key)
            if isinstance(value, (int, float)): key_hash_sum += key_hash + int(value * 1000)
            elif isinstance(value, str): key_hash_sum += key_hash + sum(ord(c) for c in value)
            elif isinstance(value, bool): key_hash_sum += key_hash + (1 if value else 0)
            else: key_hash_sum += key_hash
        return (abs(key_hash_sum) % 1000) / 1000.0 * 0.2

    def _compute_domain_score(self, domain):
        return {"finance": 0.8, "health": 0.75, "career": 0.7, "test": 0.5}.get(domain.lower(), 0.5)
