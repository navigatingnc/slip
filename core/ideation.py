"""Business concept generator for SLIP — Phase 14.

Maps each Opportunity to a human-readable BusinessConcept, completing the
README pipeline:

    Signal → Pattern → Friction → Score → Opportunity → Business Concept

Concepts are generated from pattern-keyed templates — no LLM calls required,
keeping the system fully local-first.
"""
from dataclasses import dataclass
from typing import List

from .models import Opportunity


# ---------------------------------------------------------------------------
# Business concept templates keyed by friction pattern
# ---------------------------------------------------------------------------

_CONCEPTS: dict = {
    "delay": {
        "concept": "on-demand speed layer",
        "model": "SaaS / marketplace",
        "rationale": (
            "Delays signal unmet demand for faster turnaround. "
            "A platform that connects buyers with pre-vetted, fast-response "
            "providers can charge a premium for guaranteed speed."
        ),
    },
    "workaround": {
        "concept": "workflow automation tool",
        "model": "SaaS / API product",
        "rationale": (
            "Manual workarounds expose a missing feature or integration. "
            "Packaging the workaround as a polished tool captures the users "
            "already doing the work manually and willing to pay to stop."
        ),
    },
    "gap": {
        "concept": "niche marketplace or directory",
        "model": "marketplace / lead-gen",
        "rationale": (
            "Accessibility gaps mean buyers cannot find suitable providers. "
            "A curated directory or marketplace that surfaces hard-to-find "
            "options earns trust and transaction fees."
        ),
    },
    "cost": {
        "concept": "transparent pricing platform",
        "model": "comparison / affiliate",
        "rationale": (
            "Pricing frustration drives churn and distrust. "
            "A comparison tool or price-transparency layer builds loyalty "
            "and earns referral revenue from lower-cost alternatives."
        ),
    },
    "complaint": {
        "concept": "quality assurance service",
        "model": "subscription / consulting",
        "rationale": (
            "Repeated complaints indicate a quality or reliability gap. "
            "A vetting, review aggregation, or managed-service layer "
            "commands a premium from buyers who want guaranteed outcomes."
        ),
    },
}

_DEFAULT_CONCEPT = {
    "concept": "friction-removal service",
    "model": "service / SaaS",
    "rationale": (
        "Any recurring friction point represents a monetisable gap. "
        "A targeted service that removes this specific pain can build "
        "a loyal customer base willing to pay for relief."
    ),
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@dataclass
class BusinessConcept:
    """A human-readable business idea derived from a single Opportunity."""

    opportunity_title: str   # source opportunity label
    concept: str             # short business concept name
    model: str               # business model (e.g. SaaS, marketplace)
    rationale: str           # one-paragraph justification

    def to_dict(self) -> dict:
        return {
            "opportunity_title": self.opportunity_title,
            "concept": self.concept,
            "model": self.model,
            "rationale": self.rationale,
        }

    def __repr__(self) -> str:
        return (
            f"BusinessConcept(concept={self.concept!r}, "
            f"model={self.model!r}, "
            f"opportunity={self.opportunity_title!r})"
        )


def generate_concepts(opportunities: List[Opportunity]) -> List[BusinessConcept]:
    """Map each Opportunity to a BusinessConcept.

    Args:
        opportunities: Ranked list of Opportunity objects from score().

    Returns:
        List of BusinessConcept objects in the same order as the input.
    """
    concepts: List[BusinessConcept] = []
    for opp in opportunities:
        pattern = opp.title.split()[0]  # e.g. "delay" from "delay reduction opportunity"
        template = _CONCEPTS.get(pattern, _DEFAULT_CONCEPT)
        concepts.append(
            BusinessConcept(
                opportunity_title=opp.title,
                concept=template["concept"],
                model=template["model"],
                rationale=template["rationale"],
            )
        )
    return concepts
