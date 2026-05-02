import os
from fce.engine import Engine
from fce.builtin_pack_registry import BuiltinPackRegistry

def test_t001_deterministic_evaluation():
    fixtures_dir = os.path.join(os.path.dirname(__file__), "..", "fixtures")
    engine = Engine()
    engine.registry = BuiltinPackRegistry(fixtures_dir)
    input_data = {"domain": "valid_pack", "structured_metrics": {"amount": 1500}, "user_declared": {}}
    result1 = engine.evaluate(input_data)
    result2 = engine.evaluate(input_data)
    assert "error" not in result1, result1
    r1 = {k: v for k, v in result1.items() if k != "metadata"}
    r2 = {k: v for k, v in result2.items() if k != "metadata"}
    assert r1 == r2
    assert result1["metadata"].keys() == result2["metadata"].keys()
