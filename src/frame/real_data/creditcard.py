from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

TARGET_COLUMN = "Class"
FEATURE_COLUMNS = (
    "Time",
    *(f"V{index}" for index in range(1, 29)),
    "Amount",
)
REQUIRED_COLUMNS = (*FEATURE_COLUMNS, TARGET_COLUMN)


@dataclass(frozen=True)
class CreditCardSplit:
    features: pd.DataFrame
    labels: pd.Series


@dataclass(frozen=True)
class CreditCardDataset:
    train: CreditCardSplit
    validation: CreditCardSplit
    test: CreditCardSplit
    total_rows: int
    total_fraud: int


def _validate_columns(frame: pd.DataFrame) -> None:
    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in frame.columns
    ]

    if missing:
        raise ValueError(
            "ULB credit-card dataset is missing required columns: "
            + ", ".join(missing)
        )


def _build_split(frame: pd.DataFrame) -> CreditCardSplit:
    features = frame.loc[:, FEATURE_COLUMNS].copy()
    labels = frame.loc[:, TARGET_COLUMN].astype("int8").copy()

    return CreditCardSplit(
        features=features,
        labels=labels,
    )


def load_creditcard_dataset(
    path: Path,
    *,
    train_fraction: float = 0.60,
    validation_fraction: float = 0.20,
) -> CreditCardDataset:
    if not path.exists():
        raise FileNotFoundError(
            f"Real-data CSV not found: {path}. "
            "Place the ULB creditcard.csv file at this path."
        )

    if not 0 < train_fraction < 1:
        raise ValueError("train_fraction must be between 0 and 1")

    if not 0 < validation_fraction < 1:
        raise ValueError("validation_fraction must be between 0 and 1")

    if train_fraction + validation_fraction >= 1:
        raise ValueError(
            "train_fraction + validation_fraction must be less than 1"
        )

    frame = pd.read_csv(path)
    _validate_columns(frame)

    frame = (
        frame.loc[:, REQUIRED_COLUMNS]
        .sort_values("Time", kind="stable")
        .reset_index(drop=True)
    )

    if frame.empty:
        raise ValueError("ULB credit-card dataset is empty")

    if frame.isna().any().any():
        raise ValueError(
            "ULB credit-card dataset contains missing values in required columns"
        )

    total_rows = len(frame)
    train_end = int(total_rows * train_fraction)
    validation_end = int(
        total_rows * (train_fraction + validation_fraction)
    )

    train_frame = frame.iloc[:train_end]
    validation_frame = frame.iloc[train_end:validation_end]
    test_frame = frame.iloc[validation_end:]

    for name, split_frame in (
        ("train", train_frame),
        ("validation", validation_frame),
        ("test", test_frame),
    ):
        if split_frame.empty:
            raise ValueError(f"{name} split is empty")

        if split_frame[TARGET_COLUMN].nunique() < 2:
            raise ValueError(
                f"{name} split must contain both legitimate and fraud labels"
            )

    return CreditCardDataset(
        train=_build_split(train_frame),
        validation=_build_split(validation_frame),
        test=_build_split(test_frame),
        total_rows=total_rows,
        total_fraud=int(frame[TARGET_COLUMN].sum()),
    )
