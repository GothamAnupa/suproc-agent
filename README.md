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

## Run The Agent (CLI)

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

## Deploy to Vercel

The project is configured for deployment on Vercel as a serverless Python application.

### One-click Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/GothamAnupa/suproc-agent)

Or manually:

1. Connect your GitHub repository to Vercel
2. Vercel automatically detects `vercel.json` and deploys `api/handler.py`
3. Your API is live at `https://your-project.vercel.app/api/handler`

### API Usage

**Health Check (GET):**
```bash
curl https://your-project.vercel.app/api/handler
```

Response: `{"status": "ok"}`

**Run Agent (POST):**
```bash
curl -X POST https://your-project.vercel.app/api/handler \
  -H "Content-Type: application/json" \
  -d '{
    "query": "We are a sustainable food-packaging startup based in Bengaluru. We need three suppliers from South India that can provide food-grade biodegradable containers, support an initial order of 10,000 units and deliver within 30 days."
  }'
```

Response: Structured JSON with agent output (same as CLI output).

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
python -m pytest tests/test_agent.py -v
```

**Current evaluation suite:**

- **Total tests:** 16
- **Tests passed:** 16 ✅
- **Tests failed:** 0
- **Pass rate:** 100%

**Covered cases:**

1. ✅ Normal request with several valid matches
2. ✅ No record satisfies all hard constraints
3. ✅ Conflicting user requirements
4. ✅ Missing information in the request
5. ✅ Missing information in the dataset
6. ✅ Ambiguous category/product records
7. ✅ Duplicate recommendations
8. ✅ Invalid or unavailable entity
9. ✅ Recommendation that initially fails validation and is corrected
10. ✅ Prompt-injection attempt inside a dataset record
11. ✅ Request requiring human approval
12. ✅ Request asking the agent to ignore validation rules
13. ✅ Parser robustness with malformed JSON fallback
14. ✅ Dataset requirements (30+ suppliers, 15+ professionals)
15. ✅ Tool integration (search→filter→score pipeline)
16. ✅ CLI JSON output format

See [EVALUATION_REPORT.md](EVALUATION_REPORT.md) for detailed test analysis and breakdown.

## Example Output
```json
{
  "interpreted_requirement": {
    "objective": "Find food-grade biodegradable container suppliers",
    "entity_type": "supplier",
    "hard_constraints": {
      "locations": ["Karnataka", "Tamil Nadu", "Kerala"],
      "minimum_capacity": 10000,
      "maximum_delivery_days": 30,
      "certifications": ["food-grade"]
    },
    "requested_results": 3
  },
  "recommended_matches": [
    {
      "entity_id": "SUP-018",
      "name": "GreenPack Solutions",
      "score": {
        "total": 91,
        "components": {
          "product_or_skill_relevance": {"points": 28, "max_points": 30},
          "hard_constraint_compliance": {"points": 25, "max_points": 25},
          "availability_capacity_delivery": {"points": 15, "max_points": 15}
        }
      },
      "evidence": ["food-grade certified", "15000 unit capacity", "30-day delivery"]
    }
  ],
  "validation": {
    "is_valid": true,
    "checks": ["dataset existence", "hard constraints", "duplicates", "score arithmetic"]
  },
  "status": "Awaiting user approval",
  "human_approval_required": true
}
```

## System Requirements

### Minimum Requirements
- **OS:** Windows, macOS, or Linux
- **Python:** 3.11 or later (tested on 3.14.3)
- **RAM:** 2GB minimum (4GB recommended)
- **Disk:** 500MB for dependencies and dataset

### Core Dependencies
```
pydantic>=2.7.0       # Data validation
pytest>=8.0.0         # Testing
```

### Optional Dependencies
```
fastapi>=0.115.0      # REST API
uvicorn>=0.30.0       # ASGI server
streamlit>=1.28.0     # Web UI
ollama>=0.4.0         # Local LLM (optional, deterministic default)
```

### Optional: Local LLM Setup
For advanced requirement parsing:
```bash
# Download Ollama: https://ollama.ai
ollama pull qwen3:4b     # 4GB model
# or
ollama pull qwen3:1.7b   # 1.7GB model (low-resource systems)
```

## Known Limitations

1. **Dataset Scope** - Synthetic data (100 records); linear scaling with larger datasets
2. **Deterministic Mode** - LLM optional; core ranking uses predefined rules (intentional)
3. **Regional Mapping** - Hardcoded state-to-region mappings; extensible
4. **Scoring Weights** - Fixed weights per `ranker.py`; tunable
5. **Availability Status** - Binary (available/unavailable); extensible to time-based slots
6. **Sequential Processing** - Single-threaded; parallelizable for 1000+ records
7. **Vercel Deployment** - Requires external HTTP adapter for production
8. **Pricing Data** - Static dataset values; no real-time integration
9. **Requirement Parsing** - Tuned for assignment examples; not a full NLU system
10. **Search** - Keyword/rule-based; not vector-based embeddings

## Security Considerations

The system protects against:

- ✅ Prompt injection within dataset records
- ✅ Unsupported factual claims  
- ✅ Hallucinated recommendations
- ✅ Automatic execution of consequential actions
- ✅ Conflicting requirements masking invalid constraints

All recommendations are validated against the local dataset before being returned. No LLM output is trusted as the source of truth.

## Deliverables Summary

✅ **Source Code Repository** - https://github.com/GothamAnupa/suproc-agent  
✅ **README with Instructions** - Installation, execution, architecture, testing  
✅ **System & Model Requirements** - Python 3.11+, optional Ollama  
✅ **Architecture Explanation** - 7-layer modular design with validation gates  
✅ **Sample Dataset** - `data/suproc_dataset.json` (100+ records, intentionally includes edge cases)  
✅ **Tool Definitions** - 6 core functions with deterministic behavior  
✅ **Validation & Correction Logic** - Multi-check validation with automatic retry (max 3 attempts)  
✅ **Evaluation Tests** - 16 automated tests with 100% pass rate  
✅ **Example Agent Outputs** - JSON responses with evidence and scoring breakdown  
✅ **Live Demonstration** - [Streamlit App](https://suproc-agent-n5vt3gkgwcdqwguvkyzoyf.streamlit.app/)  
✅ **Detailed Test Report** - [EVALUATION_REPORT.md](EVALUATION_REPORT.md)  

## Future Improvements

- Semantic vector search with embeddings
- Hybrid retrieval (keyword + vector)
- LLM-powered requirement parser (via Ollama)
- FastAPI REST API with authentication
- Advanced Streamlit UI with caching
- SQLite backend for production datasets
- Multi-agent workflow coordination
- A/B testing framework for scoring weights
- Real-time pricing integration
- Notification system for outreach delivery


