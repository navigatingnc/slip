"""Opportunity scorer for SLIP — converts FrictionPoints into ranked Opportunities.

Phase 13: extended to all five README scoring dimensions:
  Frequency, Severity, Willingness to Pay, Market Size, Automation Potential.
"""
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

# Willingness to pay: how likely are users to pay for a solution?
WILLINGNESS_TO_PAY: Dict[str, float] = {
    "delay": 0.7,
    "workaround": 0.8,
    "gap": 0.9,
    "cost": 0.6,
    "complaint": 0.3,
}

# Market size: estimated breadth of the problem across the general population
MARKET_SIZE: Dict[str, float] = {
    "delay": 0.8,
    "workaround": 0.7,
    "gap": 0.9,
    "cost": 0.8,
    "complaint": 0.5,
}

# Equal weights across all five dimensions (sum = 1.0)
_W_FREQUENCY = 0.20
_W_SEVERITY = 0.20
_W_AUTOMATION = 0.20
_W_WILLINGNESS = 0.20
_W_MARKET = 0.20


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
        willingness = WILLINGNESS_TO_PAY.get(pattern, 0.5)
        market = MARKET_SIZE.get(pattern, 0.5)
        composite = (
            _W_FREQUENCY * frequency
            + _W_SEVERITY * severity
            + _W_AUTOMATION * automation
            + _W_WILLINGNESS * willingness
            + _W_MARKET * market
        )
        opportunities.append(
            Opportunity(
                title=f"{pattern} reduction opportunity",
                friction_points=points,
                frequency=round(frequency, 3),
                severity=round(severity, 3),
                automation_potential=round(automation, 3),
                willingness_to_pay=round(willingness, 3),
                market_size=round(market, 3),
                composite_score=round(composite, 3),
            )
        )

    return sorted(opportunities, key=lambda o: o.composite_score, reverse=True)
