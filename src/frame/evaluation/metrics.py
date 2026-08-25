from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
)


@dataclass(frozen=True)
class EvaluationMetrics:
    precision: float
    recall: float
    f1: float
    pr_auc: float


def evaluate_predictions(
    labels: np.ndarray,
    predictions: np.ndarray,
    probabilities: np.ndarray,
) -> EvaluationMetrics:
    return EvaluationMetrics(
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
        pr_auc=float(
            average_precision_score(
                labels,
                probabilities,
            )
        ),
    )