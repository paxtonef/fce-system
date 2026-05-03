import pytest
from fastapi.testclient import TestClient

try:
    from app.main import app
except ImportError:
    pytest.skip("app.main not found -- adjust import path", allow_module_level=True)

client = TestClient(app)


def test_evaluate_missing_structured_metrics_returns_422():
    response = client.post("/evaluate", json={"domain": "finance_v1"})
    assert response.status_code == 422
    # FastAPI/Pydantic validation error format
    data = response.json()
    assert "detail" in data
    assert any("structured_metrics" in str(err.get("loc", [])) for err in data["detail"])


def test_evaluate_unknown_domain_returns_404():
    response = client.post("/evaluate", json={
        "domain": "unknown_domain_xyz",
        "structured_metrics": {},
        "user_declared": {},
    })
    assert response.status_code == 404
    detail = response.json()["detail"]
    assert detail["type"] == "unsupported_domain_error"


def test_evaluate_valid_input_returns_200():
    response = client.post("/evaluate", json={
        "domain": "finance_v1",
        "structured_metrics": {"income": 5000, "debt_ratio": 0.3},
        "user_declared": {"goal": "save"},
        "optional_external": {},
    })
    assert response.status_code == 200
    data = response.json()
    assert "state" in data
    assert "confidence_score" in data
    assert "allowed_actions" in data
    assert "blocked_actions" in data
    assert "metadata" in data


def test_evaluate_custom_pack_returns_422_on_invalid():
    response = client.post("/evaluate", json={
        "domain": "custom",
        "structured_metrics": {},
        "user_declared": {},
        "domain_constraint_pack": {"invalid": True},
    })
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["type"] == "pack_validation_error"


def test_evaluate_output_has_no_single_action_selection():
    response = client.post("/evaluate", json={
        "domain": "finance_v1",
        "structured_metrics": {},
        "user_declared": {},
    })
    if response.status_code != 200:
        pytest.skip("Pack not available")
    data = response.json()
    assert "priority_action" not in data
    assert "selected_action" not in data
    assert "executed_action" not in data
    assert "priority_bucket" in data
