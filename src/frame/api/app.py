from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    HTTPException,
    Query,
)
from fastapi.middleware.cors import CORSMiddleware

from frame.api.graph import (
    serialize_graph,
)
from frame.api.runtime import (
    build_risk_engine,
)
from frame.api.schemas import (
    RiskScoreRequest,
)
from frame.domain.transaction import (
    Transaction,
)
from frame.risk.engine import RiskEngine
from frame.risk.result import RiskResult

risk_engine: RiskEngine | None = None

DEFAULT_CORS_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://frame-risk.vercel.app",
)


def cors_origins() -> list[str]:
    configured = os.getenv(
        "FRAME_CORS_ORIGINS",
        "",
    ).strip()

    origins = {
        origin.rstrip("/")
        for origin in DEFAULT_CORS_ORIGINS
    }

    if configured:
        origins.update(
            origin.strip().rstrip("/")
            for origin in configured.split(",")
            if origin.strip()
        )

    return sorted(origins)


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


app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def require_engine() -> RiskEngine:
    if risk_engine is None:
        raise HTTPException(
            status_code=503,
            detail="risk engine unavailable",
        )

    return risk_engine


def serialize_evidence(
    result: RiskResult,
) -> list[dict[str, object]]:
    return [
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
    ]


def serialize_entities(
    transaction: Transaction,
) -> dict[str, str]:
    return {
        "customer": (
            transaction.customer_id
        ),
        "device": (
            transaction.device_id
        ),
        "ip": (
            transaction.ip_id
        ),
        "card": (
            transaction.card_id
        ),
        "merchant": (
            transaction.merchant_id
        ),
    }


def serialize_risk_detail(
    result: RiskResult,
    transaction: Transaction | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
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
        "evidence": serialize_evidence(
            result
        ),
    }

    if transaction is not None:
        payload["entities"] = (
            serialize_entities(
                transaction
            )
        )

    return payload


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "frame-risk-api",
    }


@app.get("/api/v1/stats")
def get_stats() -> dict[str, object]:
    engine = require_engine()

    results = engine.snapshot_results()
    graph = engine.snapshot_graph()

    allowed = sum(
        result.action.value == "ALLOW"
        for result in results
    )

    reviewed = sum(
        result.action.value == "REVIEW"
        for result in results
    )

    blocked = sum(
        result.action.value == "BLOCK"
        for result in results
    )

    average_risk = (
        sum(
            result.probability
            for result in results
        )
        / len(results)
        if results
        else 0.0
    )

    return {
        "transactions_scored": (
            len(results)
        ),
        "allowed": allowed,
        "reviewed": reviewed,
        "blocked": blocked,
        "average_risk_score": (
            average_risk
        ),
        "graph_nodes": (
            graph.number_of_nodes()
        ),
        "graph_edges": (
            graph.number_of_edges()
        ),
    }


@app.get("/api/v1/graph")
def get_graph() -> dict[
    str,
    list[dict[str, object]],
]:
    engine = require_engine()

    graph = engine.snapshot_graph()

    return serialize_graph(
        graph
    )


@app.get("/api/v1/risk/recent")
def recent_risk_results(
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
) -> list[dict[str, object]]:
    engine = require_engine()

    results = engine.snapshot_results()

    limited = results[
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


@app.get(
    "/api/v1/risk/{transaction_id}"
)
def get_risk_result(
    transaction_id: str,
) -> dict[str, object]:
    engine = require_engine()

    result = engine.get_result(
        transaction_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "risk result not found"
            ),
        )

    transaction = (
        engine.get_transaction(
            transaction_id
        )
    )

    return serialize_risk_detail(
        result,
        transaction,
    )


@app.post("/api/v1/demo/reset")
def reset_demo() -> dict[str, str]:
    global risk_engine

    risk_engine = build_risk_engine()

    return {
        "status": "ok",
        "message": "demo state reset",
    }


@app.post("/api/v1/risk/score")
def score_transaction(
    request: RiskScoreRequest,
) -> dict[str, object]:
    engine = require_engine()

    transaction = (
        request.to_transaction()
    )

    try:
        result = engine.score(
            transaction
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    return serialize_risk_detail(
        result,
        transaction,
    )
