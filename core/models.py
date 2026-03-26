"""Core data models for SLIP friction detection."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class FrictionPoint:
    """Represents a single detected point of friction in a workflow or signal."""

    description: str
    pattern: str  # e.g. "delay", "complaint", "workaround", "cost", "gap"
    source: Optional[str] = None  # origin of the signal (e.g. "reddit", "review")
    score: float = 0.0  # impact score 0.0–1.0
    tags: list = field(default_factory=list)

    def __repr__(self) -> str:
        return (
            f"FrictionPoint(pattern={self.pattern!r}, "
            f"score={self.score:.2f}, description={self.description!r})"
        )


@dataclass
class Opportunity:
    """A ranked business or automation opportunity derived from friction points.

    Scored across all five dimensions defined in the README:
    Frequency, Severity, Willingness to Pay, Market Size, Automation Potential.
    """
    title: str                              # short label, e.g. "rapid quoting system"
    friction_points: List[FrictionPoint]  # source signals
    frequency: float = 0.0                  # 0.0–1.0: how often the pattern appears
    severity: float = 0.0                   # 0.0–1.0: average friction score
    automation_potential: float = 0.0       # 0.0–1.0: ease of automation
    willingness_to_pay: float = 0.0         # 0.0–1.0: likelihood users pay to fix it
    market_size: float = 0.0               # 0.0–1.0: estimated breadth of the problem
    composite_score: float = 0.0            # weighted aggregate across all five dims

    def __repr__(self) -> str:
        return (
            f"Opportunity(title={self.title!r}, "
            f"composite_score={self.composite_score:.2f}, "
            f"signals={len(self.friction_points)})"
        )
