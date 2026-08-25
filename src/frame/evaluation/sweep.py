from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.metrics import (
    f1_score,
    precision_score,
    recall_score,
)

from frame.evaluation.cost import (
    CostModel,
    evaluate_threshold,
)


@dataclass(frozen=True)
class ThresholdSweepPoint:
    threshold: float
    precision: float
    recall: float
    f1: float
    false_positives: int
    false_negatives: int
    total_cost: float


def sweep_thresholds(
    labels: np.ndarray,
    probabilities: np.ndarray,
    cost_model: CostModel,
    thresholds: list[float] | None = None,
) -> list[ThresholdSweepPoint]:
    candidate_thresholds = (
        thresholds
        or [
            value / 100
            for value in range(
                5,
                100,
                5,
            )
        ]
    )

    results: list[
        ThresholdSweepPoint
    ] = []

    for threshold in candidate_thresholds:
        predictions = (
            probabilities >= threshold
        ).astype(int)

        cost_result = evaluate_threshold(
            labels,
            probabilities,
            threshold,
            cost_model,
        )

        results.append(
            ThresholdSweepPoint(
                threshold=threshold,
                precision=float(
                    precision_score(
                        labels,
                        predictions,
                        zero_division=0,
                    )
                ),
                recall=float(
                    recall_score(
                        labels,
                        predictions,
                        zero_division=0,
                    )
                ),
                f1=float(
                    f1_score(
                        labels,
                        predictions,
                        zero_division=0,
                    )
                ),
                false_positives=(
                    cost_result
                    .false_positives
                ),
                false_negatives=(
                    cost_result
                    .false_negatives
                ),
                total_cost=(
                    cost_result.total_cost
                ),
            )
        )

    return results