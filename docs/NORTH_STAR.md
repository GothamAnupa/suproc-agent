# Suproc Hermes Agent North Star

## Purpose

Upgrade the current `suproc-agent` into a stronger Suproc final-round submission by using Hermes/Qwen for agentic interpretation and planning while keeping deterministic tools, ranking, validation, and correction as the trusted safety layer.

## North Star Principle

Hermes/Qwen is the reasoning layer. The local dataset and deterministic validator are the truth layer.

The model may help interpret intent, produce structured requirements, create plans, and draft final messages. It must never invent records, skip validation, override hard constraints, mutate data, or perform consequential business actions.

## Target Outcome

Build a local agentic search, matching, and verification system that:

- Understands natural-language business requests.
- Extracts hard constraints and optional preferences.
- Creates a short execution plan.
- Uses tools to search and inspect a local Suproc-style dataset.
- Filters hard constraints strictly.
- Ranks matches using transparent evidence-backed scoring.
- Validates every recommendation deterministically.
- Corrects invalid recommendations up to three times.
- Reports no valid matches instead of inventing records.
- Prepares the next action and outreach message.
- Waits for human approval before any consequential action.

## Final Target Architecture

```text
User Request
  ↓
Hermes/Qwen Requirement Parser
  ↓
Pydantic Schema Validation
  ↓
Planner
  ↓
Tool Execution
  - search_entities
  - get_entity_details
  - filter_by_constraints
  ↓
Ranker
  ↓
Validator
  ↓
Correction Loop
  ↓
Final Response Generator
  ↓
Human Approval Gate
```

## Final Folder Structure

```text
suproc-agent/
  app/
    __init__.py
    main.py
    agent.py
    parser.py
    planner.py
    tools.py
    ranker.py
    validator.py
    memory.py
    models.py
    data_loader.py
  data/
    dataset.json
  tests/
    test_cases.py
  docs/
    NORTH_STAR.md
  config.py
  README.md
  pyproject.toml
```

## Core Design Decisions

- Use Hermes/Qwen only where language understanding helps.
- Keep factual retrieval local and deterministic.
- Validate every recommendation after ranking.
- Treat validation as mandatory and non-bypassable.
- Never perform real-world business actions automatically.
- Return fewer than requested results if only fewer are valid.
- Say `No valid matches found` instead of inventing records.
- Keep tests deterministic by supporting fallback parsing when Ollama is unavailable.

## Existing Base To Reuse

Current files already provide most of the foundation:

```text
src/agent.py
src/parser.py
src/tools.py
src/models.py
src/data_loader.py
src/cli.py
data/suproc_dataset.json
tests/test_agent.py
README.md
```

Reuse the logic, but reorganize and strengthen the architecture.

## Phase 1: Restructure Project

### Objective

Move from `src/` to assignment-friendly `app/` structure.

### Tasks

- [ ] Create `app/`.
- [ ] Move `src/__init__.py` to `app/__init__.py`.
- [ ] Move `src/models.py` to `app/models.py`.
- [ ] Move `src/data_loader.py` to `app/data_loader.py`.
- [ ] Move `src/parser.py` to `app/parser.py`.
- [ ] Move `src/tools.py` to `app/tools.py`.
- [ ] Move `src/agent.py` to `app/agent.py`.
- [ ] Move `src/cli.py` to `app/main.py`.
- [ ] Rename `data/suproc_dataset.json` to `data/dataset.json`.
- [ ] Update imports from `src.*` to `app.*`.
- [ ] Update tests to import from `app.*`.
- [ ] Run `python -m pytest -q`.

### Acceptance Check

```text
All existing tests pass after restructuring.
```

## Phase 2: Add Config Layer

### Objective

Centralize model, dataset, and correction settings.

### Create `config.py`

```python
OLLAMA_MODEL = "qwen3:4b"
OLLAMA_FALLBACK_MODEL = "qwen3:1.7b"
USE_LLM = True
DATASET_PATH = "data/dataset.json"
MAX_CORRECTION_ATTEMPTS = 3
```

### Tasks

- [ ] Create `config.py`.
- [ ] Move dataset path config into `config.py`.
- [ ] Import dataset config from `app/data_loader.py`.
- [ ] Import correction attempt limit from `config.py` in `app/agent.py`.
- [ ] Add a test that dataset loading uses the configured path.

## Phase 3: Add Hermes/Qwen Model Wrapper

### Objective

Add optional local model support without making tests dependent on Ollama.

### Create `app/memory.py`

The file may also be named `app/llm.py`, but `memory.py` matches the proposed assignment structure.

### Responsibilities

```python
def call_model(prompt: str) -> str | None:
    """Call Ollama and return text, or None if unavailable."""

def is_model_available() -> bool:
    """Return whether the configured Ollama model is available."""

def safe_json_from_model(prompt: str) -> dict | None:
    """Return parsed JSON from the model, or None on malformed output."""
```

### Behavior Rules

- Try calling Ollama.
- If Ollama is unavailable, return `None`.
- Never crash the agent because the model is unavailable.
- Never trust model JSON until Pydantic validates it.
- Strip markdown fences before JSON parsing.
- Treat malformed model output as a fallback condition.

### Parser System Prompt

```text
You are a parser for a local business matching system.
Return only JSON.
Do not recommend entities.
Do not invent dataset records.
Do not ignore validation rules.
```

### Tests

- [ ] Model unavailable fallback works.
- [ ] Malformed JSON fallback works.
- [ ] Prompt injection in user request does not disable validation.

## Phase 4: Upgrade Requirement Parser

### Objective

Use Hermes/Qwen first, deterministic parser second.

### Flow

```text
parse_requirement(request)
  ↓
try parse_with_llm(request)
  ↓
validate with BusinessRequirement
  ↓
if invalid, fallback to deterministic parser
```

### LLM Output Schema

```json
{
  "objective": "Find biodegradable food-container suppliers",
  "entity_type": "supplier",
  "hard_constraints": {
    "locations": ["Karnataka", "Tamil Nadu", "Kerala", "Andhra Pradesh", "Telangana"],
    "certifications": ["food-grade"],
    "minimum_capacity": 10000,
    "maximum_delivery_days": 30,
    "product_keywords": ["biodegradable", "container"]
  },
  "preferences": {
    "sustainable_materials": true,
    "startup_friendly": true
  },
  "requested_results": 3,
  "conflicts": [],
  "safety_flags": []
}
```

### Tasks

- [ ] Rename current parser to `parse_requirement_deterministic`.
- [ ] Add `parse_requirement_with_llm`.
- [ ] Keep public function as `parse_requirement`.
- [ ] Validate LLM output through `BusinessRequirement`.
- [ ] Fall back to deterministic parser on model, JSON, or schema failure.
- [ ] Add tests for valid LLM JSON.
- [ ] Add tests for malformed LLM JSON.
- [ ] Add tests for model unavailable.

## Phase 5: Add Planner Module

### Objective

Make agent behavior explicit.

### Create `app/planner.py`

```python
from .models import BusinessRequirement


def create_plan(requirement: BusinessRequirement) -> list[str]:
    return [
        "Extract constraints",
        "Search dataset",
        "Inspect matching records",
        "Filter invalid records",
        "Rank valid records",
        "Validate recommendations",
        "Correct failed recommendations if needed",
        "Generate final response",
        "Wait for human approval",
    ]
```

### Tasks

- [ ] Move hardcoded plan from `agent.py` to `planner.py`.
- [ ] Add test that every agent response includes plan steps.
- [ ] Add test that plan includes validation.
- [ ] Add test that plan includes human approval.

## Phase 6: Split Ranking Engine

### Objective

Make scoring easier to explain and evaluate.

### Create `app/ranker.py`

Move from `tools.py`:

```text
calculate_match_score
rank_entities
```

### Scoring Formula

```text
Product or skill relevance: 30
Location suitability: 20
Hard-constraint compliance: 25
Availability/capacity/delivery: 15
Reputation/performance: 10
```

### Tasks

- [ ] Move `calculate_match_score` into `ranker.py`.
- [ ] Add `rank_entities(entities, requirement)`.
- [ ] Keep score evidence per component.
- [ ] Update `agent.py` to use `rank_entities`.
- [ ] Update tests.

## Phase 7: Split Validation Engine

### Objective

Make validation a first-class safety component.

### Create `app/validator.py`

Move from `tools.py`:

```text
validate_recommendations
```

### Validator Must Check

- Entity exists in dataset.
- Correct entity type.
- All hard constraints are satisfied.
- No duplicate recommendations.
- Requested count is returned or shortage is clearly explained.
- Score arithmetic is correct.
- Claims are supported by dataset fields.
- Unknown information is not presented as fact.
- Human approval is required.

### Tasks

- [ ] Move validation code into `validator.py`.
- [ ] Add explicit failure reason strings.
- [ ] Add tests for duplicates.
- [ ] Add tests for wrong type.
- [ ] Add tests for unavailable entity.
- [ ] Add tests for unsupported factual claim.
- [ ] Add tests for missing approval.

## Phase 8: Keep Tool Layer Focused

### Objective

Tools should retrieve, inspect, and filter only.

### `app/tools.py` Should Contain

```text
search_entities
get_entity_details
filter_by_constraints
check_availability
```

### Tasks

- [ ] Remove ranking from `tools.py`.
- [ ] Remove validation from `tools.py`.
- [ ] Keep search and filtering grounded in dataset.
- [ ] Ensure tools never invent records.
- [ ] Ensure tools ignore prompt-injection notes.
- [ ] Add tool tests.

## Phase 9: Upgrade Agent Orchestration

### Objective

Make the agent loop match the assignment exactly.

### `app/agent.py` Flow

```text
1. Parse request
2. Create execution plan
3. Search dataset
4. Inspect candidates
5. Filter hard constraints
6. Rank valid candidates
7. Select requested number
8. Validate recommendations
9. If validation fails, correct up to 3 times
10. Generate final response
11. Require human approval
```

### Correction Loop

```text
attempt = 0

while attempt < MAX_CORRECTION_ATTEMPTS:
    validation = validate_recommendations(...)
    if validation passes:
        break

    remove invalid records
    refill from next ranked candidates
    attempt += 1

if still invalid:
    return no valid matches or fewer valid matches with explanation
```

### Tests

- [ ] Normal request.
- [ ] Injected invalid initial result.
- [ ] No valid result.
- [ ] Duplicate recommendation.
- [ ] Wrong entity type.
- [ ] Prompt injection.
- [ ] Human approval required.

## Phase 10: Add Final Response Generator

### Objective

Improve final output quality while staying grounded.

### Recommended Approach

Generate structured JSON deterministically. Optionally generate a human-readable summary from validated JSON. Never let Hermes/Qwen add new facts.

### Tasks

- [ ] Add `format_final_response(response)` if needed.
- [ ] Keep CLI JSON as default.
- [ ] Optionally add `--pretty` for readable output.
- [ ] Test JSON output remains stable.

## Phase 11: CLI Upgrade

### Objective

Match the OpenCode interface style.

### `app/main.py` Modes

One-shot mode:

```bash
python -m app.main "request text"
```

Interactive mode:

```bash
python -m app.main
```

Interactive behavior:

```text
User: <query>
Agent: <response>
```

Exit commands:

```text
exit
quit
q
```

### Tasks

- [ ] Keep one-shot CLI.
- [ ] Add input loop when no args are supplied.
- [ ] Print JSON by default.
- [ ] Add CLI smoke test.
- [ ] Manually verify interactive mode.

## Phase 12: Test Suite Upgrade

### Objective

Make evaluation coverage obvious.

### Required Tests

- [ ] Valid request returns three valid matches.
- [ ] No match case returns no invented records.
- [ ] Conflicting constraints are flagged.
- [ ] Missing information is reported.
- [ ] Duplicate recommendations fail validation.
- [ ] Invalid entity fails validation.
- [ ] Prompt injection inside dataset is ignored.
- [ ] Partial match returns fewer results with explanation.
- [ ] Wrong type request does not return suppliers.
- [ ] Approval-required request returns awaiting approval.
- [ ] LLM unavailable fallback works.
- [ ] Malformed LLM JSON fallback works.
- [ ] Request asking to ignore validation is rejected.
- [ ] CLI outputs valid JSON.

### Target

```text
Minimum: 10 tests
Recommended: 14+ tests
```

## Phase 13: README Upgrade

### Objective

Make the submission easy to evaluate.

### README Sections

- Project overview.
- Why Hermes/Qwen is used.
- Architecture diagram.
- Setup instructions.
- Model requirements.
- Dataset explanation.
- Tool definitions.
- Ranking formula.
- Validation logic.
- Correction loop.
- Human approval policy.
- How to run.
- How to test.
- Example outputs.
- Known limitations.
- Demo video checklist.

### Important README Message

```text
Hermes/Qwen is not the source of truth.
Hermes/Qwen helps interpret the user request and draft responses.
All retrieval, filtering, ranking, validation and correction are deterministic and grounded in the local dataset.
```

## Phase 14: Final Verification

### Objective

Prove the implementation is ready before submission.

### Tasks

- [ ] Run full tests.
- [ ] Run assignment example through CLI.
- [ ] Run no-match CLI request.
- [ ] Confirm no real Suproc data.
- [ ] Confirm no secrets.
- [ ] Confirm no automatic consequential actions.
- [ ] Confirm README matches implementation.
- [ ] Record final test count and pass rate.

### Verification Commands

```bash
python -m pytest -q
```

```bash
python -m app.main "We are a sustainable food-packaging startup based in Bengaluru. We need three suppliers from South India that can provide food-grade biodegradable containers, support an initial order of 10,000 units and deliver within 30 days. Explain why each supplier is suitable, identify any missing information and prepare an outreach message."
```

```bash
python -m app.main "Find five suppliers in South India with aerospace-grade biodegradable containers, capacity of 500000 units and delivery within 2 days."
```

## Acceptance Criteria

The upgraded project is complete when:

- [ ] `python -m pytest -q` passes.
- [ ] CLI returns valid JSON fo r the assignment example.
- [ ] The response includes exactly three valid suppliers when available.
- [ ] Each recommendation includes evidence from the dataset.
- [ ] Each recommendation includes score breakdown.
- [ ] Missing information is reported as missing.
- [ ] Prompt injection does not affect behavior.
- [ ] Invalid model output falls back safely.
- [ ] Validation cannot be skipped.
- [ ] Human approval is required for outreach.
- [ ] README clearly explains Hermes/Qwen as reasoning layer, not truth layer.

## Recommended Final Demo Script

1. Show folder structure.
2. Run tests:

```bash
python -m pytest -q
```

3. Run the main assignment example:

```bash
python -m app.main "We are a sustainable food-packaging startup based in Bengaluru. We need three suppliers from South India that can provide food-grade biodegradable containers, support an initial order of 10,000 units and deliver within 30 days. Explain why each supplier is suitable, identify any missing information and prepare an outreach message."
```

4. Point out:

```text
Interpreted requirement
Plan followed
Recommended suppliers
Evidence
Score breakdown
Validation status
Draft outreach
Awaiting human approval
```

5. Run the no-match case:

```bash
python -m app.main "Find five suppliers in South India with aerospace-grade biodegradable containers, capacity of 500000 units and delivery within 2 days."
```

6. Point out:

```text
No invented records
Clear failure explanation
Validation still passes because failure is honest
```

## Key Submission Message

```text
The system behaves like an agent because it interprets the user objective, creates a plan, uses tools against local data, ranks grounded results, validates its own recommendations, corrects failures, and prepares the next action while waiting for human approval.

Hermes/Qwen is used for agentic language understanding and response drafting. Deterministic tools and validators are the source of truth, which prevents hallucinated suppliers and unsafe actions.
```
