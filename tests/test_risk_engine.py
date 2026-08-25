from datetime import (
    UTC,
    datetime,
)

import numpy as np

from frame.domain.transaction import (
    Transaction,
)
from frame.risk.engine import (
    RiskEngine,
)
from frame.risk.policy import (
    RiskAction,
    RiskPolicy,
)


class FakeModel:
    def __init__(
        self,
        probability: float,
    ) -> None:
        self.probability = probability

    def predict_proba(
        self,
        features: np.ndarray,
    ) -> np.ndarray:
        return np.asarray(
            [
                [
                    1.0 - self.probability,
                    self.probability,
                ]
            ]
        )


def make_transaction(
    transaction_id: str,
    customer_id: str,
    device_id: str = "device_shared",
    ip_id: str = "ip_shared",
) -> Transaction:
    return Transaction(
        transaction_id=transaction_id,
        customer_id=customer_id,
        merchant_id="merchant_001",
        device_id=device_id,
        card_id=f"card_{customer_id}",
        ip_id=ip_id,
        amount=500.0,
        timestamp=datetime(
            2026,
            1,
            1,
            tzinfo=UTC,
        ),
        account_age_days=200,
    )


def test_risk_engine_returns_decision() -> None:
    model = FakeModel(
        probability=0.80
    )

    policy = RiskPolicy(
        review_threshold=0.50,
        block_threshold=0.90,
    )

    engine = RiskEngine(
        model=model,  # type: ignore[arg-type]
        policy=policy,
    )

    result = engine.score(
        make_transaction(
            "txn_001",
            "cust_001",
        )
    )

    assert result.transaction_id == "txn_001"
    assert result.probability == 0.80
    assert result.action is RiskAction.REVIEW


def test_engine_accumulates_graph_context() -> None:
    model = FakeModel(
        probability=0.80
    )

    policy = RiskPolicy(
        review_threshold=0.50,
        block_threshold=0.90,
    )

    engine = RiskEngine(
        model=model,  # type: ignore[arg-type]
        policy=policy,
    )

    first = engine.score(
        make_transaction(
            "txn_001",
            "cust_001",
        )
    )

    second = engine.score(
        make_transaction(
            "txn_002",
            "cust_002",
        )
    )

    assert first.evidence == ()

    assert len(
        second.evidence
    ) >= 1