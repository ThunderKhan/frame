from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from frame.evaluation.metrics import (
    EvaluationMetrics,
    evaluate_predictions,
)
from frame.evaluation.worlds import (
    SyntheticWorld,
)
from frame.graph.builder import (
    build_payment_graph,
)
from frame.risk.baseline import (
    build_labels,
    build_transaction_feature_matrix,
    train_transaction_baseline,
)
from frame.risk.hybrid import (
    build_hybrid_feature_matrix,
    train_hybrid_model,
)


@dataclass(frozen=True)
class IndependentComparison:
    baseline: EvaluationMetrics
    hybrid: EvaluationMetrics

    test_labels: np.ndarray
    baseline_probabilities: np.ndarray
    hybrid_probabilities: np.ndarray


def evaluate_independent_worlds(
    train_world: SyntheticWorld,
    test_world: SyntheticWorld,
) -> IndependentComparison:
    train_transactions = (
        train_world.transactions
    )

    test_transactions = (
        test_world.transactions
    )

    test_labels = build_labels(
        test_transactions
    )

    baseline_model = (
        train_transaction_baseline(
            train_transactions
        )
    )

    baseline_features = (
        build_transaction_feature_matrix(
            test_transactions
        )
    )

    baseline_predictions = (
        baseline_model.predict(
            baseline_features
        )
    )

    baseline_probabilities = (
        baseline_model.predict_proba(
            baseline_features
        )[:, 1]
    )

    baseline_metrics = (
        evaluate_predictions(
            test_labels,
            baseline_predictions,
            baseline_probabilities,
        )
    )

    train_graph = build_payment_graph(
        train_transactions
    )

    test_graph = build_payment_graph(
        test_transactions
    )

    hybrid_model = train_hybrid_model(
        train_transactions,
        train_graph,
    )

    hybrid_features = (
        build_hybrid_feature_matrix(
            test_transactions,
            test_graph,
        )
    )

    hybrid_predictions = (
        hybrid_model.predict(
            hybrid_features
        )
    )

    hybrid_probabilities = (
        hybrid_model.predict_proba(
            hybrid_features
        )[:, 1]
    )

    hybrid_metrics = (
        evaluate_predictions(
            test_labels,
            hybrid_predictions,
            hybrid_probabilities,
        )
    )

    return IndependentComparison(
        baseline=baseline_metrics,
        hybrid=hybrid_metrics,
        test_labels=test_labels,
        baseline_probabilities=(
            baseline_probabilities
        ),
        hybrid_probabilities=(
            hybrid_probabilities
        ),
    )