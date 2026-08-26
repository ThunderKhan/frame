from fastapi import FastAPI

app = FastAPI(
    title="FRAME Risk API",
    version="0.1.0",
    description=(
        "Explainable graph intelligence "
        "for coordinated payment abuse."
    ),
)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "frame-risk-api",
    }