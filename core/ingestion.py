"""Signal ingestion module for SLIP — Phase 6.

Normalises raw text signals from named sources into Signal objects and
feeds them through the core detect() pipeline, producing FrictionPoints.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any

from .detector import detect
from .models import FrictionPoint


@dataclass
class Signal:
    """A normalised input signal before friction analysis."""

    text: str
    source: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.text, str):
            raise TypeError(f"Signal.text must be str, got {type(self.text).__name__}")
        self.text = self.text.strip()

    def __repr__(self) -> str:
        preview = self.text[:60] + ("..." if len(self.text) > 60 else "")
        return f"Signal(source={self.source!r}, text={preview!r})"


def normalise(raw: Dict[str, Any]) -> Signal:
    """Convert a raw dict with 'text' and optional 'source' into a Signal."""
    text = raw.get("text", "")
    source = raw.get("source", "unknown")
    metadata = {k: v for k, v in raw.items() if k not in ("text", "source")}
    return Signal(text=str(text), source=str(source), metadata=metadata)


def ingest(raw_signals: List[Dict[str, Any]]) -> List[FrictionPoint]:
    """Normalise a list of raw signal dicts and run friction detection on each.

    Args:
        raw_signals: List of dicts, each containing at minimum a 'text' key
                     and an optional 'source' key.

    Returns:
        Flat list of FrictionPoint objects detected across all signals.
    """
    friction_points: List[FrictionPoint] = []
    for raw in raw_signals:
        signal = normalise(raw)
        if signal.text:
            friction_points.extend(detect(signal.text, source=signal.source))
    return friction_points
