# Contributing to FRAME

Thanks for your interest in contributing to FRAME.

FRAME is an experimental graph-based risk analysis system for coordinated payment abuse. Contributions are welcome, especially around graph analysis, temporal features, evaluation, API reliability, frontend investigation workflows, and documentation.

---

## Development setup

### Backend

FRAME requires Python 3.12 or newer.

Create and activate a virtual environment, then install the project with development dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

Run the backend test suite:

```powershell
pytest
```

Run Ruff:

```powershell
ruff check src tests scripts
```

Start the API locally:

```powershell
python -m uvicorn frame.api.app:app --reload
```

---

## Frontend

Move into the frontend directory:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Run the development server:

```powershell
npm run dev
```

Run lint:

```powershell
npm run lint
```

Build the frontend:

```powershell
npm run build
```

---

## Before submitting a change

Please make sure:

- backend tests pass
- Ruff passes
- frontend lint passes
- frontend build succeeds
- new behavior is covered by tests where practical
- public claims remain clearly qualified when based on synthetic evaluation
- evidence is described as observed network or temporal context, not direct model attribution

---

## Commit style

FRAME uses small, focused commits.

Examples:

```text
feat: add analyst case focus control
fix: reject duplicate transaction ids
docs: add architecture diagram
test: cover temporal window edge cases
refactor: separate public risk scoring schema
```

Avoid mixing unrelated changes into the same commit.

---

## Pull requests

A pull request should explain:

1. what changed
2. why the change is needed
3. how it was tested
4. whether it changes model behavior, policy behavior, API behavior, or only presentation

If a change affects evaluation results, include the exact benchmark or test configuration used.

---

## Scope and claims

FRAME is currently a prototype and research-oriented demonstration.

Please avoid describing benchmark results as production or real-world fraud-detection performance unless they have been validated on appropriate real-world data.

Similarly, observed network evidence should not be presented as causal feature attribution.

---

## Reporting issues

When reporting a bug, include:

- expected behavior
- actual behavior
- reproduction steps
- relevant logs or stack traces
- operating system
- Python or Node.js version where relevant

---

## License

By contributing to FRAME, you agree that your contributions will be licensed under the MIT License.
