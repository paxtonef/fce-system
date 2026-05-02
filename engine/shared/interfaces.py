"""interfaces.py — Signatures des dépendances FCE. Ne pas modifier."""

class PackValidator:
    def validate(self, pack_data: dict) -> dict:
        """Retourne pack_data enrichi ou raise ValueError si invalide."""
        pass

class BuiltinPackRegistry:
    def get(self, pack_id: str) -> dict: pass
    def load(self, pack_id: str) -> dict: pass
    def lookup(self, pack_id: str) -> dict: pass

class StateClassifier:
    def score(self, pack_data: dict, context: dict | None = None) -> float: pass
    def compute_confidence(self, raw_score: float) -> float: pass

class ConstraintActivator:
    def activate(self, pack_data: dict, confidence_score: float) -> list[dict]: pass

class OutputAssembler:
    def check_mutual_exclusion(self, blocked_actions: list[str], allowed_actions: list[str]) -> bool: pass
    def assert_completeness(self, output: dict) -> None: pass
    def assemble(self, pack_data: dict, constraints: list[dict], score: float) -> dict: pass

class Engine:
    def __init__(self):
        self.validator = PackValidator()
        self.registry = BuiltinPackRegistry()
        self.classifier = StateClassifier()
        self.activator = ConstraintActivator()
        self.assembler = OutputAssembler()

    def evaluate(self, pack_id: str, context: dict | None = None) -> dict:
        """
        1. pack = registry.get(pack_id)
        2. validated = validator.validate(pack)
        3. score = classifier.score(validated, context)
        4. constraints = activator.activate(validated, score)
        5. return assembler.assemble(validated, constraints, score)
        """
        pass
