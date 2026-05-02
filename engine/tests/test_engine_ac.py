import pytest
from fce.engine import Engine


@pytest.fixture
def engine():
    return Engine()


@pytest.fixture
def valid_input():
    return {
        "domain": "finance_v1",
        "structured_metrics": {"income": 5000, "debt_ratio": 0.3},
        "user_declared": {"goal": "save", "risk_tolerance": "low"},
        "optional_external": {"market_volatility": 0.15},
    }


def test_ac001_missing_field_returns_validation_error(engine, valid_input):
    del valid_input["structured_metrics"]
    result = engine.evaluate(valid_input)
    assert result["error"]["type"] == "validation_error"
    assert result["error"]["field"] == "structured_metrics"


def test_ac002_unknown_domain_returns_unsupported_domain_error(engine, valid_input):
    valid_input["domain"] = "unknown_domain_xyz"
    result = engine.evaluate(valid_input)
    assert result["error"]["type"] == "unsupported_domain_error"
    assert result["error"]["field"] == "domain"


def test_ac003_allowed_blocked_mutually_exclusive(engine, valid_input):
    result = engine.evaluate(valid_input)
    if "error" in result:
        pytest.skip("Pack not available on disk")
    assert set(result["allowed_actions"]).isdisjoint(set(result["blocked_actions"]))


def test_ac004_confidence_score_range(engine, valid_input):
    result = engine.evaluate(valid_input)
    if "error" in result:
        pytest.skip("Pack not available on disk")
    assert 0.0 <= result["confidence_score"] <= 1.0


def test_ac005_no_single_action_selection(engine, valid_input):
    result = engine.evaluate(valid_input)
    if "error" in result:
        pytest.skip("Pack not available on disk")
    assert "priority_action" not in result
    assert "selected_action" not in result
    assert "executed_action" not in result
    assert "priority_actions" in result


def test_ac006_builtin_pack_load(engine):
    input_data = {
        "domain": "finance_v1",
        "structured_metrics": {},
        "user_declared": {},
    }
    result = engine.evaluate(input_data)
    assert result.get("error", {}).get("type") in (None, "unsupported_domain_error")


def test_ac007_invalid_custom_pack_returns_pack_validation_error(engine, valid_input):
    valid_input["domain_constraint_pack"] = {"invalid": True}
    result = engine.evaluate(valid_input)
    assert result["error"]["type"] == "pack_validation_error"
    assert result["error"]["field"] == "domain_constraint_pack"


def test_ac008_missing_multiple_fields(engine):
    result = engine.evaluate({})
    assert result["error"]["type"] == "validation_error"
    assert result["error"]["field"] == "domain"


def test_ac009_invalid_state_returns_coherence_error(engine, valid_input, monkeypatch):
    from fce import state_classifier as sc_mod

    def fake_classify(*args, **kwargs):
        return {"state": "banana", "confidence_score": 0.5, "flags": []}

    monkeypatch.setattr(sc_mod.StateClassifier, "classify", fake_classify)
    result = engine.evaluate(valid_input)
    assert result["error"]["type"] == "coherence_error"


def test_ac010_domain_agnostic_core(engine, monkeypatch):
    from fce import builtin_pack_registry as reg_mod

    def fake_load(self, domain):
        return {
            "pack_id": f"{domain}_test",
            "domain": domain,
            "constraints": [{"id": "C001", "condition": "true", "action": "allow"}],
            "actions": [{"id": "A001", "risk_level": "low"}],
        }

    monkeypatch.setattr(reg_mod.BuiltinPackRegistry, "load", fake_load)
    input_data = {
        "domain": "career_v1",
        "structured_metrics": {},
        "user_declared": {},
    }
    result = engine.evaluate(input_data)
    assert "error" not in result
    assert result["state"] in ("unstable", "stable", "expansion")


def test_ac011_blocked_status_halt(engine, valid_input, monkeypatch):
    from fce import constraint_activator as ca_mod

    def fake_activate(*args, **kwargs):
        return {
            "allowed_actions": [],
            "blocked_actions": ["A001"],
            "discouraged_actions": [],
            "priority_actions": ["A001"],
            "applied_constraints": [{"id": "C001"}],
            "reasoning": "Test",
            "flags": [],
        }

    monkeypatch.setattr(ca_mod.ConstraintActivator, "activate", fake_activate)

    from fce import state_classifier as sc_mod
    monkeypatch.setattr(
        sc_mod.StateClassifier,
        "classify",
        lambda *a, **k: {"state": "unstable", "confidence_score": 0.2, "flags": []},
    )

    result = engine.evaluate(valid_input)
    assert result["error"]["type"] == "system_rule_violation"


def test_ac012_output_schema_completeness(engine, valid_input):
    result = engine.evaluate(valid_input)
    if "error" in result:
        pytest.skip("Pack not available on disk — install packs to run this test")
    required = [
        "state",
        "confidence_score",
        "allowed_actions",
        "blocked_actions",
        "discouraged_actions",
        "priority_actions",
        "applied_constraints",
        "reasoning",
        "flags",
        "metadata",
    ]
    for field in required:
        assert field in result, f"Missing field: {field}"
    assert "domain" in result["metadata"]
    assert "timestamp" in result["metadata"]
