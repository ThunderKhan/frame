from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from frame.evaluation.policy import (
    PolicyMetrics,
    evaluate_policy,
)
from frame.risk.policy import RiskPolicy


@dataclass(frozen=True)
class PolicyCostModel:
    legitimate_review_cost: float
    legitimate_block_cost: float
    fraud_allow_cost: float
    fraud_review_cost: float


@dataclass(frozen=True)
class PolicySearchResult:
    policy: RiskPolicy
    metrics: PolicyMetrics
    total_cost: float


def calculate_policy_cost(
    metrics: PolicyMetrics,
    cost_model: PolicyCostModel,
) -> float:
    return (
        metrics.legitimate_reviewed
        * cost_model.legitimate_review_cost
        + metrics.legitimate_blocked
        * cost_model.legitimate_block_cost
        + metrics.fraud_allowed
        * cost_model.fraud_allow_cost
        + metrics.fraud_reviewed
        * cost_model.fraud_review_cost
    )


def search_policy_thresholds(
    labels: np.ndarray,
    probabilities: np.ndarray,
    cost_model: PolicyCostModel,
    review_thresholds: list[float],
    block_thresholds: list[float],
) -> list[PolicySearchResult]:
    results: list[PolicySearchResult] = []

    for review_threshold in review_thresholds:
        for block_threshold in block_thresholds:
            if review_threshold >= block_threshold:
                continue

            policy = RiskPolicy(
                review_threshold=review_threshold,
                block_threshold=block_threshold,
            )

            metrics = evaluate_policy(
                labels,
                probabilities,
                policy,
            )

            total_cost = calculate_policy_cost(
                metrics,
                cost_model,
            )

            results.append(
                PolicySearchResult(
                    policy=policy,
                    metrics=metrics,
                    total_cost=total_cost,
                )
            )

    return results