"""Engine module for FCE — SPEC-FCE-001 compliant entry point."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fce.pack_validator import PackValidator
from fce.builtin_pack_registry import BuiltinPackRegistry
from fce.state_classifier import StateClassifier
from fce.constraint_activator import ConstraintActivator
from fce.output_assembler import OutputAssembler


class FCEError(Exception):
    """Structured error for FCE domain."""

    def __init__(self, error_type: str, message: str, field: Optional[str] = None):
        self.error_type = error_type
        self.message = message
        self.field = field
        super().__init__(message)


class Engine:
    """Main FCE Engine — evaluates input_data against constraint packs."""

    def __init__(self):
        self.validator = PackValidator()
        self.registry = BuiltinPackRegistry()
        self.classifier = StateClassifier()
        self.activator = ConstraintActivator()
        self.assembler = OutputAssembler()

    def evaluate(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        SPEC-FCE-001 interface.

        input_data = {
            "domain": str,
            "structured_metrics": dict,
            "user_declared": dict,
            "optional_external": dict,          # optional
            "domain_constraint_pack": dict,     # optional (custom pack)
        }

        Returns structured decision space or error dict.
        """
        required = ["domain", "structured_metrics", "user_declared"]
        for field in required:
            if field not in input_data:
                return self._error("validation_error", f"Missing required field: {field}", field)

        domain = input_data["domain"]
        structured_metrics = input_data["structured_metrics"]
        user_declared = input_data["user_declared"]
        optional_external = input_data.get("optional_external", {})
        custom_pack = input_data.get("domain_constraint_pack")

        if custom_pack is not None:
            validation = self.validator.validate(custom_pack)
            if not validation.get("valid"):
                return self._error(
                    "pack_validation_error",
                    validation.get("message", "Invalid custom constraint pack"),
                    "domain_constraint_pack",
                )
            pack = validation["data"]
        else:
            pack = self.registry.load(domain)
            if pack is None:
                return self._error("unsupported_domain_error", f"Unknown domain: {domain}", "domain")
            validation = self.validator.validate(pack)
            if not validation.get("valid"):
                return self._error(
                    "pack_validation_error",
                    validation.get("message", "Built-in pack validation failed"),
                    "domain",
                )
            pack = validation["data"]

        classification = self.classifier.classify(
            structured_metrics=structured_metrics,
            user_declared=user_declared,
            optional_external=optional_external,
            pack=pack,
        )

        state = classification["state"]
        confidence_score = classification["confidence_score"]
        flags = classification.get("flags", [])

        if state not in ("unstable", "stable", "expansion"):
            return self._error(
                "coherence_error",
                f"Classifier returned invalid state: {state}",
                "state",
            )

        pack["_confidence_score"] = confidence_score
        constraint_result = self.activator.activate(
            state=state,
            structured_metrics=structured_metrics,
            user_declared=user_declared,
            optional_external=optional_external,
            pack=pack,
        )

        if 'HARD_CONSTRAINT_TRIGGERED' in constraint_result.get('flags', []):
            if state == 'unstable':
                return self._error(
                    'domain_hard_constraint_triggered',
                    'Hard constraint activated in unstable state -- execution halted',
                    'constraints',
                )

        raw_output = {
            "state": state,
            "confidence_score": float(confidence_score),
            "allowed_actions": list(constraint_result.get("allowed_actions", [])),
            "blocked_actions": list(constraint_result.get("blocked_actions", [])),
            "discouraged_actions": list(constraint_result.get("discouraged_actions", [])),
            "priority_bucket": list(constraint_result.get("priority_bucket", [])),
            "evaluated_constraints": list(constraint_result.get("evaluated_constraints", [])),
            "reasoning": str(constraint_result.get("reasoning", "")),
            "flags": list(flags) + list(constraint_result.get("flags", [])),
            "_domain": domain,
            "_confidence_score": confidence_score,
        }

        try:
            output = self.assembler.assemble(raw_output)
        except ValueError as exc:
            return self._error("output_assembly_error", str(exc))

        if set(output["allowed_actions"]) & set(output["blocked_actions"]):
            return self._error(
                "system_rule_violation",
                "allowed_actions and blocked_actions overlap",
            )

        if state == "unstable":
            overlap = set(output["priority_bucket"]) & set(output["blocked_actions"])
            if overlap:
                return self._error(
                    "system_rule_violation",
                    "priority_bucket overlap with blocked_actions in unstable state",
                )

        return output

    def _error(self, error_type: str, message: str, field: Optional[str] = None) -> Dict[str, Any]:
        return {
            "error": {
                "type": error_type,
                "message": message,
                "field": field,
            }
        }
