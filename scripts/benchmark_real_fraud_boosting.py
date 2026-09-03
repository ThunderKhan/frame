from __future__ import annotations

import json
import pickle
from pathlib import Path
from time import perf_counter

import numpy as np
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from xgboost import XGBClassifier

from frame.real_data.creditcard import (
    FEATURE_COLUMNS,
    CreditCardSplit,
    load_creditcard_dataset,
)

DATA_PATH = Path("data/real/creditcard.csv")
REPORT_PATH = Path("reports/real_data/ulb_boosting_benchmark.json")
ARTIFACT_DIR = Path("artifacts/real_data")


def select_threshold(labels: np.ndarray, probabilities: np.ndarray) -> float:
    precision, recall, thresholds = precision_recall_curve(labels, probabilities)
    if thresholds.size == 0:
        return 0.5

    numerator = 2 * precision[:-1] * recall[:-1]
    denominator = precision[:-1] + recall[:-1]
    scores = np.divide(
        numerator,
        denominator,
        out=np.zeros_like(numerator),
        where=denominator > 0,
    )
    return float(thresholds[int(np.argmax(scores))])


def evaluate(
    split: CreditCardSplit,
    model: object,
    threshold: float,
) -> dict[str, object]:
    started = perf_counter()
    probabilities = model.predict_proba(split.features)[:, 1]
    inference_seconds = perf_counter() - started

    labels = split.labels.to_numpy()
    predictions = (probabilities >= threshold).astype("int8")
    tn, fp, fn, tp = confusion_matrix(labels, predictions, labels=[0, 1]).ravel()

    return {
        "rows": int(len(split.labels)),
        "fraud": int(split.labels.sum()),
        "pr_auc": float(average_precision_score(labels, probabilities)),
        "roc_auc": float(roc_auc_score(labels, probabilities)),
        "precision": float(precision_score(labels, predictions, zero_division=0)),
        "recall": float(recall_score(labels, predictions, zero_division=0)),
        "f1": float(f1_score(labels, predictions, zero_division=0)),
        "inference_seconds": float(inference_seconds),
        "confusion_matrix": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp),
        },
    }


def top_feature_importance(model: object) -> list[dict[str, object]]:
    raw = getattr(model, "feature_importances_", None)
    if raw is None:
        return []

    values = np.asarray(raw, dtype=float)
    total = float(values.sum())
    if total > 0:
        values = values / total

    ranked = sorted(
        zip(FEATURE_COLUMNS, values, strict=True),
        key=lambda item: item[1],
        reverse=True,
    )[:10]

    return [
        {
            "feature": feature,
            "importance": float(importance),
        }
        for feature, importance in ranked
    ]


def build_models(train_labels: np.ndarray) -> dict[str, object]:
    positives = int(train_labels.sum())
    negatives = int(len(train_labels) - positives)
    scale_pos_weight = negatives / positives

    return {
        "lightgbm": LGBMClassifier(
            n_estimators=450,
            learning_rate=0.03,
            num_leaves=31,
            max_depth=-1,
            subsample=0.90,
            colsample_bytree=0.90,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
            verbosity=-1,
        ),
        "xgboost": XGBClassifier(
            n_estimators=450,
            max_depth=5,
            learning_rate=0.03,
            min_child_weight=2,
            subsample=0.90,
            colsample_bytree=0.90,
            objective="binary:logistic",
            eval_metric="aucpr",
            tree_method="hist",
            scale_pos_weight=scale_pos_weight,
            random_state=42,
            n_jobs=-1,
        ),
        "catboost": CatBoostClassifier(
            iterations=450,
            depth=6,
            learning_rate=0.03,
            loss_function="Logloss",
            auto_class_weights="Balanced",
            random_seed=42,
            verbose=False,
            allow_writing_files=False,
            thread_count=-1,
        ),
    }


def main() -> None:
    dataset = load_creditcard_dataset(DATA_PATH)
    train_labels = dataset.train.labels.to_numpy()
    models = build_models(train_labels)

    report: dict[str, object] = {
        "dataset": {
            "name": "ULB Credit Card Fraud",
            "rows": dataset.total_rows,
            "fraud": dataset.total_fraud,
            "features": list(FEATURE_COLUMNS),
            "split_strategy": "chronological 60/20/20 split after stable sort by Time",
        },
        "threshold_strategy": "validation threshold maximizing F1",
        "models": {},
        "scope_note": (
            "This benchmark evaluates transaction-level fraud discrimination on real "
            "anonymized labeled transactions. It does not validate FRAME's heterogeneous "
            "customer/device/IP graph-ring detection layer."
        ),
    }

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    for name, model in models.items():
        print(f"\nTraining {name}...")
        started = perf_counter()
        model.fit(dataset.train.features, dataset.train.labels)
        fit_seconds = perf_counter() - started

        validation_probabilities = model.predict_proba(dataset.validation.features)[:, 1]
        threshold = select_threshold(
            dataset.validation.labels.to_numpy(),
            validation_probabilities,
        )

        validation_metrics = evaluate(dataset.validation, model, threshold)
        test_metrics = evaluate(dataset.test, model, threshold)

        artifact_path = ARTIFACT_DIR / f"frame_real_{name}_v1.pkl"
        with artifact_path.open("wb") as file:
            pickle.dump(
                {
                    "model": model,
                    "feature_names": tuple(FEATURE_COLUMNS),
                    "decision_threshold": threshold,
                    "dataset": "ULB Credit Card Fraud",
                    "model_name": name,
                },
                file,
            )

        report["models"][name] = {
            "fit_seconds": float(fit_seconds),
            "decision_threshold": threshold,
            "validation": validation_metrics,
            "test": test_metrics,
            "top_feature_importance": top_feature_importance(model),
            "artifact": str(artifact_path),
        }

        print(f"{name} complete")
        print(f"  fit time: {fit_seconds:.2f}s")
        print(f"  threshold: {threshold:.6f}")
        print(f"  test PR-AUC: {test_metrics['pr_auc']:.6f}")
        print(f"  test ROC-AUC: {test_metrics['roc_auc']:.6f}")
        print(f"  test precision: {test_metrics['precision']:.6f}")
        print(f"  test recall: {test_metrics['recall']:.6f}")
        print(f"  test F1: {test_metrics['f1']:.6f}")

    ranked = sorted(
        report["models"].items(),
        key=lambda item: item[1]["test"]["pr_auc"],
        reverse=True,
    )
    report["ranking_by_test_pr_auc"] = [name for name, _ in ranked]

    REPORT_PATH.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    print("\nFRAME boosted-tree benchmark complete")
    print(f"Ranking by test PR-AUC: {report['ranking_by_test_pr_auc']}")
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
