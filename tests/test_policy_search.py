import numpy as np

from frame.evaluation.policy import (
    evaluate_policy,
)
from frame.evaluation.policy_search import (
    PolicyCostModel,
    calculate_policy_cost,
    search_policy_thresholds,
)
from frame.risk.policy import RiskPolicy


def test_policy_cost_calculation() -> None:
    labels = np.asarray(
        [0, 0, 1, 1],
    )

    probabilities = np.asarray(
        [0.1, 0.8, 0.6, 0.99],
    )

    policy = RiskPolicy(
        review_threshold=0.5,
        block_threshold=0.9,
    )

    metrics = evaluate_policy(
        labels,
        probabilities,
        policy,
    )

    cost_model = PolicyCostModel(
        legitimate_review_cost=10.0,
        legitimate_block_cost=200.0,
        fraud_allow_cost=1000.0,
        fraud_review_cost=50.0,
    )

    cost = calculate_policy_cost(
        metrics,
        cost_model,
    )

    assert cost >= 0.0


def test_policy_search_returns_valid_pairs() -> None:
    labels = np.asarray(
        [0, 0, 1, 1],
    )

    probabilities = np.asarray(
        [0.1, 0.6, 0.8, 0.99],
    )

    cost_model = PolicyCostModel(
        legitimate_review_cost=10.0,
        legitimate_block_cost=200.0,
        fraud_allow_cost=1000.0,
        fraud_review_cost=50.0,
    )

    results = search_policy_thresholds(
        labels,
        probabilities,
        cost_model,
        review_thresholds=[
            0.3,
            0.5,
            0.7,
        ],
        block_thresholds=[
            0.8,
            0.9,
            0.95,
        ],
    )

    assert results

    assert all(
        result.policy.review_threshold
        < result.policy.block_threshold
        for result in results
    )