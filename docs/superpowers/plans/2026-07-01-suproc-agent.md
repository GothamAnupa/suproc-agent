# Suproc Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local Suproc-style agent that interprets business requests, searches a synthetic dataset, ranks evidence-backed matches, validates recommendations, corrects failures, and waits for human approval before consequential actions.

**Architecture:** Use a standalone Python package with deterministic data tools as the source of truth. The agent orchestrates parsing, planning, search, filtering, scoring, validation, correction, and final response generation over a JSON dataset.

**Tech Stack:** Python 3.11+, Pydantic, pytest, JSON dataset, optional Ollama documented but not required for tests.

---

## File Structure

- Create `pyproject.toml`: package metadata and pytest config.
- Create `README.md`: install, run, architecture, tests, limitations, demo guidance.
- Create `data/suproc_dataset.json`: synthetic Suproc-style records.
- Create `src/__init__.py`: package marker.
- Create `src/models.py`: Pydantic models and typed data contracts.
- Create `src/data_loader.py`: dataset loading.
- Create `src/parser.py`: deterministic requirement extraction.
- Create `src/tools.py`: local tool functions, filtering, scoring, validation, outreach drafting.
- Create `src/agent.py`: orchestration and correction loop.
- Create `src/cli.py`: command-line entry point.
- Create `tests/test_agent.py`: evaluation tests.

## Task 1: Project Skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `src/__init__.py`

- [ ] **Step 1: Create package configuration**

Add a minimal Pydantic/pytest project configuration with Python 3.11 support.

- [ ] **Step 2: Verify pytest discovers no tests yet**

Run: `python -m pytest -q`
Expected: pytest runs and reports no tests or collection succeeds after tests are added.

## Task 2: Models And Dataset Loader

**Files:**
- Create: `src/models.py`
- Create: `src/data_loader.py`
- Test: `tests/test_agent.py`

- [ ] **Step 1: Write tests for loading typed dataset records**

Test expectations: loader returns suppliers, professionals, and opportunities; supplier IDs are unique enough for lookup; required fields are present or explicitly nullable.

- [ ] **Step 2: Implement Pydantic models**

Models: `BusinessRequirement`, `Entity`, `ScoreBreakdown`, `Recommendation`, `ValidationResult`, `AgentResponse`.

- [ ] **Step 3: Implement loader**

Expose `load_dataset(path: Path | None = None) -> list[Entity]` and `index_entities(entities) -> dict[str, Entity]`.

## Task 3: Synthetic Dataset

**Files:**
- Create: `data/suproc_dataset.json`
- Test: `tests/test_agent.py`

- [ ] **Step 1: Write dataset shape tests**

Assert at least 30 business/supplier records, 15 professional records, and 10 opportunity/project/bounty records.

- [ ] **Step 2: Add dataset records**

Include valid biodegradable food-container suppliers in South India, invalid suppliers with missing food-grade certification, overlong delivery time, insufficient capacity, duplicate-like records, unavailable entities, ambiguous categories, missing fields, and a prompt-injection note.

## Task 4: Requirement Parser

**Files:**
- Create: `src/parser.py`
- Test: `tests/test_agent.py`

- [ ] **Step 1: Write parser tests**

Cover the example request, missing result count defaulting to 3, South India expansion, conflicting constraints, and ignore-validation prompt attempts.

- [ ] **Step 2: Implement deterministic parser**

Extract objective, entity type, hard constraints, preferences, requested results, quantity/capacity, delivery days, location names, and safety flags.

## Task 5: Tools, Filtering, And Scoring

**Files:**
- Create: `src/tools.py`
- Test: `tests/test_agent.py`

- [ ] **Step 1: Write tool tests**

Test `search_entities`, `get_entity_details`, `filter_by_constraints`, and `calculate_match_score` on known records.

- [ ] **Step 2: Implement search and lookup tools**

Search by entity type, product/skill/category keywords, and location hints. Lookup must return records only from the dataset.

- [ ] **Step 3: Implement hard filtering**

Filter unavailable records and records failing location, certification, capacity, delivery deadline, category/product, or entity type constraints.

- [ ] **Step 4: Implement transparent scoring**

Use 30/20/25/15/10 component scoring with evidence strings and total score calculation.

## Task 6: Validation And Correction

**Files:**
- Modify: `src/tools.py`
- Test: `tests/test_agent.py`

- [ ] **Step 1: Write validation tests**

Cover nonexistent entity, wrong type, duplicate recommendations, unsupported claims by missing data, score mismatch, shortage explanation, and missing human approval.

- [ ] **Step 2: Implement validator**

Return exact failure reasons and `is_valid` boolean. Treat missing fields as unknown, not factual support.

## Task 7: Agent Orchestration

**Files:**
- Create: `src/agent.py`
- Test: `tests/test_agent.py`

- [ ] **Step 1: Write end-to-end tests**

Cover normal request, no-valid-result request, validation failure correction, prompt injection in data, request requiring approval, and request asking to ignore validation.

- [ ] **Step 2: Implement agent loop**

Flow: parse requirement, create plan, search candidates, inspect details, filter, score, select requested count, validate, correct up to three attempts, draft outreach, return structured response.

## Task 8: CLI And Documentation

**Files:**
- Create: `src/cli.py`
- Create: `README.md`
- Test: `tests/test_agent.py`

- [ ] **Step 1: Write CLI smoke test**

Run `python -m src.cli "<example request>"` and assert JSON output includes interpreted requirement, recommended matches, validation status, and awaiting approval.

- [ ] **Step 2: Implement CLI**

Accept request text as command arguments and print JSON response.

- [ ] **Step 3: Write README**

Document setup, model requirements, architecture, tool definitions, validation/correction logic, tests, pass-rate command, example output, limitations, and demo video instructions.

## Task 9: Final Verification

**Files:**
- All project files.

- [ ] **Step 1: Run tests**

Run: `python -m pytest -q`
Expected: all tests pass.

- [ ] **Step 2: Run example CLI request**

Run the assignment example through `python -m src.cli`.
Expected: response includes exactly three valid suppliers when available, evidence, score breakdown, missing information, risks, outreach draft, validation status, and `Awaiting user approval`.

- [ ] **Step 3: Inspect final files**

Confirm no real Suproc data, no secrets, no automatic consequential actions, and README contains honest limitations.

## Self-Review

- Spec coverage: all assignment sections map to dataset, parser, tools, validation/correction, CLI, tests, and README tasks.
- Placeholder scan: no implementation placeholders remain in the plan; task steps define concrete files and behaviors.
- Type consistency: model and function names are consistent across tasks.
