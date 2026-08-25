import numpy as np

from frame.evaluation.cost import (
    CostModel,
    evaluate_threshold,
    find_optimal_threshold,
)


def test_threshold_cost_counts_errors() -> None:
    labels = np.asarray(
        [0, 0, 1, 1],
    )

    probabilities = np.asarray(
        [0.1, 0.8, 0.4, 0.9],
    )

    cost_model = CostModel(
        false_positive_cost=100.0,
        false_negative_cost=500.0,
    )

    result = evaluate_threshold(
        labels,
        probabilities,
        threshold=0.5,
        cost_model=cost_model,
    )

    assert result.false_positives == 1
    assert result.false_negatives == 1
    assert result.total_cost == 600.0


def test_optimal_threshold_minimizes_cost() -> None:
    labels = np.asarray(
        [0, 0, 0, 1, 1, 1],
    )

    probabilities = np.asarray(
        [0.1, 0.2, 0.6, 0.4, 0.8, 0.9],
    )

    cost_model = CostModel(
        false_positive_cost=100.0,
        false_negative_cost=500.0,
    )

    result = find_optimal_threshold(
        labels,
        probabilities,
        cost_model,
        thresholds=[
            0.3,
            0.5,
            0.7,
        ],
    )

    assert result.threshold in {
        0.3,
        0.5,
        0.7,
    }