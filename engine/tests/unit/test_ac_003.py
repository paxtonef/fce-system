import os
from fce.engine import Engine
from fce.builtin_pack_registry import BuiltinPackRegistry

def test_t003_completeness():
    fixtures_dir = os.path.join(os.path.dirname(__file__), "..", "fixtures")
    engine = Engine()
    engine.registry = BuiltinPackRegistry(fixtures_dir)
    input_data = {"domain": "valid_pack", "structured_metrics": {"amount": 1500}, "user_declared": {}}
    result = engine.evaluate(input_data)
    assert "error" not in result, result
    assert len(result["applied_constraints"]) > 0
    assert len(result["reasoning"]) > 0
