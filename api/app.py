"""Local FastAPI application for SLIP — Phase 8 + Phase 12 + Phase 17 + Phase 21 + Phase 22 + Phase 24.

Exposes the full ingest → detect → score → report pipeline over HTTP via a
single POST /analyze endpoint, and a GET /reports endpoint that returns all
persisted SlipReports from the data/ directory. Run with:

    uvicorn api.app:app --reload
"""
import csv
import io
from collections import Counter
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from core.persistence import clear_reports, delete_report, load_report_by_id, load_reports, save_report
from core.report import generate_report

app = FastAPI(
    title="SLIP API",
    description="System for Locating and Identifying Points of friction — local API",
    version="0.24.0",
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


class SummaryResponse(BaseModel):
    total_reports: int
    total_signals: int
    total_friction: int
    top_patterns: List[str]
    top_opportunities: List[str]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", tags=["meta"])
def health() -> Dict[str, str]:
    """Liveness check."""
    return {"status": "ok", "service": "slip-api"}


@app.get("/reports/summary", response_model=SummaryResponse, tags=["reports"])
def get_reports_summary() -> SummaryResponse:
    """Return aggregate statistics across all persisted SlipReports.

    Aggregates total report count, total signals analysed, total friction
    points detected, the top-3 most frequent friction patterns, and the
    top-3 opportunities ranked by composite score across all reports.
    Returns zero counts and empty lists when no reports are persisted.
    """
    reports = load_reports()

    total_signals = sum(r.get("signal_count", 0) for r in reports)
    total_friction = sum(r.get("friction_count", 0) for r in reports)

    pattern_counter: Counter = Counter()
    opp_scores: Dict[str, float] = {}

    for r in reports:
        if r.get("top_pattern"):
            pattern_counter[r["top_pattern"]] += 1
        for opp in r.get("opportunities", []):
            title = opp.get("title", "")
            score = opp.get("composite_score", 0.0)
            if title and score > opp_scores.get(title, -1.0):
                opp_scores[title] = score

    top_patterns = [p for p, _ in pattern_counter.most_common(3)]
    top_opportunities = sorted(opp_scores, key=lambda t: opp_scores[t], reverse=True)[:3]

    return SummaryResponse(
        total_reports=len(reports),
        total_signals=total_signals,
        total_friction=total_friction,
        top_patterns=top_patterns,
        top_opportunities=top_opportunities,
    )


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


@app.get("/reports/{report_id}/export", tags=["reports"])
def export_report_csv(report_id: str) -> StreamingResponse:
    """Export the ranked opportunities of a persisted SlipReport as a CSV file.

    The report ID is the timestamp stem of the filename, e.g.
    ``20260327T002427Z`` for ``data/report_20260327T002427Z.json``.
    Returns 404 if no matching report is found.
    """
    from fastapi import HTTPException
    report = load_report_by_id(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found")

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "Title", "Composite Score", "Severity", "Frequency",
        "Automation Potential", "Willingness to Pay", "Market Size", "Signal Count",
    ])
    for opp in report.get("opportunities", []):
        writer.writerow([
            opp.get("title", ""),
            opp.get("composite_score", ""),
            opp.get("severity", ""),
            opp.get("frequency", ""),
            opp.get("automation_potential", ""),
            opp.get("willingness_to_pay", ""),
            opp.get("market_size", ""),
            opp.get("signal_count", ""),
        ])
    buf.seek(0)
    filename = f"slip_report_{report_id}.csv"
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


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
