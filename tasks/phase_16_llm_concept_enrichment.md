# phase_16_llm_concept_enrichment
Goal:
  Enrich BusinessConcept rationale with an optional LLM-generated description
  using the OpenAI-compatible API, keeping the system fully local-first by
  falling back to the existing static template when the SLIP_OPENAI_API_KEY
  environment variable is not set.

Inputs:
  - Existing BusinessConcept generator in core/ideation.py (phase 14).
  - SLIP_OPENAI_API_KEY env var (optional; if absent, static templates are used).

Outputs:
  - core/ideation.py gains enrich_concept(concept) that calls the LLM when the
    env var is present and updates concept.rationale in-place.
  - generate_concepts() calls enrich_concept() for each BusinessConcept.
  - core/test_ideation.py gains tests: static fallback when key absent, LLM path
    mocked with unittest.mock.patch.

Constraints:
  - Atomic improvement: one new helper function + test coverage only.
  - No breaking changes to phases 2–15.
  - Follows README dev model: ≤400 tokens of code + description.
