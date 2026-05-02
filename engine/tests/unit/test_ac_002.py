"""Test AC-002: Mutual exclusion of blocked and allowed actions."""
import os
import sys
import yaml

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from fce.engine import Engine


def test_t002_mutual_exclusion():
    """
    T-002: Garantir qu'aucune action ne peut être à la fois autorisée et bloquée.
    Lancer engine.evaluate() avec fixture valide.
    Asserter que blocked_actions ∩ allowed_actions = ensemble vide.
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

    # Verify mutual exclusion
    blocked_actions = result.get("blocked_actions", [])
    allowed_actions = result.get("allowed_actions", [])

    blocked_set = set(blocked_actions)
    allowed_set = set(allowed_actions)
    intersection = blocked_set & allowed_set

    assert len(intersection) == 0, (
        f"Mutual exclusion violated: actions {sorted(intersection)} "
        f"are in both blocked_actions and allowed_actions"
    )

    # Verify output structure
    assert "applied_constraints" in result
    assert "reasoning" in result
    assert "confidence_score" in result
    assert isinstance(result["confidence_score"], float)
    assert 0.0 <= result["confidence_score"] <= 1.0

    # Verify lists are not empty (fixture has data)
    assert len(blocked_actions) > 0 or len(allowed_actions) > 0

    print("T-002 PASSED: blocked_actions and allowed_actions are disjoint")


if __name__ == "__main__":
    test_t002_mutual_exclusion()
