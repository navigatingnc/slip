# phase_09_agent_layer
Goal:
  Implement the `SlipAgent` class in `/agents/slip_agent.py` — a stateful wrapper
  over the core pipeline that exposes the three OpenClaw-compatible methods defined
  in the README: `analyze()`, `suggest()`, and `execute()`. This populates the
  `agents/` stub and makes SLIP ready for OpenClaw integration.
Inputs:
  - `analyze(signals)`: list of raw signal dicts → runs ingest→detect→score→report
  - `suggest(friction_points)`: list of FrictionPoint objects → returns ranked Opportunities
  - `execute(opportunity)`: Opportunity object → returns an agent-ready execution plan dict
Outputs:
  - `analyze()` → SlipReport
  - `suggest()` → List[Opportunity] sorted by composite_score descending
  - `execute()` → dict with keys: opportunity, actions, priority, automation_potential
Constraints:
  - Atomic improvement: agent wiring only, no new detection, scoring, or report logic
  - No breaking changes to phases 2–8
  - Follows README dev model: ≤400 tokens of code + description
  - All logic covered by inline tests in `/agents/test_slip_agent.py`
