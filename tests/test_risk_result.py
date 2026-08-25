from frame.risk.policy import (
    RiskAction,
)
from frame.risk.result import (
    RiskResult,
)


def test_risk_result_can_store_decision() -> None:
    result = RiskResult(
        transaction_id="txn_001",
        probability=0.91,
        action=RiskAction.REVIEW,
        evidence=(),
    )

    assert result.transaction_id == "txn_001"
    assert result.probability == 0.91
    assert result.action is RiskAction.REVIEW