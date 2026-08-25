from __future__ import annotations

from dataclasses import dataclass

from sklearn.model_selection import train_test_split

from frame.domain.transaction import Transaction
from frame.evaluation.metrics import EvaluationMetrics, evaluate_predictions
from frame.graph.builder import build_payment_graph
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
class ModelComparison:
    baseline: EvaluationMetrics
    hybrid: EvaluationMetrics


def compare_models(
    transactions: list[Transaction],
    test_size: float = 0.25,
    random_state: int = 42,
) -> ModelComparison:
    train_transactions, test_transactions = train_test_split(
        transactions,
        test_size=test_size,
        random_state=random_state,
        stratify=[
            transaction.is_fraud
            for transaction in transactions
        ],
    )

    baseline_model = train_transaction_baseline(
        train_transactions,
    )

    baseline_test_features = build_transaction_feature_matrix(
        test_transactions,
    )

    test_labels = build_labels(
        test_transactions,
    )

    baseline_predictions = baseline_model.predict(
        baseline_test_features,
    )

    baseline_probabilities = baseline_model.predict_proba(
        baseline_test_features,
    )[:, 1]

    baseline_metrics = evaluate_predictions(
        test_labels,
        baseline_predictions,
        baseline_probabilities,
    )

    train_graph = build_payment_graph(
        train_transactions,
    )

    test_graph = build_payment_graph(
        test_transactions,
    )

    hybrid_model = train_hybrid_model(
        train_transactions,
        train_graph,
    )

    hybrid_test_features = build_hybrid_feature_matrix(
        test_transactions,
        test_graph,
    )

    hybrid_predictions = hybrid_model.predict(
        hybrid_test_features,
    )

    hybrid_probabilities = hybrid_model.predict_proba(
        hybrid_test_features,
    )[:, 1]

    hybrid_metrics = evaluate_predictions(
        test_labels,
        hybrid_predictions,
        hybrid_probabilities,
    )

    return ModelComparison(
        baseline=baseline_metrics,
        hybrid=hybrid_metrics,
    )