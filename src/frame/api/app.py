from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    HTTPException,
)

from frame.api.graph import (
    serialize_graph,
)
from frame.api.runtime import (
    build_risk_engine,
)
from frame.domain.transaction import (
    Transaction,
)
from frame.risk.engine import RiskEngine

risk_engine: RiskEngine | None = None


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    global risk_engine

    risk_engine = build_risk_engine()

    yield

    risk_engine = None


app = FastAPI(
    title="FRAME Risk API",
    version="0.1.0",
    description=(
        "Explainable graph intelligence "
        "for coordinated payment abuse."
    ),
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "frame-risk-api",
    }

@app.get("/api/v1/graph")
def get_graph() -> dict[
    str,
    list[dict[str, object]],
]:
    if risk_engine is None:
        raise HTTPException(
            status_code=503,
            detail="risk engine unavailable",
        )

    return serialize_graph(
        risk_engine.graph
    )

@app.get("/api/v1/risk/recent")
def recent_risk_results(
    limit: int = 50,
) -> list[dict[str, object]]:
    if risk_engine is None:
        raise HTTPException(
            status_code=503,
            detail="risk engine unavailable",
        )

    limited = risk_engine.results[
        -limit:
    ]

    return [
        {
            "transaction_id": (
                result.transaction_id
            ),
            "risk_score": (
                result.probability
            ),
            "action": (
                result.action.value
            ),
            "evidence_count": len(
                result.evidence
            ),
        }
        for result in limited
    ]

@app.post("/api/v1/risk/score")
def score_transaction(
    transaction: Transaction,
) -> dict[str, object]:
    if risk_engine is None:
        raise HTTPException(
            status_code=503,
            detail="risk engine unavailable",
        )

    result = risk_engine.score(
        transaction
    )

    return {
        "transaction_id": (
            result.transaction_id
        ),
        "risk_score": (
            result.probability
        ),
        "action": (
            result.action.value
        ),
        "evidence": [
            {
                "type": (
                    evidence.evidence_type.value
                ),
                "severity": (
                    evidence.severity
                ),
                "message": (
                    evidence.message
                ),
                "value": (
                    evidence.value
                ),
            }
            for evidence in result.evidence
        ],
    }