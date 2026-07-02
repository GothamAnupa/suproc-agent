# Suproc Local Agentic Search, Matching And Verification System

This is a lightweight local AI-agent-style system for the Suproc final round assignment. It accepts a natural-language business request, interprets requirements, searches a synthetic Suproc-style dataset, ranks grounded recommendations, validates them deterministically, corrects invalid output, and prepares the next action without performing it automatically.

## Features

- Natural language requirement understanding
- Structured requirement extraction
- Agent planning
- Local dataset search
- Deterministic constraint filtering
- Transparent match scoring
- Validation and correction loop
- Prompt injection protection
- Human approval workflow
- CLI-based execution
- Automated evaluation tests

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

User Request
      │
      ▼
Requirement Parser
      │
      ▼
Planner
      │
      ▼
Tool Layer
 ├── search_entities
 ├── filter_by_constraints
 ├── get_entity_details
 ├── calculate_match_score
 └── validate_recommendations
      │
      ▼
Ranking
      │
      ▼
Validation
      │
      ▼
Correction Loop
      │
      ▼
Final Response
      │
      ▼
Awaiting Human Approval

The system follows a modular agent architecture. The parser extracts structured requirements, the planner generates execution steps, the tool layer retrieves and filters dataset entities, the ranking engine scores candidates, and the validator ensures every recommendation is grounded in dataset evidence. If validation fails, the correction loop retries up to three times before returning a graceful failure. This separation keeps the reasoning layer independent from deterministic business logic.

## Project Structure
suproc-agent/
│
├── data/
│   └── suproc_dataset.json
│
├── src/
│   ├── agent.py
│   ├── parser.py
│   ├── planner.py
│   ├── tools.py
│   ├── validator.py
│   ├── models.py
│   ├── data_loader.py
│   └── cli.py
│
├── tests/
│   └── test_agent.py
│
├── README.md
└── requirements.txt

- `data/suproc_dataset.json`: synthetic local dataset only, with suppliers, businesses, professionals, projects, procurement requirements, opportunities, bounties, incomplete records, unavailable records, duplicate-like records, and prompt-injection text.
- `src/models.py`: Pydantic contracts for entities, requirements, scores, validation, recommendations, and final output.
- `src/data_loader.py`: loads and indexes local JSON records.
- `src/parser.py`: deterministic natural-language requirement extraction.
- `src/tools.py`: required tool layer for search, details lookup, filtering, scoring, validation, and outreach drafting.
- `src/agent.py`: agent orchestration and correction loop.
- `src/cli.py`: local command-line interface.
- `tests/test_agent.py`: repeatable evaluation tests.

## 𝗔𝗴𝗲𝗻𝘁 𝗪𝗼𝗿𝗸𝗳𝗹𝗼𝘄

User Query
      │
Requirement Parsing
      │
Planning
      │
Search Dataset
      │
Constraint Filtering
      │
Ranking
      │
Validation
      │
Correction Loop
      │
Prepare Outreach
      │
Await Human Approval

## Assignment Requirement Coverage

| Requirement | Status |
|-------------|--------|
| Requirement understanding | ✅ |
| Execution planning | ✅ |
| Tool usage | ✅ |
| Local dataset | ✅ |
| Ranking | ✅ |
| Validation | ✅ |
| Correction loop | ✅ |
| Human approval | ✅ |
| Prompt injection handling | ✅ |
| Evaluation tests | ✅ |

## Dataset

The project uses a synthetic Suproc-style dataset stored locally.

Dataset contains:

- 30+ suppliers and businesses
- 15 professionals
- 10 projects/opportunities
- procurement requirements
- certifications
- locations
- capacities
- delivery timelines
- ratings
- previous interaction history

To test robustness, the dataset intentionally includes:

- incomplete records
- conflicting records
- duplicate-like entries
- unavailable entities
- prompt-injection text

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

## Validation Checks
Validation is completely deterministic and is performed using only dataset evidence. The LLM (if enabled) is never trusted as the source of truth.
- Entity exists
- Correct entity type
- Hard constraints satisfied
- No duplicate recommendations
- Match score verified
- Requested result count satisfied
- No unsupported factual claims
- Human approval required

The validator checks every recommendation against deterministic dataset evidence. If validation fails, the agent removes invalid records and refills from the ranked valid pool for up to three correction attempts. If no valid records remain, it clearly reports that no valid matches are available instead of inventing entities.

The agent never follows instructions embedded in dataset notes. A dataset record includes a prompt-injection note specifically to verify this behavior.

## Human Approval

The agent may prepare a message and recommend a next action, but it does not send messages, approve purchases, accept suppliers, award bounties, create contracts, invite users, or mutate the dataset.

Consequential recommendations return:

```text
Status: Awaiting user approval
```
The agent never automatically:

- Send messages
- Accept suppliers
- Approve purchases
- Create contracts
- Modify the dataset

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

## 𝗘𝘅𝗮𝗺𝗽𝗹𝗲 𝗢𝘂𝘁𝗽𝘂𝘁
{
  "recommended_suppliers": [
    {
      "id": "SUP-018",
      "score": 91
    }
  ],
  "validation_status": "Passed",
  "status": "Awaiting user approval"
}

## Security

The system protects against:

- Prompt injection within dataset records
- Unsupported factual claims
- Hallucinated recommendations
- Automatic execution of consequential actions

All recommendations are validated against the local dataset before being returned.
## Known Limitations

- Requirement extraction is deterministic and tuned for the assignment examples. It is not a full natural-language understanding system.
- Ollama/Qwen is documented as optional but not required by the current implementation.
- Dataset search is keyword/rule based, not vector search.
- The system prepares outreach only; it intentionally does not integrate with email, contracts, purchasing, or Suproc production systems.
- Price and commercial terms are often missing from the synthetic dataset and are reported as missing information.

## Future Improvements

- Semantic vector search
- Hybrid retrieval (keyword + embeddings)
- LLM-powered requirement parser
- FastAPI REST API
- Streamlit web interface
- SQLite backend
- Multi-agent workflow


