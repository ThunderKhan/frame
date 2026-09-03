# FRAME Submission Guide

## One-line pitch

**FRAME is an explainable graph-intelligence system for coordinated payment abuse that combines online payment-risk scoring with schema-adaptive relationship analysis.**

## Short description

Individual payments can look normal while coordinated abuse appears through shared devices, IPs, cards, merchants, timing, and connected identities. FRAME builds and analyzes those relationships, scores native payments with a calibrated online model, applies deterministic `ALLOW / REVIEW / BLOCK` policy, and exposes observed network evidence for investigation.

FRAME also includes a Dataset Lab that can analyze known public fraud datasets or arbitrary relational CSVs without inventing relationships that are not present in the source data.

---

## Submission links

- Product: `https://frame-risk.vercel.app/`
- Dataset Lab: `https://frame-risk.vercel.app/demo/`
- Branded docs: `https://frame-risk.vercel.app/docs/`
- Backend API: `https://frame-api-tun8.onrender.com`
- OpenAPI: `https://frame-api-tun8.onrender.com/docs`
- Repository: `https://github.com/ThunderKhan/frame`

---

## What to demonstrate first

The strongest judge path is the built-in FRAME benchmark because it exercises both model layers without requiring a download.

```text
/demo/
  ↓
FRAME Ring Benchmark
  ↓
RUN BUILT-IN
  ↓
Watch transaction-order graph playback
  ↓
Shared device/IP structure emerges
  ↓
FRAME-ONLINE-V1 emits REVIEW/BLOCK alerts
  ↓
Inspect risk + observed signals
  ↓
Inspect relationship analysis metrics and anomaly percentiles
```

Then show breadth:

```text
Select PaySim / IBM AML / another adapter-ready profile
  ↓
Show schema verification
  ↓
Explain that official files are not redistributed
  ↓
Show BYOD and map arbitrary relational columns
```

---

## Technical story to tell

### Problem

Fraud systems that only score isolated rows can miss coordinated behavior where each payment looks individually plausible.

### Insight

Relationships create additional context:

```text
customer ↔ device
customer ↔ IP
customer ↔ card
customer ↔ merchant
```

Repeated/shared infrastructure and short-window bursts can reveal coordination.

### FRAME's answer

FRAME has two explicit modes:

**FRAME-ONLINE-V1**

- native payment schema
- 13 graph/temporal/context features
- calibrated logistic-regression risk probability
- deterministic `ALLOW / REVIEW / BLOCK`
- observed evidence layer

**Dataset Lab**

- known adapters or arbitrary schema mapping
- relationship graph construction
- graph-derived row features
- Isolation Forest
- within-run anomaly percentile
- optional PR-AUC / ROC-AUC when labels exist

Do not describe Dataset Lab anomaly percentiles as fraud probabilities.

---

## Claims that are safe to make

### Synthetic graph benchmark

Use the qualifier **synthetic hard-negative benchmark** whenever citing these numbers.

- 95.83% of planted fraud intercepted through `REVIEW` or `BLOCK`
- 83.33% of planted fraud blocked
- 0% of legitimate transactions blocked
- 4.48% of legitimate transactions reviewed
- 3 / 3 planted rings produced graph-backed evidence
- average fraud transaction position at graph-backed evidence emergence: 2.33
- binary threshold 0.050: precision 0.6357, recall 0.9271, F1 0.7542, PR-AUC 0.9366

Do **not** call these real-world or production performance metrics.

### ULB real-data benchmark

Use the qualifier **transaction-level fraud discrimination on real anonymized transactions**.

Held-out results:

| Model | PR-AUC | ROC-AUC | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Logistic Regression | 0.7436 | 0.9820 | 0.9434 | 0.6667 | 0.7813 |
| LightGBM | 0.7988 | 0.9811 | 0.9474 | 0.7200 | 0.8182 |
| XGBoost | 0.7909 | 0.9775 | 0.8871 | 0.7333 | 0.8029 |
| CatBoost | 0.8039 | 0.9694 | 0.8730 | 0.7333 | 0.7971 |

Safe interpretation:

- CatBoost has the highest test PR-AUC.
- LightGBM has the highest test F1 at its validation-selected threshold.
- ULB does not validate the heterogeneous graph-ring layer because the released data lacks customer/device/IP/card identifiers.

---

## Dataset Lab compatibility story

FRAME exposes 13 dataset profiles, but **does not claim to bundle 13 datasets**.

Support tiers:

- `full_pipeline` — native FRAME benchmark
- `adapter_ready` — known single-file schema after user supplies official data
- `multi_file_graph` — requires coordinated graph files
- `multi_file_gated` — multi-file plus access constraints
- `transaction_only` — useful benchmark but insufficient relational identifiers for the graph thesis

This wording is important because it shows methodological discipline instead of inflated integration claims.

---

## What not to claim

Do not say:

- "FRAME has 95.83% real-world fraud accuracy."
- "Isolation Forest outputs fraud probability."
- "Observed Network Evidence explains which feature caused the score."
- "ULB validates fraud-ring detection."
- "All 13 datasets are shipped inside FRAME."
- "Dataset playback is a WebSocket/SSE production stream."
- "FRAME uses a GNN" or "FRAME uses an LLM for scoring."
- "The public demo is production multi-tenant infrastructure."

Correct alternatives:

- synthetic benchmark result
- anomaly percentile
- observed context/evidence
- transaction-level real-data validation
- compatibility/adapters
- ordered browser playback
- calibrated logistic online model
- research-oriented deployed prototype

---

## 90-second demo outline

### 0–10s — problem

> A payment can look normal by itself. Coordinated abuse becomes visible through the infrastructure around it.

Show the landing page and the FRAME thesis.

### 10–20s — architecture

Briefly state:

> FRAME combines a native online risk model with a schema-adaptive relationship-analysis layer.

Do not spend time listing libraries.

### 20–55s — built-in benchmark

Open Dataset Lab and click `RUN BUILT-IN`.

While playback runs:

> These are transactions arriving in chronological order. FRAME builds the customer, device, IP, card and merchant graph as the traffic develops.

When shared infrastructure appears:

> The red paths are observed shared device/IP relationships across multiple customers.

When REVIEW/BLOCK appears:

> Because this benchmark uses FRAME's native schema, each payment is also processed by FRAME-ONLINE-V1. The model produces calibrated risk; a deterministic policy produces ALLOW, REVIEW or BLOCK.

### 55–70s — results

Show relationship analysis:

> Separately, the Dataset Lab ranks unusual relationship structure with Isolation Forest. This number is an anomaly percentile, not a fraud probability.

Point to PR-AUC/ROC-AUC only with the synthetic/labeled-data qualifier.

### 70–82s — arbitrary data

Show dataset catalog + BYOD:

> FRAME also supports known schema adapters and arbitrary relational CSVs. It only maps relationships actually present in the source file.

### 82–90s — close

> FRAME turns isolated payments into an explainable relationship investigation surface — without letting an LLM or opaque model independently authorize payments.

End on the graph or landing-page thesis.

---

## Final engineering verification

Run before release:

```powershell
python -m pytest
python -m ruff check src tests scripts

cd frontend
npm run lint
npm run build
cd ..
```

Expected state: all tests and linters green; production frontend build succeeds.

Then smoke-test:

```text
https://frame-risk.vercel.app/
https://frame-risk.vercel.app/demo/
https://frame-risk.vercel.app/docs/
https://frame-api-tun8.onrender.com/health
https://frame-api-tun8.onrender.com/api/v1/datasets
```

Check that `/api/v1/datasets` reports 13 profiles.

---

## Production demo smoke test

1. Hard refresh `/demo/`.
2. Confirm engine/API status is online.
3. Run FRAME Ring Benchmark.
4. Confirm graph playback starts at zero and grows transaction by transaction.
5. Confirm a genuine `REVIEW` or `BLOCK` policy alert appears during playback.
6. Confirm results show relationship metrics and anomaly percentile language.
7. Select an adapter-ready dataset and verify the upload/schema workbench is understandable.
8. Upload a known bad schema and confirm it is rejected before analysis.
9. Upload a valid mini adapter schema and confirm `SCHEMA VERIFIED`.
10. Test BYOD with at least two entity mappings.

---

## Release checklist

Before creating `v1.0.0`:

- [ ] all tests green
- [ ] Ruff green
- [ ] ESLint green
- [ ] Vite production build green
- [ ] Render deployment green
- [ ] Vercel deployment green
- [ ] production benchmark playback works
- [ ] policy alert appears
- [ ] Dataset Lab adapter flow works
- [ ] BYOD flow works
- [ ] README links resolve
- [ ] branded docs resolve
- [ ] architecture image renders on GitHub
- [ ] demo video uploaded / linked
- [ ] final submission description uses scoped claims
- [ ] repository license visible
- [ ] create release: `v1.0.0 — FRAME Buildathon Submission`

---

## Suggested submission description

FRAME — Fraud Ring Analysis & Mapping Engine — is an explainable graph-intelligence prototype for coordinated payment abuse. Its native online engine builds customer/card/device/IP/merchant context, combines graph and 30-minute temporal features, produces calibrated risk probabilities, and applies deterministic ALLOW/REVIEW/BLOCK policy with observed network evidence. A separate Dataset Lab supports public fraud-data adapters and arbitrary relational CSVs through schema-aware graph construction and unsupervised relationship anomaly ranking. FRAME is deployed end-to-end with FastAPI, React/TypeScript, interactive transaction-order graph playback, synthetic hard-negative graph evaluation, and separate held-out real-data transaction benchmarks.
