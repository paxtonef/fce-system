"""Test AC-003: Completeness of applied_constraints and reasoning."""
import os
import sys
import yaml

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from fce.engine import Engine


def test_t003_completeness():
    """
    T-003: Garantir que la sortie contient toujours les contraintes appliquées et le raisonnement.
    Lancer engine.evaluate() avec fixture valide.
    Asserter que applied_constraints est non-vide.
    Asserter que reasoning est non-vide.
    """
    # Load fixture
    fixtures_dir = os.path.join(os.path.dirname(__file__), "..", "fixtures")
    fixture_path = os.path.join(fixtures_dir, "valid_pack.yaml")

    with open(fixture_path, "r") as f:
        pack_data = yaml.safe_load(f)

    # Create engine
    from fce.registry import BuiltinPackRegistry

    engine = Engine()
    # Override registry to point to fixtures
    engine.registry = BuiltinPackRegistry(fixtures_dir)

    # Context
    context = {"amount": 1500, "user_id": "test_user_123"}

    # Run evaluation
    result = engine.evaluate("valid_pack", context)

    # Verify completeness
    applied_constraints = result.get("applied_constraints")
    reasoning = result.get("reasoning")

    assert applied_constraints is not None, "applied_constraints should not be None"
    assert len(applied_constraints) > 0, "applied_constraints should not be empty"

    assert reasoning is not None, "reasoning should not be None"
    assert len(reasoning) > 0, "reasoning should not be empty"

    # Verify output structure
    assert "blocked_actions" in result
    assert "allowed_actions" in result
    assert "confidence_score" in result
    assert isinstance(result["confidence_score"], float)
    assert 0.0 <= result["confidence_score"] <= 1.0

    print("T-003 PASSED: applied_constraints and reasoning are complete")


if __name__ == "__main__":
    test_t003_completeness()
