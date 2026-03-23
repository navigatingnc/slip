"""SlipAgent — OpenClaw-compatible agent wrapper for SLIP (Phase 9).

Exposes the three methods defined in the README's OpenClaw integration spec:

    agent = SlipAgent()
    report   = agent.analyze(signals)        # ingest → detect → score → report
    opps     = agent.suggest(friction_points) # score → ranked opportunities
    plan     = agent.execute(opportunity)     # opportunity → execution plan
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.ingestion import ingest
from core.models import FrictionPoint, Opportunity
from core.report import SlipReport, generate_report
from core.scorer import score

# Action templates keyed by friction pattern
_ACTION_TEMPLATES: Dict[str, List[str]] = {
    "delay": [
        "Map the current process steps and identify the longest wait",
        "Introduce async handling or queuing to remove the bottleneck",
        "Set SLA targets and alert when thresholds are breached",
    ],
    "workaround": [
        "Document the workaround to understand the missing capability",
        "Build or integrate a native solution that replaces the hack",
        "Deprecate the workaround once the native solution is validated",
    ],
    "cost": [
        "Audit the cost structure and identify the largest line items",
        "Benchmark against alternatives and negotiate or switch providers",
        "Introduce tiered pricing or usage caps to control spend",
    ],
    "complaint": [
        "Aggregate complaint signals to find the highest-frequency pain point",
        "Prioritise a fix for the top complaint in the next sprint",
        "Add a feedback loop so users can confirm the issue is resolved",
    ],
    "gap": [
        "Define the missing capability as a product requirement",
        "Prototype the simplest solution that closes the gap",
        "Validate demand before investing in a full build",
    ],
}

_DEFAULT_ACTIONS = [
    "Investigate the friction signal in more detail",
    "Quantify the impact and estimate effort to resolve",
    "Propose a targeted improvement and measure outcome",
]


class SlipAgent:
    """Stateful OpenClaw-compatible agent wrapping the SLIP core pipeline.

    Maintains a session log of all analyses run so results can be
    inspected or replayed without re-running the pipeline.
    """

    def __init__(self, source: str = "agent") -> None:
        self.source = source
        self._history: List[SlipReport] = []

    # ------------------------------------------------------------------
    # Public API (mirrors README OpenClaw spec)
    # ------------------------------------------------------------------

    def analyze(self, signals: List[Dict[str, Any]]) -> SlipReport:
        """Run the full ingest → detect → score → report pipeline.

        Args:
            signals: List of raw signal dicts with 'text' and optional 'source'.

        Returns:
            SlipReport summarising all detected friction and ranked opportunities.
        """
        # Stamp each signal with the agent source if none provided
        stamped = [
            s if "source" in s else {**s, "source": self.source}
            for s in signals
        ]
        report = generate_report(stamped)
        self._history.append(report)
        return report

    def suggest(self, friction_points: List[FrictionPoint]) -> List[Opportunity]:
        """Convert a list of FrictionPoints into ranked Opportunities.

        Args:
            friction_points: FrictionPoint objects from core.detect() or ingest().

        Returns:
            List of Opportunity objects sorted by composite_score descending.
        """
        return score(friction_points)

    def execute(self, opportunity: Opportunity) -> Dict[str, Any]:
        """Produce an agent-ready execution plan for a given Opportunity.

        Args:
            opportunity: An Opportunity object from suggest() or analyze().

        Returns:
            Dict with keys: opportunity, actions, priority, automation_potential.
        """
        pattern = opportunity.title.split()[0]  # e.g. "delay" from "delay reduction..."
        actions = _ACTION_TEMPLATES.get(pattern, _DEFAULT_ACTIONS)

        priority = (
            "high" if opportunity.composite_score >= 0.6
            else "medium" if opportunity.composite_score >= 0.4
            else "low"
        )

        return {
            "opportunity": opportunity.title,
            "composite_score": opportunity.composite_score,
            "priority": priority,
            "automation_potential": opportunity.automation_potential,
            "actions": actions,
        }

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------

    @property
    def history(self) -> List[SlipReport]:
        """All SlipReports produced by this agent instance."""
        return list(self._history)

    def reset(self) -> None:
        """Clear the session history."""
        self._history.clear()

    def __repr__(self) -> str:
        return f"SlipAgent(source={self.source!r}, analyses={len(self._history)})"
