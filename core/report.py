"""Report generator for SLIP — Phase 7.

Assembles the full ingest → detect → score pipeline output into a structured
SlipReport dataclass that is serialisable to a plain dict (JSON-ready).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .ideation import generate_concepts
from .ingestion import ingest
from .models import Opportunity
from .scorer import score


@dataclass
class SlipReport:
    """Structured summary of a batch signal analysis run."""

    signal_count: int
    friction_count: int
    opportunities: List[Opportunity]
    top_pattern: Optional[str]
    top_opportunity: Optional[str]
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serialisable representation of the report."""
        concepts = generate_concepts(self.opportunities)
        concept_map = {bc.opportunity_title: bc.to_dict() for bc in concepts}
        return {
            "generated_at": self.generated_at,
            "signal_count": self.signal_count,
            "friction_count": self.friction_count,
            "top_pattern": self.top_pattern,
            "top_opportunity": self.top_opportunity,
            "opportunities": [
                {
                    "title": opp.title,
                    "composite_score": opp.composite_score,
                    "severity": opp.severity,
                    "frequency": opp.frequency,
                    "automation_potential": opp.automation_potential,
                    "willingness_to_pay": opp.willingness_to_pay,
                    "market_size": opp.market_size,
                    "signal_count": len(opp.friction_points),
                    "business_concept": concept_map.get(opp.title),
                }
                for opp in self.opportunities
            ],
        }

    def __repr__(self) -> str:
        return (
            f"SlipReport(signals={self.signal_count}, "
            f"friction={self.friction_count}, "
            f"opportunities={len(self.opportunities)}, "
            f"top={self.top_opportunity!r})"
        )


def generate_report(raw_signals: List[Dict[str, Any]]) -> SlipReport:
    """Run the full ingest → detect → score pipeline and return a SlipReport.

    Args:
        raw_signals: List of dicts with 'text' and optional 'source' keys.

    Returns:
        A SlipReport summarising all detected friction and ranked opportunities.
    """
    friction_points = ingest(raw_signals)
    opportunities = score(friction_points)

    top_pattern: Optional[str] = None
    top_opportunity: Optional[str] = None

    if friction_points:
        # Most frequent pattern across all detected friction points
        pattern_counts: Dict[str, int] = {}
        for fp in friction_points:
            pattern_counts[fp.pattern] = pattern_counts.get(fp.pattern, 0) + 1
        top_pattern = max(pattern_counts, key=lambda p: pattern_counts[p])

    if opportunities:
        top_opportunity = opportunities[0].title

    return SlipReport(
        signal_count=len(raw_signals),
        friction_count=len(friction_points),
        opportunities=opportunities,
        top_pattern=top_pattern,
        top_opportunity=top_opportunity,
    )
