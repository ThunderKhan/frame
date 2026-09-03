from fastapi.testclient import TestClient

import frame.api.app as api_module
from frame.api.app import app


class ResetEngine:
    pass


def test_demo_reset_rebuilds_engine(
    monkeypatch,
) -> None:
    rebuilt = ResetEngine()

    monkeypatch.setattr(
        api_module,
        "build_risk_engine",
        lambda: rebuilt,
    )

    api_module.risk_engine = object()

    client = TestClient(app)

    response = client.post(
        "/api/v1/demo/reset"
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "message": "demo state reset",
    }
    assert api_module.risk_engine is rebuilt
