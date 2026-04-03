"""Local FastAPI application for SLIP — Phase 8 + Phase 12 + Phase 17 + Phase 21.

Exposes the full ingest → detect → score → report pipeline over HTTP via a
single POST /analyze endpoint, and a GET /reports endpoint that returns all
persisted SlipReports from the data/ directory. Run with:

    uvicorn api.app:app --reload
"""
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

from core.persistence import clear_reports, delete_report, load_report_by_id, load_reports, save_report
from core.report import generate_report

app = FastAPI(
    title="SLIP API",
    description="System for Locating and Identifying Points of friction — local API",
    version="0.21.0",
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


class BusinessConceptOut(BaseModel):
    opportunity_title: str
    concept: str
    model: str
    rationale: str


class OpportunityOut(BaseModel):
    title: str
    composite_score: float
    severity: float
    frequency: float
    automation_potential: float
    willingness_to_pay: float
    market_size: float
    signal_count: int
    business_concept: Optional[BusinessConceptOut] = None


class AnalyzeResponse(BaseModel):
    generated_at: str
    signal_count: int
    friction_count: int
    top_pattern: Optional[str]
    top_opportunity: Optional[str]
    opportunities: List[OpportunityOut]


class ReportsResponse(BaseModel):
    count: int
    reports: List[Dict[str, Any]]


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
    save_report(report)
    return AnalyzeResponse(**report.to_dict())


@app.get("/reports", response_model=ReportsResponse, tags=["reports"])
def get_reports() -> ReportsResponse:
    """Return all persisted SlipReports from the data/ directory, oldest first."""
    reports = load_reports()
    return ReportsResponse(count=len(reports), reports=reports)


@app.get("/reports/{report_id}", tags=["reports"])
def get_report_by_id(report_id: str) -> Dict[str, Any]:
    """Return a single persisted SlipReport by its ID.

    The report ID is the timestamp stem of the filename, e.g.
    ``20260327T002427Z`` for ``data/report_20260327T002427Z.json``.
    Returns 404 if no matching report is found.
    """
    from fastapi import HTTPException
    report = load_report_by_id(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found")
    return report


@app.delete("/reports", tags=["reports"])
def delete_all_reports() -> Dict[str, int]:
    """Delete all persisted SlipReports from the data/ directory.

    Returns a JSON object with the count of deleted reports.
    """
    count = clear_reports()
    return {"deleted": count}


@app.delete("/reports/{report_id}", status_code=204, tags=["reports"])
def delete_report_by_id(report_id: str) -> None:
    """Delete a single persisted SlipReport by its ID.

    The report ID is the timestamp stem of the filename, e.g.
    ``20260327T002427Z`` for ``data/report_20260327T002427Z.json``.
    Returns 204 No Content on success, 404 if no matching report is found.
    """
    from fastapi import HTTPException
    deleted = delete_report(report_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found")
