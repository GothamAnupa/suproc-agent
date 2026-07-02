from __future__ import annotations

import json
import sys

from .agent import run_agent


def _print_response(request: str) -> None:
    response = run_agent(request)
    print(json.dumps(response.model_dump(), indent=2))


def main() -> None:
    if len(sys.argv) > 1:
        _print_response(" ".join(sys.argv[1:]))
        return
    while True:
        query = input("User: ").strip()
        if query.lower() in {"exit", "quit", "q"}:
            break
        if query:
            _print_response(query)


if __name__ == "__main__":
    main()
