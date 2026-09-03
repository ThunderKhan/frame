from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from frame.analysis.catalog import CATALOG_BY_ID, DATASET_CATALOG
from frame.analysis.service import AnalysisMapping, EntityColumn, analyze_csv


router = APIRouter(prefix="/api/v1", tags=["dataset-analysis"])


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
    row_limit: int = Field(default=5000, ge=1, le=10000)


def _mapping_from_payload(
    request: DatasetAnalysisRequest,
) -> AnalysisMapping:
    mapping_payload: dict[str, Any] | None

    if request.mapping is not None:
        mapping_payload = request.mapping.model_dump()
    else:
        profile = CATALOG_BY_ID.get(request.dataset_id)
        mapping_payload = (
            profile.get("default_mapping")
            if profile is not None
            else None
        )

    if not mapping_payload:
        raise HTTPException(
            status_code=422,
            detail=(
                "this dataset needs an explicit schema mapping before FRAME can "
                "analyze it"
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


@router.post("/analysis/dataset")
def analyze_dataset(
    request: DatasetAnalysisRequest,
) -> dict[str, Any]:
    mapping = _mapping_from_payload(request)

    try:
        return analyze_csv(
            dataset_id=request.dataset_id,
            filename=request.filename,
            csv_text=request.csv_text,
            mapping=mapping,
            row_limit=request.row_limit,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
