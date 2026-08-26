from frame.risk.policy import (
    RiskAction,
)
from frame.risk.result import (
    RiskResult,
)


def test_risk_result_history_shape() -> None:
    result = RiskResult(
        transaction_id="txn_001",
        probability=0.5,
        action=RiskAction.REVIEW,
        evidence=(),
    )

    history = [
        result
    ]

    assert history[
        -1
    ].transaction_id == "txn_001"