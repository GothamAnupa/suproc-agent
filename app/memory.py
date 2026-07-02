from __future__ import annotations

import json
import subprocess

from config import OLLAMA_FALLBACK_MODEL, OLLAMA_MODEL, USE_LLM


def call_model(prompt: str) -> str | None:
    if not USE_LLM:
        return None
    for model in (OLLAMA_MODEL, OLLAMA_FALLBACK_MODEL):
        try:
            completed = subprocess.run(
                ["ollama", "run", model, prompt],
                text=True,
                capture_output=True,
                timeout=30,
                check=False,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return None
        if completed.returncode == 0 and completed.stdout.strip():
            return completed.stdout.strip()
    return None


def is_model_available() -> bool:
    try:
        completed = subprocess.run(["ollama", "list"], text=True, capture_output=True, timeout=5, check=False)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    return completed.returncode == 0 and (OLLAMA_MODEL in completed.stdout or OLLAMA_FALLBACK_MODEL in completed.stdout)


def safe_json_from_model(prompt: str) -> dict | None:
    output = call_model(prompt)
    if not output:
        return None
    cleaned = output.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        parsed = json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None
