from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from frame.real_data.creditcard import (
    FEATURE_COLUMNS,
    CreditCardSplit,
    load_creditcard_dataset,
)

DEFAULT_DATA_PATH = Path("data/real/creditcard.csv")
DEFAULT_ARTIFACT_PATH = Path("artifacts/frame_real_v1.pkl")
DEFAULT_METRICS_PATH = Path("reports/real_data/ulb_metrics.json")


def build_model() -> Pipeline:
    return Pipeline(
        steps=[
            (
                "scale",
                StandardScaler(),
            ),
            (
                "model",
                LogisticRegression(
                    max_iter=2_000,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )


def select_validation_threshold(
    labels: np.ndarray,
    probabilities: np.ndarray,
) -> float:
    precision, recall, thresholds = precision_recall_curve(
        labels,
        probabilities,
    )

    if thresholds.size == 0:
        return 0.5

    numerator = 2 * precision[:-1] * recall[:-1]
    denominator = precision[:-1] + recall[:-1]

    f1 = np.divide(
        numerator,
        denominator,
        out=np.zeros_like(numerator),
        where=denominator > 0,
    )

    best_index = int(np.argmax(f1))
    return float(thresholds[best_index])


def evaluate_split(
    split: CreditCardSplit,
    model: Pipeline,
    threshold: float,
) -> dict[str, object]:
    labels = split.labels.to_numpy()
    probabilities = model.predict_proba(split.features)[:, 1]
    predictions = (probabilities >= threshold).astype("int8")

    tn, fp, fn, tp = confusion_matrix(
        labels,
        predictions,
        labels=[0, 1],
    ).ravel()

    return {
        "rows": len(split.labels),
        "fraud": int(split.labels.sum()),
        "fraud_rate": float(split.labels.mean()),
        "pr_auc": float(
            average_precision_score(labels, probabilities)
        ),
        "roc_auc": float(roc_auc_score(labels, probabilities)),
        "precision": float(
            precision_score(labels, predictions, zero_division=0)
        ),
        "recall": float(
            recall_score(labels, predictions, zero_division=0)
        ),
        "f1": float(f1_score(labels, predictions, zero_division=0)),
        "confusion_matrix": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Train and evaluate FRAME's separate real-data fraud baseline "
            "using the ULB Credit Card Fraud dataset."
        )
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help="Path to ULB creditcard.csv",
    )
    parser.add_argument(
        "--artifact",
        type=Path,
        default=DEFAULT_ARTIFACT_PATH,
        help="Output path for the trained real-data model artifact",
    )
    parser.add_argument(
        "--metrics",
        type=Path,
        default=DEFAULT_METRICS_PATH,
        help="Output path for JSON evaluation metrics",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    dataset = load_creditcard_dataset(args.data)
    model = build_model()

    model.fit(
        dataset.train.features,
        dataset.train.labels,
    )

    validation_probabilities = model.predict_proba(
        dataset.validation.features
    )[:, 1]

    threshold = select_validation_threshold(
        dataset.validation.labels.to_numpy(),
        validation_probabilities,
    )

    metrics = {
        "dataset": {
            "name": "ULB Credit Card Fraud",
            "rows": dataset.total_rows,
            "fraud": dataset.total_fraud,
            "features": list(FEATURE_COLUMNS),
            "split_strategy": (
                "chronological 60/20/20 split after stable sort by Time"
            ),
        },
        "model": {
            "name": "frame-real-v1",
            "estimator": "StandardScaler + LogisticRegression",
            "class_weight": "balanced",
            "threshold_selection": (
                "validation threshold maximizing F1"
            ),
            "decision_threshold": threshold,
        },
        "train": evaluate_split(
            dataset.train,
            model,
            threshold,
        ),
        "validation": evaluate_split(
            dataset.validation,
            model,
            threshold,
        ),
        "test": evaluate_split(
            dataset.test,
            model,
            threshold,
        ),
        "scope_note": (
            "This experiment validates transaction-level fraud discrimination "
            "on real anonymized labeled transactions. It does not validate "
            "FRAME's customer/device/IP graph-ring detection layer because "
            "those relationship identifiers are not present in this dataset."
        ),
    }

    args.artifact.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    args.metrics.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with args.artifact.open("wb") as file:
        pickle.dump(
            {
                "model": model,
                "feature_names": tuple(FEATURE_COLUMNS),
                "decision_threshold": threshold,
                "dataset": "ULB Credit Card Fraud",
            },
            file,
        )

    args.metrics.write_text(
        json.dumps(metrics, indent=2) + "\n",
        encoding="utf-8",
    )

    test = metrics["test"]

    print("FRAME real-data evaluation complete")
    print(f"Dataset rows: {dataset.total_rows}")
    print(f"Fraud labels: {dataset.total_fraud}")
    print(f"Decision threshold: {threshold:.6f}")
    print(f"Test PR-AUC: {test['pr_auc']:.6f}")
    print(f"Test ROC-AUC: {test['roc_auc']:.6f}")
    print(f"Test precision: {test['precision']:.6f}")
    print(f"Test recall: {test['recall']:.6f}")
    print(f"Test F1: {test['f1']:.6f}")
    print(f"Metrics: {args.metrics}")
    print(f"Artifact: {args.artifact}")


if __name__ == "__main__":
    main()
