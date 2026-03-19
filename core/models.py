"""Core data models for SLIP friction detection."""

from dataclasses import dataclass, field
from typing import Optional


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
