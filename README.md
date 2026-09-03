<div align="center">

# FRAME

### Fraud Ring Analysis & Mapping Engine

**Explainable graph intelligence for coordinated payment abuse.**

<br />

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116%2B-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-20232A?style=flat-square&logo=react&logoColor=61DAFB)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-6-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![NetworkX](https://img.shields.io/badge/NetworkX-Graph%20Analysis-2C5BB4?style=flat-square)](https://networkx.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![CI](https://github.com/ThunderKhan/frame/actions/workflows/ci.yml/badge.svg)](https://github.com/ThunderKhan/frame/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

<br />

**Graph-based fraud detection · Temporal risk analysis · Analyst investigation workflow**

</div>

---

<p align="center">
  <a href="#the-problem">Problem</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#real-data-benchmark">Real Data</a> •
  <a href="#synthetic-benchmark">Synthetic Benchmark</a> •
  <a href="#live-demo">Demo</a> •
  <a href="#api">API</a> •
  <a href="#running-frame">Run Locally</a>
</p>

## Highlights

- Graph-aware fraud analysis across customers, cards, devices, IPs, and merchants
- Online temporal features over a rolling 30-minute window
- Calibrated machine-learning risk scoring for the live graph pipeline
- Deterministic `ALLOW / REVIEW / BLOCK` decision policy
- Observed network evidence for analyst investigation
- Interactive live payment graph
- Real-data fraud benchmark across Logistic Regression, LightGBM, XGBoost, and CatBoost
- Chronological held-out evaluation on 284,807 anonymized card transactions
- Synthetic hard-negative benchmark with planted coordinated fraud rings
- FastAPI backend with React investigation interface

## The problem

Many payment-abuse patterns are not obvious at the level of a single transaction.

A transaction may look individually reasonable while being part of a coordinated pattern such as:

- multiple accounts sharing the same device
- multiple customers using the same IP address
- bursts of transactions within a short time window
- one device interacting with many merchants
- clusters of connected identities and payment infrastructure

FRAME is built around the idea that:

> **Individual transactions can look normal. Coordinated abuse becomes visible through relationships.**

---

## What FRAME does

For every incoming transaction, FRAME:

1. inspects its current graph context
2. computes short-window temporal activity
3. constructs an online feature vector
4. scores the transaction using a calibrated machine-learning model
5. applies a deterministic ALLOW / REVIEW / BLOCK policy
6. extracts observed network evidence
7. updates the live payment graph
8. exposes the result through a FastAPI backend and investigation interface

The model does **not** directly authorize payments.

The final policy is deterministic:

| Risk score      | Decision |
| --------------- | -------- |
| `< 0.020`       | ALLOW    |
| `0.020 – 0.699` | REVIEW   |
| `>= 0.700`      | BLOCK    |

---

## Architecture

<p align="center">
  <img
    src="assets/frame-architecture.png"
    alt="FRAME system architecture"
    width="100%"
  />
</p>

---

## Graph model

FRAME represents payment activity as an undirected graph.

### Node types

- customer
- card
- device
- IP address
- merchant

### Example

```text
customer_1
   |
   +---- card_7
   |
   +---- device_12 ---- customer_2
   |
   +---- ip_4 --------- customer_3
   |
   +---- merchant_9
```

Shared infrastructure can make coordinated activity visible even when individual transactions appear ordinary.

---

## Online features

The current live model uses 13 online features.

### Transaction context

- amount
- account age

### Graph structure

- customer degree
- card degree
- device degree
- merchant degree
- connected-component size

### 30-minute temporal activity

- device transaction count
- IP transaction count
- customer transaction count
- unique customers per device
- unique customers per IP
- unique merchants per device

The production online feature schema intentionally does not use lifetime IP degree. IP behavior remains represented through short-window temporal features.

---

## Live scoring model

The current live graph pipeline uses:

```text
StandardScaler
      ↓
LogisticRegression
      ↓
CalibratedClassifierCV
```

Configuration:

- logistic regression with balanced class weights
- maximum 2,000 iterations
- sigmoid probability calibration
- 5-fold calibration

FRAME currently does **not** use a GNN, neural network, or LLM for live transaction scoring.

The live model remains intentionally lightweight and transparent. More expressive boosted-tree models are evaluated separately on real anonymized transaction data rather than being silently substituted into the graph demo.

---

## Real-data benchmark

FRAME is separately evaluated on the **ULB Credit Card Fraud** dataset containing **284,807 anonymized card transactions** and **492 labeled fraud cases**.

To reduce temporal leakage, the data is stable-sorted by `Time` and split chronologically into **60% train / 20% validation / 20% test**. Decision thresholds are selected only on the validation split by maximizing F1, then frozen for held-out test evaluation.

This real-data experiment evaluates **transaction-level fraud discrimination**. It does **not** validate FRAME's heterogeneous customer/device/IP graph-ring layer because those relationship identifiers are not present in the public dataset.

### Held-out test results

| Model | PR-AUC | ROC-AUC | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Logistic Regression | 0.7436 | **0.9820** | 0.9434 | 0.6667 | 0.7813 |
| **LightGBM** | 0.7988 | 0.9811 | **0.9474** | 0.7200 | **0.8182** |
| XGBoost | 0.7909 | 0.9775 | 0.8871 | **0.7333** | 0.8029 |
| CatBoost | **0.8039** | 0.9694 | 0.8730 | **0.7333** | 0.7971 |

### Operational interpretation

- **CatBoost** achieved the highest held-out PR-AUC: **0.8039**.
- **LightGBM** achieved the highest F1: **0.8182**, while preserving **94.74% precision** and **72% recall**.
- On 56,962 held-out test transactions, LightGBM produced **3 false positives**, detected **54 of 75 fraud cases**, and missed 21.
- XGBoost and CatBoost each detected 55 of 75 fraud cases, with 7 and 8 false positives respectively.

The benchmark therefore does not claim one universally best model: CatBoost ranks fraud cases best by PR-AUC, while LightGBM provides the strongest F1/precision tradeoff at the selected operating point.

### Calibration experiment

FRAME also compares the balanced logistic baseline against 5-fold sigmoid calibration.

Calibration dramatically improved probability quality on the held-out test set:

| Model | Brier score ↓ | Log loss ↓ | PR-AUC | F1 |
| --- | ---: | ---: | ---: | ---: |
| Uncalibrated logistic | 0.02273 | 0.09809 | **0.7436** | **0.7813** |
| Sigmoid calibrated | **0.00054** | **0.00302** | 0.7386 | 0.7541 |

Because calibration slightly reduced held-out discrimination and F1, the real-data benchmark retains the uncalibrated logistic model as its linear baseline and treats its decision value as a **model score**, not a literal fraud probability.

### Feature importance

The three boosted-tree models independently rank anonymized feature `V14` as their most important feature. LightGBM also ranks `Amount` and `Time` among its top features.

Because `V1`–`V28` are anonymized/PCA-derived variables, FRAME does not assign semantic meaning to those feature names.

Reproducible reports are stored under:

```text
reports/real_data/
├── ulb_metrics.json
├── ulb_calibration_comparison.json
└── ulb_boosting_benchmark.json
```

---

## Observed Network Evidence

FRAME separates **risk scoring** from **analyst evidence**.

Evidence represents observed graph or temporal facts such as:

- shared device
- shared IP
- device burst
- IP burst
- customer burst
- multiple customers using one device
- multiple customers using one IP
- one device interacting with multiple merchants
- unusually large connected component

These signals are **not feature attributions**.

FRAME does not claim that any single evidence item caused the model's score. The evidence layer is intended to give analysts concrete network context around a transaction.

---

## Synthetic benchmark

> **95.83% of planted fraud was intercepted through REVIEW or BLOCK in the locked synthetic hard-negative benchmark.**

> **3 / 3 planted coordinated fraud rings produced graph-backed evidence.**

All reported results in this section are from a controlled synthetic benchmark and are not claims of production or real-world graph-ring performance.

### Locked hard-negative test results

At a binary threshold of `0.050`:

| Metric          | Result |
| --------------- | -----: |
| Precision       | 0.6357 |
| Recall          | 0.9271 |
| F1              | 0.7542 |
| PR-AUC          | 0.9366 |
| False positives |     51 |
| False negatives |      7 |

### Locked policy evaluation

Using the production policy:

| Decision | Count |
| -------- | ----: |
| ALLOW    | 4,780 |
| REVIEW   |   236 |
| BLOCK    |    80 |

Fraud outcomes:

| Outcome        | Count |
| -------------- | ----: |
| Fraud allowed  |     4 |
| Fraud reviewed |    12 |
| Fraud blocked  |    80 |

This corresponds to:

- **95.83%** of planted fraud intercepted through REVIEW or BLOCK
- **83.33%** of planted fraud blocked
- **4.17%** of planted fraud allowed
- **0%** of legitimate transactions blocked
- **4.48%** of legitimate transactions sent to review

All results above are from a **synthetic hard-negative benchmark** and should not be interpreted as production or real-world fraud-detection performance.

---

## Fraud-ring detection

In the locked graph-backed ring evaluation:

- all **3 / 3 planted fraud rings** were detected with graph-backed evidence
- average fraud transaction position at which graph-backed evidence emerged: **2.33**

This demonstrates the central FRAME hypothesis within the synthetic environment:

> relational patterns can become visible before a large number of transactions from a coordinated group have occurred.

---

## Live demo

FRAME includes a deterministic synthetic streaming demo designed to make graph formation visible in real time.

The scenario progresses through:

```text
NORMAL TRAFFIC
      ↓
COORDINATION EMERGES
      ↓
ANALYST HANDOFF
```

The demo generates ordinary traffic first, followed by a coordinated synthetic ring in which multiple customers share device and IP infrastructure.

The model and decision policy are not changed for the demo.

Synthetic traffic is used for the live presentation so coordinated behavior can be reproduced reliably. Real-world model validation is reported separately in the real-data benchmark above.

---

## API

FRAME exposes a FastAPI backend.

### Health

```text
GET /health
```

### Runtime statistics

```text
GET /api/v1/stats
```

### Current graph

```text
GET /api/v1/graph
```

### Recent risk decisions

```text
GET /api/v1/risk/recent
```

Optional query:

```text
?limit=1..200
```

### Investigation detail

```text
GET /api/v1/risk/{transaction_id}
```

### Score a transaction

```text
POST /api/v1/risk/score
```

Example request:

```json
{
  "transaction_id": "txn_example_001",
  "customer_id": "cust_001",
  "merchant_id": "merchant_004",
  "device_id": "device_012",
  "card_id": "card_007",
  "ip_id": "ip_004",
  "amount": 1499.0,
  "timestamp": "2026-08-26T12:00:00",
  "account_age_days": 240
}
```

Training labels such as `is_fraud` and `fraud_ring_id` are intentionally not part of the public scoring API.

---

## Safety and state handling

The current API includes several protections for its stateful online scoring engine:

- duplicate transaction IDs are rejected
- out-of-order timestamps are rejected
- scoring mutations are serialized with a lock
- graph and result reads use thread-safe snapshots
- public scoring input is separated from training-label schemas
- recent-result query size is bounded

The current prototype keeps online graph and temporal state in memory, so server restarts reset runtime state.

---

## Technology

### Backend

- Python
- FastAPI
- Pydantic
- NetworkX
- NumPy
- scikit-learn

### Frontend

- React
- TypeScript
- Vite
- react-force-graph-2d

### ML

- graph-derived features
- temporal-window features
- logistic regression
- probability calibration
- LightGBM
- XGBoost
- CatBoost
- chronological validation/test evaluation
- PR-AUC-focused imbalanced classification analysis

---

## Running FRAME

### 1. Install Python dependencies

```powershell
pip install -e .
```

For the optional real-data boosted-tree benchmark:

```powershell
pip install -e ".[real-ml]"
```

### 2. Train the online model artifact

```powershell
python scripts\train_online_model_artifact.py
```

### 3. Start the backend

```powershell
python -m uvicorn frame.api.app:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

### 4. Start the frontend

From the frontend directory:

```powershell
npm install
npm run dev
```

### 5. Run the synthetic streaming demo

With the backend and frontend running:

```powershell
python scripts\stream_demo_transactions.py
```

For a clean demonstration, restart the backend before streaming the scenario.

### 6. Reproduce the real-data benchmark

Download the ULB Credit Card Fraud dataset locally so `creditcard.csv` is located at:

```text
data/real/creditcard.csv
```

Then run:

```powershell
python scripts\train_real_fraud_model.py
python scripts\compare_real_fraud_calibration.py
python scripts\benchmark_real_fraud_boosting.py
```

The raw dataset and trained `.pkl` artifacts are intentionally excluded from Git.

---

## Current scope

FRAME is currently a prototype and research-oriented demonstration.

It is designed to explore:

- coordinated payment-abuse detection
- graph-based fraud context
- online temporal risk features
- explainable analyst workflows
- deterministic risk-policy integration
- real-world transaction-level fraud benchmarking

It is **not** presented as a production-ready fraud engine.

Future work may include:

- real datasets that retain customer/device/IP relationship identifiers
- richer graph-learning baselines
- persistent graph/state storage
- adaptive temporal windows
- merchant-specific calibration
- analyst feedback loops
- optional LLM-generated summaries of already-computed evidence

Any future LLM component would summarize existing evidence only and would not independently authorize or block transactions.

---

## License

MIT
