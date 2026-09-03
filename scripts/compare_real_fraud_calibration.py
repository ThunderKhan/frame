from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path

import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    log_loss,
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
DEFAULT_REPORT_PATH = Path(
    "reports/real_data/ulb_calibration_comparison.json"
)
DEFAULT_ARTIFACT_PATH = Path(
    "artifacts/frame_real_calibrated_v1.pkl"
)


def build_base_model() -> Pipeline:
    return Pipeline(
        steps=[
            ("scale", StandardScaler()),
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


def build_calibrated_model() -> CalibratedClassifierCV:
    return CalibratedClassifierCV(
        estimator=build_base_model(),
        method="sigmoid",
        cv=5,
        n_jobs=-1,
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
    model: object,
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
        "roc_auc": float(
            roc_auc_score(labels, probabilities)
        ),
        "precision": float(
            precision_score(labels, predictions, zero_division=0)
        ),
        "recall": float(
            recall_score(labels, predictions, zero_division=0)
        ),
        "f1": float(
            f1_score(labels, predictions, zero_division=0)
        ),
        "brier_score": float(
            brier_score_loss(labels, probabilities)
        ),
        "log_loss": float(
            log_loss(labels, probabilities, labels=[0, 1])
        ),
        "confusion_matrix": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp),
        },
    }


def run_experiment(
    name: str,
    model: object,
    dataset: object,
) -> dict[str, object]:
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

    return {
        "name": name,
        "decision_threshold": threshold,
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
        "model": model,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare uncalibrated and sigmoid-calibrated real-data "
            "fraud classifiers on the ULB Credit Card Fraud dataset."
        )
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA_PATH,
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT_PATH,
    )
    parser.add_argument(
        "--artifact",
        type=Path,
        default=DEFAULT_ARTIFACT_PATH,
    )
    return parser.parse_args()


def strip_model(experiment: dict[str, object]) -> dict[str, object]:
    return {
        key: value
        for key, value in experiment.items()
        if key != "model"
    }


def main() -> None:
    args = parse_args()
    dataset = load_creditcard_dataset(args.data)

    baseline = run_experiment(
        "baseline_balanced_logistic_regression",
        build_base_model(),
        dataset,
    )
    calibrated = run_experiment(
        "sigmoid_calibrated_balanced_logistic_regression",
        build_calibrated_model(),
        dataset,
    )

    baseline_test = baseline["test"]
    calibrated_test = calibrated["test"]

    comparison = {
        "dataset": {
            "name": "ULB Credit Card Fraud",
            "rows": dataset.total_rows,
            "fraud": dataset.total_fraud,
            "features": list(FEATURE_COLUMNS),
            "split_strategy": (
                "chronological 60/20/20 split after stable sort by Time"
            ),
        },
        "baseline": strip_model(baseline),
        "calibrated": strip_model(calibrated),
        "test_delta_calibrated_minus_baseline": {
            "pr_auc": (
                calibrated_test["pr_auc"]
                - baseline_test["pr_auc"]
            ),
            "roc_auc": (
                calibrated_test["roc_auc"]
                - baseline_test["roc_auc"]
            ),
            "f1": (
                calibrated_test["f1"]
                - baseline_test["f1"]
            ),
            "brier_score": (
                calibrated_test["brier_score"]
                - baseline_test["brier_score"]
            ),
            "log_loss": (
                calibrated_test["log_loss"]
                - baseline_test["log_loss"]
            ),
        },
        "interpretation_note": (
            "Lower Brier score and log loss indicate better probability "
            "calibration. PR-AUC and ROC-AUC measure ranking/discrimination. "
            "Thresholded precision, recall and F1 use a threshold selected "
            "only on the validation split."
        ),
    }

    args.report.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    args.artifact.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    args.report.write_text(
        json.dumps(comparison, indent=2) + "\n",
        encoding="utf-8",
    )

    with args.artifact.open("wb") as file:
        pickle.dump(
            {
                "model": calibrated["model"],
                "feature_names": tuple(FEATURE_COLUMNS),
                "decision_threshold": calibrated[
                    "decision_threshold"
                ],
                "dataset": "ULB Credit Card Fraud",
                "calibration": "sigmoid, 5-fold cross-validation",
            },
            file,
        )

    print("FRAME real-data calibration comparison complete")
    print()
    print("BASELINE")
    print(
        "Threshold: "
        f"{baseline['decision_threshold']:.6f}"
    )
    print(
        "Test PR-AUC: "
        f"{baseline_test['pr_auc']:.6f}"
    )
    print(
        "Test F1: "
        f"{baseline_test['f1']:.6f}"
    )
    print(
        "Test Brier: "
        f"{baseline_test['brier_score']:.8f}"
    )
    print(
        "Test log loss: "
        f"{baseline_test['log_loss']:.8f}"
    )
    print()
    print("CALIBRATED")
    print(
        "Threshold: "
        f"{calibrated['decision_threshold']:.6f}"
    )
    print(
        "Test PR-AUC: "
        f"{calibrated_test['pr_auc']:.6f}"
    )
    print(
        "Test F1: "
        f"{calibrated_test['f1']:.6f}"
    )
    print(
        "Test Brier: "
        f"{calibrated_test['brier_score']:.8f}"
    )
    print(
        "Test log loss: "
        f"{calibrated_test['log_loss']:.8f}"
    )
    print()
    print(f"Report: {args.report}")
    print(f"Calibrated artifact: {args.artifact}")


if __name__ == "__main__":
    main()
