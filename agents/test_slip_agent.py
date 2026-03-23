"""Tests for SlipAgent — OpenClaw-compatible agent layer (Phase 9)."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.slip_agent import SlipAgent
from core.models import FrictionPoint, Opportunity
from core.report import SlipReport

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_SIGNALS = [
    {"text": "It takes too long to get a quote.", "source": "reddit"},
    {"text": "I had to hack a workaround for the billing system.", "source": "forum"},
    {"text": "Too expensive and nobody offers a cheaper option.", "source": "review"},
]

_CLEAN_SIGNALS = [{"text": "Everything works perfectly.", "source": "survey"}]


def _make_fp(pattern: str, score: float = 0.5) -> FrictionPoint:
    return FrictionPoint(description="test signal", pattern=pattern, score=score)


def _make_opp(pattern: str, score: float = 0.6) -> Opportunity:
    return Opportunity(
        title=f"{pattern} reduction opportunity",
        friction_points=[_make_fp(pattern)],
        composite_score=score,
        automation_potential=0.8,
    )


# ---------------------------------------------------------------------------
# SlipAgent instantiation
# ---------------------------------------------------------------------------

def test_agent_default_source():
    agent = SlipAgent()
    assert agent.source == "agent"


def test_agent_custom_source():
    agent = SlipAgent(source="openclaw")
    assert agent.source == "openclaw"


def test_agent_repr():
    agent = SlipAgent()
    assert "SlipAgent" in repr(agent)
    assert "analyses=0" in repr(agent)


# ---------------------------------------------------------------------------
# analyze()
# ---------------------------------------------------------------------------

def test_analyze_returns_slip_report():
    agent = SlipAgent()
    report = agent.analyze(_SIGNALS)
    assert isinstance(report, SlipReport)


def test_analyze_signal_count():
    agent = SlipAgent()
    report = agent.analyze(_SIGNALS)
    assert report.signal_count == len(_SIGNALS)


def test_analyze_detects_friction():
    agent = SlipAgent()
    report = agent.analyze(_SIGNALS)
    assert report.friction_count > 0


def test_analyze_clean_signals_zero_friction():
    agent = SlipAgent()
    report = agent.analyze(_CLEAN_SIGNALS)
    assert report.friction_count == 0


def test_analyze_stamps_source_when_missing():
    agent = SlipAgent(source="test-stamp")
    signals = [{"text": "It takes too long."}]  # no 'source' key
    report = agent.analyze(signals)
    # All friction points should carry the agent source
    for fp in report.opportunities[0].friction_points if report.opportunities else []:
        assert fp.source == "test-stamp"


def test_analyze_appends_to_history():
    agent = SlipAgent()
    assert len(agent.history) == 0
    agent.analyze(_SIGNALS)
    assert len(agent.history) == 1
    agent.analyze(_CLEAN_SIGNALS)
    assert len(agent.history) == 2


def test_analyze_history_is_copy():
    agent = SlipAgent()
    agent.analyze(_SIGNALS)
    h = agent.history
    h.clear()
    assert len(agent.history) == 1  # internal list unaffected


# ---------------------------------------------------------------------------
# suggest()
# ---------------------------------------------------------------------------

def test_suggest_returns_opportunities():
    agent = SlipAgent()
    fps = [_make_fp("delay"), _make_fp("workaround"), _make_fp("cost")]
    opps = agent.suggest(fps)
    assert len(opps) == 3
    assert all(isinstance(o, Opportunity) for o in opps)


def test_suggest_sorted_descending():
    agent = SlipAgent()
    fps = [_make_fp("delay"), _make_fp("workaround"), _make_fp("complaint")]
    opps = agent.suggest(fps)
    scores = [o.composite_score for o in opps]
    assert scores == sorted(scores, reverse=True)


def test_suggest_empty_returns_empty():
    agent = SlipAgent()
    assert agent.suggest([]) == []


# ---------------------------------------------------------------------------
# execute()
# ---------------------------------------------------------------------------

def test_execute_returns_dict():
    agent = SlipAgent()
    plan = agent.execute(_make_opp("delay"))
    assert isinstance(plan, dict)


def test_execute_required_keys():
    agent = SlipAgent()
    plan = agent.execute(_make_opp("workaround"))
    assert {"opportunity", "composite_score", "priority", "automation_potential", "actions"} == set(plan.keys())


def test_execute_actions_is_list():
    agent = SlipAgent()
    plan = agent.execute(_make_opp("cost"))
    assert isinstance(plan["actions"], list)
    assert len(plan["actions"]) > 0


def test_execute_priority_high_for_high_score():
    agent = SlipAgent()
    plan = agent.execute(_make_opp("delay", score=0.75))
    assert plan["priority"] == "high"


def test_execute_priority_medium():
    agent = SlipAgent()
    plan = agent.execute(_make_opp("delay", score=0.5))
    assert plan["priority"] == "medium"


def test_execute_priority_low_for_low_score():
    agent = SlipAgent()
    plan = agent.execute(_make_opp("delay", score=0.2))
    assert plan["priority"] == "low"


def test_execute_unknown_pattern_uses_defaults():
    agent = SlipAgent()
    opp = Opportunity(
        title="unknown reduction opportunity",
        friction_points=[_make_fp("unknown")],
        composite_score=0.5,
        automation_potential=0.5,
    )
    plan = agent.execute(opp)
    assert len(plan["actions"]) > 0


# ---------------------------------------------------------------------------
# reset()
# ---------------------------------------------------------------------------

def test_reset_clears_history():
    agent = SlipAgent()
    agent.analyze(_SIGNALS)
    agent.analyze(_SIGNALS)
    assert len(agent.history) == 2
    agent.reset()
    assert len(agent.history) == 0


if __name__ == "__main__":
    test_agent_default_source()
    test_agent_custom_source()
    test_agent_repr()
    test_analyze_returns_slip_report()
    test_analyze_signal_count()
    test_analyze_detects_friction()
    test_analyze_clean_signals_zero_friction()
    test_analyze_stamps_source_when_missing()
    test_analyze_appends_to_history()
    test_analyze_history_is_copy()
    test_suggest_returns_opportunities()
    test_suggest_sorted_descending()
    test_suggest_empty_returns_empty()
    test_execute_returns_dict()
    test_execute_required_keys()
    test_execute_actions_is_list()
    test_execute_priority_high_for_high_score()
    test_execute_priority_medium()
    test_execute_priority_low_for_low_score()
    test_execute_unknown_pattern_uses_defaults()
    test_reset_clears_history()
    print("All SlipAgent tests passed.")
