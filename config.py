from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
OLLAMA_MODEL = "qwen3:4b"
OLLAMA_FALLBACK_MODEL = "qwen3:1.7b"
USE_LLM = True
DATASET_PATH = PROJECT_ROOT / "data" / "suproc_dataset.json"
MAX_CORRECTION_ATTEMPTS = 3
