"""Engine module for FCE - Point d'entrée principal."""
from fce.pack_validator import PackValidator
from fce.registry import BuiltinPackRegistry
from fce.state_classifier import StateClassifier
from fce.constraint_activator import ConstraintActivator
from fce.output_assembler import OutputAssembler


class Engine:
    """Main FCE Engine."""

    def __init__(self):
        self.validator = PackValidator()
        self.registry = BuiltinPackRegistry()
        self.classifier = StateClassifier()
        self.activator = ConstraintActivator()
        self.assembler = OutputAssembler()

    def evaluate(self, pack_id: str, context: dict | None = None) -> dict:
        """
        Pipeline :
        1. pack = registry.get(pack_id)
        2. validated = validator.validate(pack)
        3. score = classifier.score(validated, context)
        4. constraints = activator.activate(validated, score)
        5. return assembler.assemble(validated, constraints, score)
        """
        # AC-007 — guard clause
        if not pack_id:
            raise ValueError("Missing required input: pack_id")

        # 1. Récupérer le pack
        pack = self.registry.get(pack_id)

        # 2. Valider
        validated = self.validator.validate(pack)

        # 3. Scorer
        score = self.classifier.score(validated, context)

        # 4. Activer les contraintes
        constraints = self.activator.activate(validated, score)

        # 5. Assembler la sortie
        return self.assembler.assemble(validated, constraints, score)
