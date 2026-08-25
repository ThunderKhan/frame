import numpy as np

from frame.evaluation.cost import (
    CostModel,
)
from frame.evaluation.sweep import (
    sweep_thresholds,
)


def test_threshold_sweep_returns_all_points() -> None:
    labels = np.asarray(
        [0, 0, 1, 1],
    )

    probabilities = np.asarray(
        [0.1, 0.6, 0.4, 0.9],
    )

    cost_model = CostModel(
        false_positive_cost=100.0,
        false_negative_cost=500.0,
    )

    results = sweep_thresholds(
        labels,
        probabilities,
        cost_model,
        thresholds=[
            0.3,
            0.5,
            0.7,
        ],
    )

    assert len(results) == 3

    assert [
        result.threshold
        for result in results
    ] == [
        0.3,
        0.5,
        0.7,
    ]