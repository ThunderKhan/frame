import csv
from io import StringIO
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from frame.analysis.catalog import DATASET_CATALOG as BASE_DATASET_CATALOG
from frame.analysis.catalog_extra import EXTRA_DATASET_CATALOG
from frame.analysis.service import AnalysisMapping, EntityColumn, analyze_csv
from frame.evaluation.worlds import build_hard_negative_world

DATASET_CATALOG = BASE_DATASET_CATALOG + EXTRA_DATASET_CATALOG

CATALOG_BY_ID = {dataset["id"]: dataset for dataset in DATASET_CATALOG}

router = APIRouter(
    prefix="/api/v1",
    tags=["dataset-analysis"],
)


class EntityMappingRequest(BaseModel):
    column: str
    type: str


class DatasetMappingRequest(BaseModel):
    entities: list[EntityMappingRequest] = Field(default_factory=list)
    transaction_id: str | None = None
    timestamp: str | None = None
    amount: str | None = None
    label: str | None = None


class DatasetAnalysisRequest(BaseModel):
    dataset_id: str = "custom"
    filename: str
    csv_text: str
    mapping: DatasetMappingRequest | None = None
    row_limit: int = Field(
        default=5000,
        ge=1,
        le=10000,
    )


def _mapping_from_payload(
    request: DatasetAnalysisRequest,
) -> AnalysisMapping:
    mapping_payload: dict[str, Any] | None

    if request.mapping is not None:
        mapping_payload = request.mapping.model_dump()
    else:
        profile = CATALOG_BY_ID.get(request.dataset_id)
        mapping_payload = profile.get("default_mapping") if profile is not None else None

    if not mapping_payload:
        raise HTTPException(
            status_code=422,
            detail=(
                "this dataset needs an explicit schema mapping before FRAME can analyze it"
            ),
        )

    entities = tuple(
        EntityColumn(
            column=entity["column"],
            entity_type=entity["type"],
        )
        for entity in mapping_payload.get("entities", [])
    )

    return AnalysisMapping(
        entities=entities,
        transaction_id=mapping_payload.get("transaction_id"),
        timestamp=mapping_payload.get("timestamp"),
        amount=mapping_payload.get("amount"),
        label=mapping_payload.get("label"),
    )


def _frame_benchmark_csv() -> str:
    world = build_hard_negative_world(
        legitimate_count=240,
        ring_count=3,
        ring_size=5,
        transactions_per_account=4,
        seed=2026,
    )

    stream = StringIO()
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(
        [
            "transaction_id",
            "customer_id",
            "merchant_id",
            "device_id",
            "card_id",
            "ip_id",
            "amount",
            "timestamp",
            "account_age_days",
            "is_fraud",
            "fraud_ring_id",
        ]
    )

    for transaction in world.transactions:
        writer.writerow(
            [
                transaction.transaction_id,
                transaction.customer_id,
                transaction.merchant_id,
                transaction.device_id,
                transaction.card_id,
                transaction.ip_id,
                transaction.amount,
                transaction.timestamp.isoformat(),
                transaction.account_age_days,
                int(transaction.is_fraud),
                transaction.fraud_ring_id or "",
            ]
        )

    return stream.getvalue()


def _attach_stream_to_graph(result: dict[str, Any]) -> dict[str, Any]:
    graph = result.get("graph")
    stream_events = result.get("stream_events")

    if isinstance(graph, dict) and isinstance(stream_events, list):
        graph["stream_events"] = stream_events
        graph["analysis_id"] = result.get("analysis_id")

    return result


@router.get("/datasets")
def list_datasets() -> dict[str, object]:
    return {
        "datasets": list(DATASET_CATALOG),
        "count": len(DATASET_CATALOG),
        "upload_limits": {
            "max_csv_mb": 5,
            "max_rows": 10000,
        },
    }


@router.post("/analysis/builtin/{dataset_id}")
def analyze_builtin_dataset(
    dataset_id: str,
) -> dict[str, Any]:
    if dataset_id != "frame-benchmark":
        raise HTTPException(
            status_code=404,
            detail="built-in dataset not found",
        )

    profile = CATALOG_BY_ID[dataset_id]
    mapping_payload = profile["default_mapping"]
    assert mapping_payload is not None

    mapping = AnalysisMapping(
        entities=tuple(
            EntityColumn(
                column=entity["column"],
                entity_type=entity["type"],
            )
            for entity in mapping_payload["entities"]
        ),
        transaction_id=mapping_payload.get("transaction_id"),
        timestamp=mapping_payload.get("timestamp"),
        amount=mapping_payload.get("amount"),
        label=mapping_payload.get("label"),
    )

    try:
        return _attach_stream_to_graph(
            analyze_csv(
                dataset_id=dataset_id,
                filename="frame-ring-benchmark.csv",
                csv_text=_frame_benchmark_csv(),
                mapping=mapping,
                row_limit=5000,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


@router.post("/analysis/dataset")
def analyze_dataset(
    request: DatasetAnalysisRequest,
) -> dict[str, Any]:
    mapping = _mapping_from_payload(request)

    try:
        return _attach_stream_to_graph(
            analyze_csv(
                dataset_id=request.dataset_id,
                filename=request.filename,
                csv_text=request.csv_text,
                mapping=mapping,
                row_limit=request.row_limit,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
