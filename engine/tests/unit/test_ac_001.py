"""Test AC-001: Deterministic engine evaluation."""
import os
import sys
import yaml

# Ajouter src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from fce.engine import Engine


def test_t001_deterministic_evaluation():
    """
    T-001: Garantir que le moteur produit toujours le même résultat pour les mêmes données.
    Appeler engine.evaluate deux fois avec les mêmes données (pack_id + context identiques)
    Asserter que les deux résultats sont identiques (==)
    """
    # Charger le fixture valid_pack.yaml
    fixtures_dir = os.path.join(os.path.dirname(__file__), "..", "fixtures")
    fixture_path = os.path.join(fixtures_dir, "valid_pack.yaml")

    with open(fixture_path, "r") as f:
        pack_data = yaml.safe_load(f)

    # Créer l'engine avec un registry pointant sur le répertoire fixtures
    from fce.registry import BuiltinPackRegistry
    from fce.pack_validator import PackValidator
    from fce.state_classifier import StateClassifier
    from fce.constraint_activator import ConstraintActivator
    from fce.output_assembler import OutputAssembler

    engine = Engine()
    # Override le registry pour pointer sur les fixtures
    engine.registry = BuiltinPackRegistry(fixtures_dir)

    # Contexte de test
    context = {"amount": 1500, "user_id": "test_user_123"}

    # Premier appel
    result1 = engine.evaluate("valid_pack", context)

    # Deuxième appel avec les mêmes données
    result2 = engine.evaluate("valid_pack", context)

    # Assertion: les résultats doivent être identiques
    assert result1 == result2, f"Results differ!\nResult 1: {result1}\nResult 2: {result2}"

    # Vérifications supplémentaires BR-006
    assert isinstance(result1["confidence_score"], float)
    assert 0.0 <= result1["confidence_score"] <= 1.0
    assert "applied_constraints" in result1
    assert "reasoning" in result1
    assert "blocked_actions" in result1
    assert "allowed_actions" in result1

    # Vérifier que blocked_actions et allowed_actions sont disjoints
    blocked_set = set(result1["blocked_actions"])
    allowed_set = set(result1["allowed_actions"])
    assert len(blocked_set & allowed_set) == 0, "blocked_actions and allowed_actions must be disjoint"

    print("T-001 PASSED: Engine evaluation is deterministic")


if __name__ == "__main__":
    test_t001_deterministic_evaluation()
