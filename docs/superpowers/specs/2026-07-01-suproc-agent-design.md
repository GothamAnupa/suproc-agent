# Suproc Local Agent Design

## Objective

Build a lightweight local agent that accepts a natural-language business request, searches a synthetic Suproc-style dataset, ranks suitable entities with evidence, validates recommendations deterministically, corrects failures, and prepares the next action without performing consequential business actions.

## Scope

The project is a standalone Python CLI application under `suproc-agent`. It will use a local JSON dataset and deterministic Python tools for retrieval, filtering, ranking, validation, and outreach drafting. Ollama/Qwen support is optional for requirement extraction, with a rule-based fallback so tests and demos run even without the model.

## Architecture

The system is split into focused modules:

- `src/models.py`: Pydantic schemas for requirements, entities, scoring, validation results, and final responses.
- `src/data_loader.py`: Loads `data/suproc_dataset.json` and exposes typed records.
- `src/parser.py`: Converts a request into structured requirements using simple deterministic extraction and optional Ollama enrichment.
- `src/tools.py`: Implements tool functions required by the assignment: `search_entities`, `get_entity_details`, `filter_by_constraints`, and `validate_recommendations`. It also includes `calculate_match_score` and `draft_outreach`.
- `src/agent.py`: Orchestrates the agent loop: interpret request, plan, search, inspect, filter, rank, validate, correct up to three times, and return final structured output.
- `src/cli.py`: Command-line entry point.
- `tests/`: Repeatable pytest suite with at least 10 evaluation cases.

## Dataset

The dataset will be a single JSON file with synthetic records only:

- At least 30 business/supplier records.
- At least 15 professional records.
- At least 10 projects, procurement requirements, opportunities, or bounties.
- Fields include IDs, names, entity type, categories, products or skills, locations, certifications, capacity, delivery time, availability, ratings, completed projects, previous interactions, risk notes, and free-text notes.
- Some records intentionally contain missing fields, conflicting fields, duplicate-like entries, unavailable entities, and prompt-injection text to test validation and safety.

## Data Flow

1. CLI receives a user request.
2. Parser extracts objective, entity type, hard constraints, optional preferences, locations, quantity/capacity, deadline, and requested result count.
3. Agent creates a short execution plan.
4. Agent calls search tools to retrieve candidates from the local dataset.
5. Agent inspects candidate details and filters records that fail hard constraints.
6. Agent scores valid candidates using transparent weighted criteria.
7. Agent validates the recommendations.
8. If validation fails, the agent removes or replaces invalid recommendations and retries, up to three correction attempts.
9. Agent returns a structured final response with evidence, missing information, risks, draft outreach, validation status, and human approval requirement.

## Scoring

Default scoring will use a 100-point weighted method:

- Product or skill relevance: 30 points.
- Location suitability: 20 points.
- Hard-constraint compliance: 25 points.
- Availability, capacity, or delivery fit: 15 points.
- Reputation and previous performance: 10 points.

Each score component will include evidence from dataset fields. Hard-constraint failures are filtered before ranking; they are not hidden by high scores in other areas.

## Validation And Correction

The validator checks:

- Every recommendation exists in the dataset.
- Entity type matches the interpreted request.
- Every hard constraint is satisfied.
- Factual claims are supported by dataset fields.
- Duplicate recommendations are absent.
- The requested number of results is returned, or a clear shortage explanation is provided.
- Unknown or missing data is not presented as fact.
- Match-score totals match the component scores.
- Proposed actions require human approval when consequential.

On validation failure, the agent receives exact failure reasons and attempts correction. It may search again, remove invalid records, replace records, or explain that fewer valid matches are available. It must never invent records.

## Human Approval

The agent may prepare outreach messages and recommend next actions, but it must not send messages, award bounties, approve purchases, accept suppliers, create contracts, invite users, or mutate the dataset. Final outputs will include `Status: Awaiting user approval` for consequential next actions.

## CLI

Example usage:

```bash
python -m src.cli "We are a sustainable food-packaging startup based in Bengaluru. We need three suppliers from South India that can provide food-grade biodegradable containers, support an initial order of 10,000 units and deliver within 30 days. Explain why each supplier is suitable, identify any missing information and prepare an outreach message."
```

The CLI will print JSON by default for easy evaluation, with a readable summary option if time permits.

## Testing

The pytest suite will include repeatable cases for:

- Normal request with several valid matches.
- No record satisfies all hard constraints.
- Conflicting user requirements.
- Missing information in the request.
- Missing information in the dataset.
- Ambiguous location or category.
- Duplicate records.
- Invalid or unavailable entity.
- Recommendation that initially fails validation.
- Prompt-injection attempt inside a dataset record.
- Request requiring human approval.
- Request asking the agent to ignore validation rules.

The README will record total tests, pass/fail status, main failure cases, and known limitations.

## Documentation

The README will include installation instructions, model/system requirements, architecture explanation, sample commands, tool definitions, validation and correction logic, evaluation test instructions, example output, known limitations, and demo video guidance.

## Limitations

Requirement extraction will be intentionally lightweight and optimized for assignment examples rather than general natural-language completeness. Deterministic validation is treated as the authority over model output. The agent will not perform real outreach or external network actions.
