from __future__ import annotations

from typing import Any


EXTRA_DATASET_CATALOG: tuple[dict[str, Any], ...] = (
    {
        "id": "baf-neurips",
        "name": "Bank Account Fraud (BAF) Suite",
        "provider": "Feedzai / NeurIPS 2022",
        "kind": "synthetic_from_anonymized_real",
        "access": "public_download",
        "support": "transaction_only",
        "scale": "6 datasets × 1,000,000 applications",
        "labels": True,
        "graph_mode": "none — account-opening application classification",
        "description": (
            "NeurIPS 2022 benchmark suite for realistic bank-account opening fraud, "
            "class imbalance, temporal dynamics, distribution shift and fairness."
        ),
        "source_url": "https://github.com/feedzai/bank-account-fraud",
        "limitations": (
            "Rows are account-opening applications rather than relationship-bearing "
            "payment transactions. FRAME lists BAF for model stress testing, not for "
            "relationship-graph validation."
        ),
        "default_mapping": None,
    },
    {
        "id": "bitcoinheist",
        "name": "BitcoinHeist Ransomware Address",
        "provider": "UCI Machine Learning Repository",
        "kind": "real_blockchain_derived",
        "access": "public_download",
        "support": "transaction_only",
        "scale": "2,916,697 address-time observations",
        "labels": True,
        "graph_mode": "precomputed Bitcoin graph features per address",
        "description": (
            "Bitcoin ransomware benchmark derived from daily transaction-network "
            "snapshots, with address topology features and ransomware-family labels."
        ),
        "source_url": (
            "https://archive.ics.uci.edu/dataset/526/"
            "bitcoinheistransomwareaddressdataset"
        ),
        "limitations": (
            "The released CSV contains graph-derived address features rather than the "
            "raw Bitcoin edge list, so FRAME should not reconstruct nonexistent edges."
        ),
        "default_mapping": None,
    },
)
