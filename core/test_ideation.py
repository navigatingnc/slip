"""Tests for the ideation module — Phase 14 + Phase 16."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.models import FrictionPoint, Opportunity
from unittest.mock import MagicMock, patch

from core.ideation import BusinessConcept, enrich_concept, generate_concepts


def _make_opportunity(pattern: str) -> Opportunity:
    fp = FrictionPoint(description="test signal", pattern=pattern, score=0.5)
    return Opportunity(
        title=f"{pattern} reduction opportunity",
        friction_points=[fp],
        frequency=1.0,
        severity=0.5,
        automation_potential=0.7,
        willingness_to_pay=0.6,
        market_size=0.7,
        composite_score=0.62,
    )


def test_generate_concepts_returns_list():
    opps = [_make_opportunity("delay")]
    result = generate_concepts(opps)
    assert isinstance(result, list)
    assert len(result) == 1


def test_generate_concepts_returns_business_concept_instances():
    opps = [_make_opportunity("workaround")]
    result = generate_concepts(opps)
    assert isinstance(result[0], BusinessConcept)


def test_generate_concepts_maps_all_known_patterns():
    patterns = ["delay", "workaround", "gap", "cost", "complaint"]
    opps = [_make_opportunity(p) for p in patterns]
    result = generate_concepts(opps)
    assert len(result) == len(patterns)
    for bc in result:
        assert bc.concept != ""
        assert bc.model != ""
        assert bc.rationale != ""


def test_generate_concepts_unknown_pattern_uses_default():
    fp = FrictionPoint(description="weird signal", pattern="unknown_pattern", score=0.3)
    opp = Opportunity(
        title="unknown_pattern reduction opportunity",
        friction_points=[fp],
        frequency=1.0,
        severity=0.3,
        automation_potential=0.5,
        willingness_to_pay=0.5,
        market_size=0.5,
        composite_score=0.46,
    )
    result = generate_concepts([opp])
    assert result[0].concept == "friction-removal service"


def test_generate_concepts_preserves_order():
    patterns = ["gap", "delay", "cost"]
    opps = [_make_opportunity(p) for p in patterns]
    result = generate_concepts(opps)
    for i, bc in enumerate(result):
        assert bc.opportunity_title == opps[i].title


def test_generate_concepts_empty_input():
    assert generate_concepts([]) == []


def test_business_concept_to_dict_keys():
    bc = generate_concepts([_make_opportunity("delay")])[0]
    d = bc.to_dict()
    assert set(d.keys()) == {"opportunity_title", "concept", "model", "rationale"}


def test_business_concept_opportunity_title_matches():
    opp = _make_opportunity("gap")
    bc = generate_concepts([opp])[0]
    assert bc.opportunity_title == opp.title


# ---------------------------------------------------------------------------
# Phase 16: enrich_concept tests
# ---------------------------------------------------------------------------

def test_enrich_concept_noop_without_api_key(monkeypatch):
    """enrich_concept must not alter rationale when SLIP_OPENAI_API_KEY is unset."""
    monkeypatch.delenv("SLIP_OPENAI_API_KEY", raising=False)
    bc = BusinessConcept(
        opportunity_title="delay reduction opportunity",
        concept="on-demand speed layer",
        model="SaaS / marketplace",
        rationale="original rationale",
    )
    enrich_concept(bc)
    assert bc.rationale == "original rationale"


def test_enrich_concept_updates_rationale_when_llm_responds(monkeypatch):
    """enrich_concept must replace rationale with LLM output when key is set."""
    monkeypatch.setenv("SLIP_OPENAI_API_KEY", "test-key")
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "LLM-generated rationale."
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    with patch("openai.OpenAI", return_value=mock_client):
        bc = BusinessConcept(
            opportunity_title="delay reduction opportunity",
            concept="on-demand speed layer",
            model="SaaS / marketplace",
            rationale="original rationale",
        )
        enrich_concept(bc)
    assert bc.rationale == "LLM-generated rationale."


def test_enrich_concept_falls_back_on_llm_exception(monkeypatch):
    """enrich_concept must keep original rationale when the LLM call raises."""
    monkeypatch.setenv("SLIP_OPENAI_API_KEY", "test-key")
    with patch("openai.OpenAI", side_effect=RuntimeError("network error")):
        bc = BusinessConcept(
            opportunity_title="gap reduction opportunity",
            concept="niche marketplace",
            model="marketplace / lead-gen",
            rationale="original rationale",
        )
        enrich_concept(bc)
    assert bc.rationale == "original rationale"


def test_generate_concepts_calls_enrich_for_each_opportunity(monkeypatch):
    """generate_concepts must call enrich_concept once per opportunity."""
    monkeypatch.delenv("SLIP_OPENAI_API_KEY", raising=False)
    call_count = []

    def fake_enrich(concept):
        call_count.append(1)

    with patch("core.ideation.enrich_concept", side_effect=fake_enrich):
        opps = [_make_opportunity(p) for p in ["delay", "gap", "cost"]]
        generate_concepts(opps)

    assert len(call_count) == 3
