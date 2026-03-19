"""Core friction detection logic for SLIP."""

from typing import List
from .models import FrictionPoint

# Keyword patterns mapped to friction type labels
FRICTION_PATTERNS: dict = {
    "delay": [
        "takes too long", "slow", "waiting", "weeks to get", "delayed",
        "never responds", "no reply", "backlog",
    ],
    "complaint": [
        "frustrated", "annoying", "terrible", "broken", "hate", "awful",
        "worst", "useless", "disappointing",
    ],
    "workaround": [
        "had to hack", "workaround", "manually", "spreadsheet instead",
        "copy paste", "export and re-import", "duct tape",
    ],
    "cost": [
        "too expensive", "overpriced", "hidden fee", "charged extra",
        "not worth the price", "billing issue",
    ],
    "gap": [
        "no way to", "can't find", "doesn't exist", "wish there was",
        "nobody offers", "impossible to", "hard to access",
    ],
}


def detect(text: str, source: str = "unknown") -> List[FrictionPoint]:
    """
    Scan a text signal for friction patterns.

    Args:
        text: Raw input text to analyze.
        source: Origin label for the signal (e.g. "reddit", "review").

    Returns:
        List of FrictionPoint instances found in the text.
    """
    text_lower = text.lower()
    found: List[FrictionPoint] = []

    for pattern, keywords in FRICTION_PATTERNS.items():
        matched = [kw for kw in keywords if kw in text_lower]
        if matched:
            score = min(1.0, len(matched) * 0.25)
            found.append(
                FrictionPoint(
                    description=text.strip(),
                    pattern=pattern,
                    source=source,
                    score=score,
                    tags=matched,
                )
            )

    return found
