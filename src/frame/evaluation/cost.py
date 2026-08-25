from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class CostModel:
    false_positive_cost: float
    false_negative_cost: float
    review_cost: float = 0.0


@dataclass(frozen=True)
class ThresholdResult:
    threshold: float
    false_positives: int
    false_negatives: int
    total_cost: float


def evaluate_threshold(
    labels: np.ndarray,
    probabilities: np.ndarray,
    threshold: float,
    cost_model: CostModel,
) -> ThresholdResult:
    predictions = (
        probabilities >= threshold
    ).astype(int)

    false_positives = int(
        np.sum(
            (predictions == 1)
            & (labels == 0)
        )
    )

    false_negatives = int(
        np.sum(
            (predictions == 0)
            & (labels == 1)
        )
    )

    total_cost = (
        false_positives
        * cost_model.false_positive_cost
        + false_negatives
        * cost_model.false_negative_cost
    )

    return ThresholdResult(
        threshold=threshold,
        false_positives=false_positives,
        false_negatives=false_negatives,
        total_cost=total_cost,
    )


def find_optimal_threshold(
    labels: np.ndarray,
    probabilities: np.ndarray,
    cost_model: CostModel,
    thresholds: list[float] | None = None,
) -> ThresholdResult:
    candidate_thresholds = thresholds or [
        value / 100
        for value in range(5, 96, 5)
    ]

    results = [
        evaluate_threshold(
            labels,
            probabilities,
            threshold,
            cost_model,
        )
        for threshold in candidate_thresholds
    ]

    return min(
        results,
        key=lambda result: result.total_cost,
    )