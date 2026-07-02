# Suproc Local Agentic Search, Matching And Verification System

This is a lightweight local AI-agent-style system for the Suproc final round assignment. It accepts a natural-language business request, interprets requirements, searches a synthetic Suproc-style dataset, ranks grounded recommendations, validates them deterministically, corrects invalid output, and prepares the next action without performing it automatically.

## Requirements

- Python 3.11 or later
- Pydantic 2.x
- Pytest
- Optional: Ollama with `qwen3:4b` or `qwen3:1.7b` for future LLM parsing experiments

The current implementation is deterministic and does not require Ollama to run. This keeps tests repeatable on low-resource machines.

## Installation

```bash
cd C:\Users\anupa\suproc-agent
python -m pip install pydantic pytest
```

Optional model setup:

```bash
ollama pull qwen3:4b
```

## Run The Agent

```bash
python -m src.cli "We are a sustainable food-packaging startup based in Bengaluru. We need three suppliers from South India that can provide food-grade biodegradable containers, support an initial order of 10,000 units and deliver within 30 days. Explain why each supplier is suitable, identify any missing information and prepare an outreach message."
```

The CLI prints structured JSON containing:

- Interpreted business requirement
- Hard constraints and optional preferences
- Plan followed
- Recommended matches
- Evidence and score breakdowns
- Constraints checked
- Missing information
- Risks and uncertainties
- Recommended next action
- Draft outreach message
- Validation status
- Human approval status

## Architecture

- `data/suproc_dataset.json`: synthetic local dataset only, with suppliers, businesses, professionals, projects, procurement requirements, opportunities, bounties, incomplete records, unavailable records, duplicate-like records, and prompt-injection text.
- `src/models.py`: Pydantic contracts for entities, requirements, scores, validation, recommendations, and final output.
- `src/data_loader.py`: loads and indexes local JSON records.
- `src/parser.py`: deterministic natural-language requirement extraction.
- `src/tools.py`: required tool layer for search, details lookup, filtering, scoring, validation, and outreach drafting.
- `src/agent.py`: agent orchestration and correction loop.
- `src/cli.py`: local command-line interface.
- `tests/test_agent.py`: repeatable evaluation tests.

## Tool Definitions

- `search_entities(entities, requirement)`: searches local records by entity type, product/category keywords, and location hints.
- `get_entity_details(entities, entity_id)`: retrieves a single dataset-backed entity or raises if it does not exist.
- `filter_by_constraints(entities, requirement)`: removes records that fail hard constraints.
- `calculate_match_score(entity, requirement)`: calculates transparent component scores.
- `validate_recommendations(...)`: checks dataset existence, entity type, hard constraints, factual support, duplicates, requested count, score arithmetic, and human approval.
- `draft_outreach(requirement, recommendations)`: prepares an unsent outreach draft.

## Scoring

Scores use a 100-point weighted method:

- Product or skill relevance: 30
- Location suitability: 20
- Hard-constraint compliance: 25
- Availability, capacity, or delivery fit: 15
- Reputation and previous performance: 10

Hard constraints are filtered before ranking. A high score cannot hide a hard-constraint failure.

## Validation And Correction

The validator checks every recommendation against deterministic dataset evidence. If validation fails, the agent removes invalid records and refills from the ranked valid pool for up to three correction attempts. If no valid records remain, it clearly reports that no valid matches are available instead of inventing entities.

The agent never follows instructions embedded in dataset notes. A dataset record includes a prompt-injection note specifically to verify this behavior.

## Human Approval

The agent may prepare a message and recommend a next action, but it does not send messages, approve purchases, accept suppliers, award bounties, create contracts, invite users, or mutate the dataset.

Consequential recommendations return:

```text
Status: Awaiting user approval
```

## Tests And Pass Rate

Run:

```bash
python -m pytest -q
```

Current evaluation suite:

- Total tests: 13
- Tests passed: 13
- Tests failed: 0

Covered cases:

- Normal request with several valid matches
- No record satisfies all hard constraints
- Conflicting user requirements
- Missing information in the request
- Missing information in the dataset
- Ambiguous category/product records
- Duplicate recommendations
- Invalid or unavailable entity
- Recommendation that initially fails validation and is corrected
- Prompt-injection attempt inside a dataset record
- Request requiring human approval
- Request asking the agent to ignore validation rules
- CLI JSON output

## Known Limitations

- Requirement extraction is deterministic and tuned for the assignment examples. It is not a full natural-language understanding system.
- Ollama/Qwen is documented as optional but not required by the current implementation.
- Dataset search is keyword/rule based, not vector search.
- The system prepares outreach only; it intentionally does not integrate with email, contracts, purchasing, or Suproc production systems.
- Price and commercial terms are often missing from the synthetic dataset and are reported as missing information.

## Demonstration Video Guidance

For the required short demo video, show:

1. Running `python -m pytest -q` and the pass rate.
2. Running the assignment example through `python -m src.cli`.
3. Pointing out evidence-backed recommendations, validation status, missing information, draft outreach, and `Awaiting user approval`.
4. Optionally running a no-match request to show graceful failure without invented records.
