import pytest

from frame.risk.policy import (
    RiskAction,
    RiskPolicy,
)


def test_policy_allows_low_risk() -> None:
    policy = RiskPolicy(
        review_threshold=0.70,
        block_threshold=0.95,
    )

    assert (
        policy.decide(0.30)
        == RiskAction.ALLOW
    )


def test_policy_reviews_medium_risk() -> None:
    policy = RiskPolicy(
        review_threshold=0.70,
        block_threshold=0.95,
    )

    assert (
        policy.decide(0.80)
        == RiskAction.REVIEW
    )


def test_policy_blocks_high_risk() -> None:
    policy = RiskPolicy(
        review_threshold=0.70,
        block_threshold=0.95,
    )

    assert (
        policy.decide(0.99)
        == RiskAction.BLOCK
    )


def test_policy_rejects_invalid_threshold_order() -> None:
    with pytest.raises(ValueError):
        RiskPolicy(
            review_threshold=0.95,
            block_threshold=0.70,
        )