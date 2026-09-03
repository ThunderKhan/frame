from __future__ import annotations

from typing import Any


DATASET_CATALOG: tuple[dict[str, Any], ...] = (
    {
        "id": "frame-benchmark",
        "name": "FRAME Ring Benchmark",
        "provider": "FRAME",
        "kind": "synthetic",
        "access": "built_in",
        "support": "full_pipeline",
        "scale": "configurable",
        "labels": True,
        "graph_mode": "customer/device/ip/card/merchant",
        "description": (
            "FRAME's native hard-negative benchmark with explicit customer, "
            "device, IP, card and merchant relationships."
        ),
        "source_url": "https://github.com/ThunderKhan/frame",
        "limitations": (
            "Synthetic benchmark; use it to validate the full graph pipeline, "
            "not as evidence of production fraud performance."
        ),
        "default_mapping": {
            "transaction_id": "transaction_id",
            "timestamp": "timestamp",
            "amount": "amount",
            "label": "is_fraud",
            "entities": [
                {"column": "customer_id", "type": "customer"},
                {"column": "device_id", "type": "device"},
                {"column": "ip_id", "type": "ip"},
                {"column": "card_id", "type": "card"},
                {"column": "merchant_id", "type": "merchant"},
            ],
        },
    },
    {
        "id": "ibm-aml",
        "name": "IBM Transactions for AML",
        "provider": "IBM",
        "kind": "synthetic",
        "access": "public_download",
        "support": "adapter_ready",
        "scale": "millions of transactions",
        "labels": True,
        "graph_mode": "account-to-account + bank relationships",
        "description": (
            "Synthetic banking transactions with sender/receiver accounts, "
            "banks, payment format and money-laundering labels."
        ),
        "source_url": (
            "https://www.kaggle.com/datasets/ealtman2019/"
            "ibm-transactions-for-anti-money-laundering-aml"
        ),
        "limitations": (
            "Large files are not bundled with FRAME; upload the official CSV "
            "or a subset and the adapter maps it automatically."
        ),
        "default_mapping": {
            "timestamp": "Timestamp",
            "amount": "Amount Paid",
            "label": "Is Laundering",
            "entities": [
                {"column": "Account", "type": "account"},
                {"column": "Account.1", "type": "account"},
                {"column": "From Bank", "type": "bank"},
                {"column": "To Bank", "type": "bank"},
            ],
        },
    },
    {
        "id": "amlsim",
        "name": "AMLSim",
        "provider": "IBM",
        "kind": "synthetic",
        "access": "open_source",
        "support": "adapter_ready",
        "scale": "configurable simulator",
        "labels": True,
        "graph_mode": "account transfer graph + AML alert patterns",
        "description": (
            "Multi-agent AML simulator designed specifically for graph "
            "algorithms and money-laundering pattern evaluation."
        ),
        "source_url": "https://github.com/IBM/AMLSim",
        "limitations": (
            "AMLSim is a generator rather than a single immutable dataset; "
            "FRAME ingests its exported transaction CSVs."
        ),
        "default_mapping": {
            "timestamp": "timestamp",
            "amount": "amount",
            "label": "is_sar",
            "entities": [
                {"column": "orig_id", "type": "account"},
                {"column": "dest_id", "type": "account"},
            ],
        },
    },
    {
        "id": "paysim",
        "name": "PaySim",
        "provider": "PaySim / Kaggle mirror",
        "kind": "synthetic",
        "access": "public_download",
        "support": "adapter_ready",
        "scale": "6,362,620 transactions",
        "labels": True,
        "graph_mode": "source-account to destination-account",
        "description": (
            "Mobile-money transfer simulation with source/destination account "
            "IDs, transaction type, balances and fraud labels."
        ),
        "source_url": "https://www.kaggle.com/datasets/ealaxi/paysim1",
        "limitations": (
            "Contains account-transfer relationships but no device/IP/card "
            "identity layer. FRAME therefore analyzes the graph it actually has."
        ),
        "default_mapping": {
            "timestamp": "step",
            "amount": "amount",
            "label": "isFraud",
            "entities": [
                {"column": "nameOrig", "type": "account"},
                {"column": "nameDest", "type": "account"},
            ],
        },
    },
    {
        "id": "banksim",
        "name": "BankSim",
        "provider": "BankSim",
        "kind": "synthetic",
        "access": "public_download",
        "support": "adapter_ready",
        "scale": "hundreds of thousands of transactions",
        "labels": True,
        "graph_mode": "customer-to-merchant bipartite graph",
        "description": (
            "Bank-payment simulation with customer IDs, merchant IDs, category, "
            "amount and fraud labels."
        ),
        "source_url": "https://www.kaggle.com/datasets/ntnu-testimon/banksim1",
        "limitations": (
            "Useful for customer/merchant relationship analysis; it does not "
            "contain device or IP identifiers."
        ),
        "default_mapping": {
            "timestamp": "step",
            "amount": "amount",
            "label": "fraud",
            "entities": [
                {"column": "customer", "type": "customer"},
                {"column": "merchant", "type": "merchant"},
            ],
        },
    },
    {
        "id": "sparkov",
        "name": "Sparkov Credit Card Transactions",
        "provider": "Sparkov",
        "kind": "synthetic",
        "access": "public_download",
        "support": "adapter_ready",
        "scale": "~1.85 million transactions",
        "labels": True,
        "graph_mode": "card/customer-to-merchant + geography",
        "description": (
            "Synthetic card transactions covering 1,000 customers and 800 "
            "merchants with timestamps, amounts, geography and fraud labels."
        ),
        "source_url": "https://www.kaggle.com/datasets/kartik2112/fraud-detection",
        "limitations": (
            "Rich customer/card/merchant structure, but no native device or IP IDs."
        ),
        "default_mapping": {
            "transaction_id": "trans_num",
            "timestamp": "trans_date_trans_time",
            "amount": "amt",
            "label": "is_fraud",
            "entities": [
                {"column": "cc_num", "type": "card"},
                {"column": "merchant", "type": "merchant"},
            ],
        },
    },
    {
        "id": "fraud-handbook",
        "name": "Fraud Detection Handbook",
        "provider": "Fraud Detection Handbook",
        "kind": "synthetic",
        "access": "open_source",
        "support": "adapter_ready",
        "scale": "configurable / published raw datasets",
        "labels": True,
        "graph_mode": "customer-to-terminal",
        "description": (
            "Reproducible payment-card simulation with customer IDs, terminal IDs, "
            "timestamps, amounts and fraud labels."
        ),
        "source_url": "https://github.com/Fraud-Detection-Handbook/simulated-data-raw",
        "limitations": (
            "Designed for reproducible fraud research; relationship depth is "
            "customer/terminal rather than full device/IP identity."
        ),
        "default_mapping": {
            "transaction_id": "TRANSACTION_ID",
            "timestamp": "TX_DATETIME",
            "amount": "TX_AMOUNT",
            "label": "TX_FRAUD",
            "entities": [
                {"column": "CUSTOMER_ID", "type": "customer"},
                {"column": "TERMINAL_ID", "type": "terminal"},
            ],
        },
    },
    {
        "id": "tabformer",
        "name": "IBM TabFormer Credit Card",
        "provider": "IBM Research",
        "kind": "synthetic",
        "access": "open_source_large",
        "support": "adapter_ready",
        "scale": "24 million transactions",
        "labels": True,
        "graph_mode": "user/card/merchant temporal relationships",
        "description": (
            "Large synthetic credit-card sequence dataset released with IBM's "
            "TabFormer research code."
        ),
        "source_url": "https://github.com/IBM/TabFormer",
        "limitations": (
            "Very large; FRAME's public deployment should analyze bounded subsets "
            "instead of loading all 24M rows into memory."
        ),
        "default_mapping": {
            "timestamp": "Time",
            "amount": "Amount",
            "label": "Is Fraud?",
            "entities": [
                {"column": "User", "type": "customer"},
                {"column": "Card", "type": "card"},
                {"column": "Merchant Name", "type": "merchant"},
            ],
        },
    },
    {
        "id": "elliptic",
        "name": "Elliptic Bitcoin Transaction Graph",
        "provider": "Elliptic",
        "kind": "real_anonymized_blockchain",
        "access": "public_download",
        "support": "multi_file_graph",
        "scale": "203,769 nodes / 234,355 edges",
        "labels": True,
        "graph_mode": "transaction-to-transaction Bitcoin flow graph",
        "description": (
            "Anonymized Bitcoin transaction graph with licit, illicit and unknown "
            "node labels plus 166 node features."
        ),
        "source_url": "https://www.kaggle.com/datasets/ellipticco/elliptic-data-set",
        "limitations": (
            "Uses separate edge, feature and class files; it requires the multi-file "
            "graph importer rather than the single-CSV adapter."
        ),
        "default_mapping": None,
    },
    {
        "id": "ieee-cis",
        "name": "IEEE-CIS Fraud Detection",
        "provider": "IEEE-CIS / Vesta",
        "kind": "real_anonymized",
        "access": "competition_gated",
        "support": "multi_file_gated",
        "scale": "1.35 GB / transaction + identity tables",
        "labels": True,
        "graph_mode": "transaction/card/device/email identity relationships",
        "description": (
            "Competition dataset pairing transaction records with an identity table, "
            "including card and device-related fields."
        ),
        "source_url": "https://www.kaggle.com/c/ieee-fraud-detection/data",
        "limitations": (
            "Kaggle competition rules require the user to accept access terms; FRAME "
            "must not redistribute or silently download it."
        ),
        "default_mapping": None,
    },
    {
        "id": "ulb-creditcard",
        "name": "ULB Credit Card Fraud",
        "provider": "Machine Learning Group ULB",
        "kind": "real_anonymized",
        "access": "public_download",
        "support": "transaction_only",
        "scale": "284,807 transactions / 492 fraud",
        "labels": True,
        "graph_mode": "none — transaction classification only",
        "description": (
            "Highly imbalanced real anonymized card-fraud benchmark with PCA features, "
            "Time, Amount and Class."
        ),
        "source_url": "https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud",
        "limitations": (
            "No customer, merchant, device, IP or card identifiers are present, so it "
            "cannot validate FRAME's relationship-graph thesis."
        ),
        "default_mapping": {
            "timestamp": "Time",
            "amount": "Amount",
            "label": "Class",
            "entities": [],
        },
    },
)


CATALOG_BY_ID = {
    dataset["id"]: dataset
    for dataset in DATASET_CATALOG
}
