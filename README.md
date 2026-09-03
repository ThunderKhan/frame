<div align="center">

<img src="assets/frame-readme-hero.png" alt="FRAME — Fraud Ring Analysis & Mapping Engine" width="100%" />

**Explainable graph intelligence for coordinated payment abuse.**

[Live Product](https://frame-risk.vercel.app/) · [Dataset Lab](https://frame-risk.vercel.app/demo/) · [Documentation](https://frame-risk.vercel.app/docs/) · [API](https://frame-api-tun8.onrender.com/docs)

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

**Online payment risk · Relationship anomaly analysis · Dataset adapters · Analyst investigation**

</div>

---

<p align="center">
  <a href="#why-frame">Why FRAME</a> •
  <a href="#two-analysis-modes">Analysis Modes</a> •
  <a href="#dataset-lab">Dataset Lab</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#evaluation">Evaluation</a> •
  <a href="#api">API</a> •
  <a href="#run-locally">Run Locally</a>
</p>

## Why FRAME

A payment can look individually ordinary while still belonging to coordinated abuse.

The useful signal may live in the relationships around it:

- multiple customers sharing one device
- multiple accounts appearing behind one IP address
- rapid bursts through reused infrastructure
- one device touching many merchants in a short window
- connected clusters that only become suspicious when viewed together

FRAME is built around one thesis:

> **Individual payments can look normal. Coordinated abuse becomes visible through relationships.**

Instead of treating fraud detection as only a row-by-row classification problem, FRAME combines transaction context, temporal behavior, relationship graphs, deterministic policy, and analyst-facing evidence.

---

## What exists today

FRAME is a deployed end-to-end prototype with:

- a stateful online payment-risk engine
- a heterogeneous customer/card/device/IP/merchant graph
- rolling 30-minute temporal features
- calibrated `FRAME-ONLINE-V1` risk probabilities
- deterministic `ALLOW / REVIEW / BLOCK` policy
- observed network/context evidence for investigation
- transaction-by-transaction graph playback
- an arbitrary relational CSV Dataset Lab
- 13 public dataset profiles with explicit compatibility tiers
- known-schema adapters for supported public datasets
- BYOD schema mapping without fabricating missing relationships
- unsupervised relationship-anomaly ranking for unknown schemas
- PR-AUC / ROC-AUC evaluation when labels are supplied
- real-data fraud benchmarks on ULB Credit Card Fraud
- synthetic hard-negative fraud-ring evaluation
- FastAPI backend, React/TypeScript frontend, CI, tests, and production deployments

---

## Two analysis modes

FRAME deliberately uses **two different analysis modes** instead of pretending one model generalizes to every financial dataset.

### 1. FRAME-ONLINE-V1 — native payment risk

Used when the incoming payment follows FRAME's native schema:

```text
customer + card + device + IP + merchant + amount + timestamp + account age
```

Pipeline:

```text
Incoming payment
      ↓
Current relationship graph
      ↓
30-minute temporal context
      ↓
13 online features
      ↓
StandardScaler
      ↓
LogisticRegression(class_weight="balanced")
      ↓
5-fold sigmoid calibration
      ↓
Risk probability
      ↓
ALLOW / REVIEW / BLOCK
      ↓
Observed Network Evidence
```

Policy:

| Calibrated risk | Decision |
| --- | --- |
| `< 0.020` | `ALLOW` |
| `0.020 – 0.699` | `REVIEW` |
| `>= 0.700` | `BLOCK` |

The model supplies risk; the deterministic policy supplies the action.

### 2. Dataset Lab — schema-adaptive relationship analysis

Used for known public datasets and arbitrary relational CSVs.

Pipeline:

```text
CSV
 ↓
Known adapter or user mapping
 ↓
Observed entity relationships
 ↓
Relationship graph
 ↓
Row-level graph-derived features
 ↓
Isolation Forest
 ↓
Anomaly percentile ranking
 ↓
Optional label evaluation
```

The Dataset Lab score is an **anomaly percentile within the current run**. It is **not a fraud probability** and does not emit `ALLOW / REVIEW / BLOCK` for arbitrary schemas.

When labels are supplied they are used for evaluation, not as Isolation Forest inputs.

The built-in FRAME benchmark is special: because it uses FRAME's native schema, the demo can show **both layers simultaneously** — Dataset Lab relationship analysis plus real `FRAME-ONLINE-V1` policy decisions during playback.

---

## Dataset Lab

Production: **https://frame-risk.vercel.app/demo/**

The Dataset Lab is designed around three judge/user paths.

### Built-in benchmark

`FRAME Ring Benchmark` requires no upload.

```text
RUN BUILT-IN
      ↓
Generate chronological hard-negative traffic
      ↓
Relationship analysis
      ↓
Transaction-by-transaction graph playback
      ↓
FRAME-ONLINE-V1 ALLOW / REVIEW / BLOCK alerts
      ↓
Evaluation + anomaly ranking
```

### Known public dataset

For adapter-ready datasets:

```text
SELECT DATASET
      ↓
Upload official CSV
      ↓
Client-side schema verification
      ↓
Known adapter mapping
      ↓
RUN FRAME
      ↓
Graph + anomaly ranking + optional label metrics
```
### Bring your own data

For arbitrary relational CSVs:

```text
UPLOAD CSV
      ↓
Detect columns
      ↓
Map 2+ observed entity columns
      ↓
Optionally map amount / label / ID / timestamp
      ↓
RUN FRAME
```

FRAME does **not** invent devices, IPs, cards, merchants, customers, or other relationships that are absent from the uploaded data.

### Dataset catalog

FRAME exposes 13 profiles with explicit support levels:

| Dataset | Support | Relationship mode |
| --- | --- | --- |
| FRAME Ring Benchmark | Full pipeline | customer / device / IP / card / merchant |
| IBM Transactions for AML | Adapter ready | banking transfer network |
| AMLSim | Adapter ready | configurable AML transaction graph |
| PaySim | Adapter ready | origin → destination accounts |
| BankSim | Adapter ready | customer → merchant |
| Sparkov Credit Card Transactions | Adapter ready | card/customer → merchant |
| Fraud Detection Handbook | Adapter ready | customer → terminal |
| IBM TabFormer Credit Card | Adapter ready | user/card/merchant relationships |
| Elliptic Bitcoin Transaction Graph | Multi-file graph | transaction graph |
| IEEE-CIS Fraud Detection | Gated / multi-file | transaction + identity tables |
| ULB Credit Card Fraud | Transaction only | anonymized tabular benchmark |
| Bank Account Fraud (BAF) Suite | Transaction only | account-opening applications |
| BitcoinHeist | Transaction only | Bitcoin address-time graph features |

A catalog entry means **FRAME understands the dataset's analytical role and ingestion requirements**. It does not mean every upstream dataset is redistributed inside this repository.

The public deployment intentionally caps CSV uploads and row counts to keep the free hosted demo bounded.

---

## Architecture

<p align="center">
  <img src="assets/frame-architecture.png" alt="FRAME system architecture" width="100%" />
</p>

At a high level:

```text
                         ┌─────────────────────────┐
                         │   React / TypeScript    │
                         │ Landing · Demo · Docs   │
                         └────────────┬────────────┘
                                      │ HTTPS
                         ┌────────────▼────────────┐
                         │        FastAPI          │
                         └──────┬───────────┬──────┘
                                │           │
                ┌───────────────▼───┐   ┌──▼──────────────────┐
                │ FRAME-ONLINE-V1   │   │ Dataset Lab          │
                │ Stateful scoring  │   │ Schema-adaptive      │
                └───────┬───────────┘   └─────────┬────────────┘
                        │                         │
             ┌──────────▼──────────┐   ┌──────────▼───────────┐
             │ Graph + temporal    │   │ Relationship graph    │
             │ feature engine      │   │ + row graph features  │
             └──────────┬──────────┘   └──────────┬───────────┘
                        │                         │
             ┌──────────▼──────────┐   ┌──────────▼───────────┐
             │ Calibrated LR       │   │ Isolation Forest      │
             │ + policy + evidence │   │ + percentile ranking  │
             └─────────────────────┘   └───────────────────────┘
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for component boundaries, state semantics, ingestion rules, and deployment architecture.

---

## Native graph model

FRAME's online payment graph contains:

- `customer`
- `card`
- `device`
- `ip`
- `merchant`

Example:

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

Shared infrastructure can reveal coordination that is invisible when each transaction is viewed independently.

---

## Online features

`FRAME-ONLINE-V1` uses 13 online features.

**Transaction context**

- amount
- account age

**Graph structure**

- customer degree
- card degree
- device degree
- merchant degree
- connected-component size

**Rolling 30-minute context**

- device transaction count
- IP transaction count
- customer transaction count
- unique customers per device
- unique customers per IP
- unique merchants per device

Lifetime IP degree is intentionally excluded from the production online feature schema; IP behavior remains represented through short-window temporal features.

---

## Observed Network Evidence

FRAME separates **model risk** from **analyst evidence**.

Evidence is made of observed graph/temporal facts such as:

- shared device
- shared IP
- device burst
- IP burst
- customer burst
- multiple customers using one device
- multiple customers using one IP
- one device interacting with multiple merchants
- unusually large connected component

These are **not feature attributions**.

FRAME does not claim that any single evidence item caused the model score. The evidence layer gives an analyst concrete context around a decision.

---

## Evaluation

FRAME reports two distinct kinds of evaluation and keeps their scope separate.

### Synthetic hard-negative graph benchmark

> **95.83% of planted fraud was intercepted through REVIEW or BLOCK.**

> **3 / 3 planted coordinated rings produced graph-backed evidence.**

These are controlled synthetic results and are **not claims of production or real-world graph-ring performance**.

At the locked binary threshold `0.050`:

| Metric | Result |
| --- | ---: |
| Precision | 0.6357 |
| Recall | 0.9271 |
| F1 | 0.7542 |
| PR-AUC | 0.9366 |
| False positives | 51 |
| False negatives | 7 |

Locked policy evaluation:

| Decision | Count |
| --- | ---: |
| ALLOW | 4,780 |
| REVIEW | 236 |
| BLOCK | 80 |

Fraud outcomes:

| Outcome | Count |
| --- | ---: |
| Fraud allowed | 4 |
| Fraud reviewed | 12 |
| Fraud blocked | 80 |
Equivalent rates:

- **95.83%** planted fraud intercepted through `REVIEW` or `BLOCK`
- **83.33%** planted fraud blocked
- **4.17%** planted fraud allowed
- **0%** legitimate transactions blocked
- **4.48%** legitimate transactions reviewed

In the locked graph-backed ring evaluation:

- **3 / 3** planted fraud rings produced graph-backed evidence
- average fraud transaction position at evidence emergence: **2.33**

### Real transaction-level benchmark — ULB Credit Card Fraud

The ULB dataset contains **284,807 anonymized transactions** and **492 fraud cases**.

FRAME stable-sorts by `Time`, then uses a chronological **60% train / 20% validation / 20% test** split. Decision thresholds are selected on validation data and frozen before held-out testing.

This experiment evaluates **transaction-level fraud discrimination only**. The public ULB release does not contain customer/device/IP/card relationship identifiers, so it does not validate FRAME's heterogeneous fraud-ring graph layer.

Held-out results:

| Model | PR-AUC | ROC-AUC | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Logistic Regression | 0.7436 | **0.9820** | 0.9434 | 0.6667 | 0.7813 |
| **LightGBM** | 0.7988 | 0.9811 | **0.9474** | 0.7200 | **0.8182** |
| XGBoost | 0.7909 | 0.9775 | 0.8871 | **0.7333** | 0.8029 |
| CatBoost | **0.8039** | 0.9694 | 0.8730 | **0.7333** | 0.7971 |

Interpretation:

- CatBoost ranks fraud cases best by held-out PR-AUC (`0.8039`).
- LightGBM has the strongest held-out F1 (`0.8182`) at its validation-selected threshold.
- LightGBM produced 3 false positives and detected 54 of 75 fraud cases on the held-out test partition.
- XGBoost and CatBoost each detected 55 of 75 fraud cases, with 7 and 8 false positives respectively.

The three boosted-tree models independently rank anonymized `V14` as their most important feature. FRAME does not assign semantic meaning to PCA-derived `V1`–`V28`.

### Calibration experiment

| Model | Brier ↓ | Log loss ↓ | PR-AUC | F1 |
| --- | ---: | ---: | ---: | ---: |
| Uncalibrated logistic | 0.02273 | 0.09809 | **0.7436** | **0.7813** |
| Sigmoid calibrated | **0.00054** | **0.00302** | 0.7386 | 0.7541 |

Calibration substantially improved probability calibration while slightly reducing ranking/F1 in this experiment. The ULB linear baseline therefore remains a separate experimental benchmark; it is not silently substituted for `FRAME-ONLINE-V1`.

Reproducible committed reports:

```text
reports/real_data/
├── ulb_metrics.json
├── ulb_calibration_comparison.json
└── ulb_boosting_benchmark.json
```

---

## Live product and demo

- **Product:** https://frame-risk.vercel.app/
- **Dataset Lab:** https://frame-risk.vercel.app/demo/
- **Branded docs:** https://frame-risk.vercel.app/docs/
- **API:** https://frame-api-tun8.onrender.com
- **OpenAPI:** https://frame-api-tun8.onrender.com/docs

Recommended judge path:

```text
Open /demo/
    ↓
FRAME Ring Benchmark
    ↓
RUN BUILT-IN
    ↓
Watch transaction-order playback
    ↓
Observe shared device/IP structure emerge
    ↓
Observe genuine FRAME-ONLINE-V1 REVIEW/BLOCK alerts
    ↓
Inspect graph + evaluation + anomaly ranking
    ↓
Try a known adapter or BYOD CSV
```

Dataset playback is faithful to transaction order but is currently **batch-computed then replayed in the browser**. It is not claimed to be an SSE/WebSocket production stream.

---

## API

### Online engine

```text
GET  /health
GET  /api/v1/stats
GET  /api/v1/graph
GET  /api/v1/risk/recent
GET  /api/v1/risk/{transaction_id}
POST /api/v1/risk/score
```

Public scoring input intentionally excludes training labels such as `is_fraud` and `fraud_ring_id`.

Example:

```json
{
  "transaction_id": "txn_example_001",
  "customer_id": "cust_001",
  "merchant_id": "merchant_004",
  "device_id": "device_012",
  "card_id": "card_007",
  "ip_id": "ip_004",
  "amount": 1499.0,
  "timestamp": "2026-09-03T12:00:00",
  "account_age_days": 240
}
```

### Dataset Lab

```text
GET  /api/v1/datasets
POST /api/v1/analysis/dataset
POST /api/v1/analysis/builtin/frame-benchmark
```

The public Dataset Lab enforces bounded upload/row limits and browser graph truncation where needed.

---

## State and safety semantics

The online API currently:

- rejects duplicate transaction IDs
- rejects out-of-order timestamps
- serializes scoring mutations
- exposes thread-safe graph/result snapshots
- separates public scoring inputs from training-label schemas
- bounds recent-result queries

Online graph and temporal state are currently in memory. Server restarts reset that state.

The public demo reset endpoint exists for hackathon/demo reproducibility and should not be interpreted as a production multi-tenant state architecture.

---

## Technology

**Backend**

- Python 3.12+
- FastAPI
- Pydantic
- NetworkX
- NumPy / pandas
- scikit-learn

**Frontend**

- React 19
- TypeScript
- Vite
- react-force-graph-2d

**ML / evaluation**

- graph-derived relationship features
- rolling temporal features
- calibrated logistic regression
- Isolation Forest for arbitrary relational anomaly ranking
- LightGBM / XGBoost / CatBoost comparative benchmarks
- chronological held-out evaluation
- PR-AUC-focused imbalanced classification analysis

---

## Run locally

### Backend

```powershell
pip install -e .
python scripts\train_online_model_artifact.py
python -m uvicorn frame.api.app:app --reload
```

API: `http://127.0.0.1:8000`

OpenAPI: `http://127.0.0.1:8000/docs`

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

### Quality gate

```powershell
python -m pytest
python -m ruff check src tests scripts

cd frontend
npm run lint
npm run build
```

### Reproduce ULB experiments

Place `creditcard.csv` at:

```text
data/real/creditcard.csv
```

Then:

```powershell
python scripts\train_real_fraud_model.py
python scripts\compare_real_fraud_calibration.py
python scripts\benchmark_real_fraud_boosting.py
```

Optional boosted-tree dependencies:

```powershell
pip install -e ".[real-ml]"
```

Raw public datasets and generated model artifacts are intentionally excluded from Git.

---

## Scope and limitations

FRAME is a research-oriented prototype, not a production fraud engine.

Current limitations include:

- the synthetic graph benchmark is not real-world graph-ring validation
- the ULB experiment validates transaction-level discrimination only
- generic Dataset Lab analysis uses unsupervised relationship ranking, not calibrated fraud probability
- some public datasets require external download, gated access, or multi-file ingestion
- the public hosted Dataset Lab is intentionally bounded
- online runtime state is in memory
- dataset playback is browser replay of ordered rows, not a server-pushed streaming transport
- the system does not currently use a GNN or LLM for transaction authorization

Potential future work includes persistent graph storage, richer graph-learning baselines, adaptive temporal windows, tenant-isolated analysis sessions, analyst feedback loops, and optional summaries of already-computed evidence.

Any future LLM component would summarize existing evidence only; it would not independently authorize or block transactions.

---

## Additional documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system boundaries, model roles, state and data flow
- [`docs/SUBMISSION.md`](docs/SUBMISSION.md) — judge-facing demo path, claims, links, and release checklist
- [`CONTRIBUTING.md`](CONTRIBUTING.md)
- [`SECURITY.md`](SECURITY.md)

---

## License

MIT