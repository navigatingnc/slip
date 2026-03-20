"""Opportunity scorer for SLIP — converts FrictionPoints into ranked Opportunities."""
from typing import Dict, List
from .models import FrictionPoint, Opportunity

# Automation potential by pattern: how automatable is each friction type?
AUTOMATION_POTENTIAL: Dict[str, float] = {
    "delay": 0.8,
    "workaround": 0.9,
    "gap": 0.7,
    "cost": 0.5,
    "complaint": 0.4,
}

# Composite score weights
_W_FREQUENCY = 0.35
_W_SEVERITY = 0.40
_W_AUTOMATION = 0.25


def score(friction_points: List[FrictionPoint]) -> List[Opportunity]:
    """
    Group FrictionPoints by pattern and produce ranked Opportunity objects.

    Args:
        friction_points: List of FrictionPoint instances from detect().

    Returns:
        List of Opportunity objects sorted by composite_score descending.
    """
    if not friction_points:
        return []

    # Group by pattern
    groups: Dict[str, List[FrictionPoint]] = {}
    for fp in friction_points:
        groups.setdefault(fp.pattern, []).append(fp)

    total = len(friction_points)
    opportunities: List[Opportunity] = []

    for pattern, points in groups.items():
        frequency = min(1.0, len(points) / total)
        severity = sum(fp.score for fp in points) / len(points)
        automation = AUTOMATION_POTENTIAL.get(pattern, 0.5)
        composite = (
            _W_FREQUENCY * frequency
            + _W_SEVERITY * severity
            + _W_AUTOMATION * automation
        )
        opportunities.append(
            Opportunity(
                title=f"{pattern} reduction opportunity",
                friction_points=points,
                frequency=round(frequency, 3),
                severity=round(severity, 3),
                automation_potential=round(automation, 3),
                composite_score=round(composite, 3),
            )
        )

    return sorted(opportunities, key=lambda o: o.composite_score, reverse=True)
