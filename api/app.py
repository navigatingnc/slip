"""Local FastAPI application for SLIP — Phase 8.

Exposes the full ingest → detect → score → report pipeline over HTTP via a
single POST /analyze endpoint. Run with:

    uvicorn api.app:app --reload
"""
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

from core.report import generate_report

app = FastAPI(
    title="SLIP API",
    description="System for Locating and Identifying Points of friction — local API",
    version="0.8.0",
)


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class SignalInput(BaseModel):
    text: str = Field(..., description="Raw text signal to analyse")
    source: str = Field("api", description="Origin label for the signal")

    model_config = {"extra": "allow"}  # pass-through metadata fields


class AnalyzeRequest(BaseModel):
    signals: List[SignalInput] = Field(
        ..., min_length=1, description="One or more signals to analyse"
    )


class OpportunityOut(BaseModel):
    title: str
    composite_score: float
    severity: float
    frequency: float
    automation_potential: float
    signal_count: int


class AnalyzeResponse(BaseModel):
    generated_at: str
    signal_count: int
    friction_count: int
    top_pattern: Optional[str]
    top_opportunity: Optional[str]
    opportunities: List[OpportunityOut]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", tags=["meta"])
def health() -> Dict[str, str]:
    """Liveness check."""
    return {"status": "ok", "service": "slip-api"}


@app.post("/analyze", response_model=AnalyzeResponse, tags=["analysis"])
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """Run the full SLIP pipeline on a batch of signals and return a report."""
    raw_signals: List[Dict[str, Any]] = [s.model_dump() for s in request.signals]
    report = generate_report(raw_signals)
    return AnalyzeResponse(**report.to_dict())
