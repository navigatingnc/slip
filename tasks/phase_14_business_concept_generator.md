# phase_14_business_concept_generator
Goal:
  Implement a BusinessConcept generator that maps each Opportunity to a
  human-readable business idea, completing the README pipeline:
    Signal → Pattern → Friction → Score → Opportunity → Business Concept
Inputs:
  - An Opportunity object (title, pattern, composite_score, willingness_to_pay,
    market_size, automation_potential).
Outputs:
  - A BusinessConcept dataclass with: opportunity_title, concept, model,
    and rationale fields.
  - core/ideation.py exposes generate_concepts(opportunities) → List[BusinessConcept].
  - SlipReport.to_dict() surfaces concepts in its JSON output.
  - CLI --score output prints the business concept alongside each opportunity.
Constraints:
  - Pattern-keyed template lookup only — no LLM calls, stays local-first.
  - Atomic improvement: ideation layer only, no changes to detection or scoring.
  - No breaking changes to phases 2–13.
  - All logic covered by tests in core/test_ideation.py.
  - Follows README dev model: ≤400 tokens of code + description.
