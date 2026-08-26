from datetime import UTC, datetime

from fastapi.testclient import TestClient

import frame.api.app as api_module
from frame.api.app import app
from frame.risk.evidence import (
    EvidenceType,
    RiskEvidence,
)
from frame.risk.policy import (
    RiskAction,
)
from frame.risk.result import (
    RiskResult,
)


class FakeRiskEngine:
    def score(
        self,
        transaction,
    ) -> RiskResult:
        return RiskResult(
            transaction_id=(
                transaction.transaction_id
            ),
            probability=0.81,
            action=RiskAction.BLOCK,
            evidence=(
                RiskEvidence(
                    evidence_type=(
                        EvidenceType.SHARED_DEVICE
                    ),
                    severity=0.8,
                    message=(
                        "Device is already linked "
                        "to 4 customers"
                    ),
                    value=4.0,
                ),
            ),
        )


def test_score_endpoint() -> None:
    api_module.risk_engine = (
        FakeRiskEngine()
    )

    client = TestClient(app)
    
    response = client.post(
        "/api/v1/risk/score",
        json={
            "transaction_id": "txn_001",
            "customer_id": "cust_001",
            "merchant_id": "merchant_001",
            "device_id": "device_001",
            "card_id": "card_001",
            "ip_id": "ip_001",
            "amount": 2499.0,
            "timestamp": (
                datetime(
                    2026,
                    8,
                    25,
                    tzinfo=UTC,
                ).isoformat()
            ),
            "account_age_days": 91,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body[
        "transaction_id"
    ] == "txn_001"

    assert body[
        "risk_score"
    ] == 0.81

    assert body[
        "action"
    ] == "BLOCK"

    assert len(
        body["evidence"]
    ) == 1