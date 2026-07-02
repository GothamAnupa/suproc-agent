from __future__ import annotations

import json
import sys

from .agent import run_agent


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python -m src.cli '<business request>'")
    response = run_agent(" ".join(sys.argv[1:]))
    print(json.dumps(response.model_dump(), indent=2))


if __name__ == "__main__":
    main()
