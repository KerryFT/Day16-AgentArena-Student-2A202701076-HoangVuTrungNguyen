#!/usr/bin/env python3
"""Run the public arena with safe defaults for an OpenAI-compatible model.

The mock is useful for testing middleware, but it follows a fixed retrieval
plan.  This entry point opts into the real-model prompt addendum so the model
can reformulate weak searches and solve the depth and synthesis briefs.
"""

from __future__ import annotations

import argparse
import os
import sys

try:
    from scripts import run_practice
except ImportError:  # Direct execution puts ``scripts`` on sys.path.
    import run_practice


REQUIRED_ENV = ("ARENA_API_KEY", "ARENA_BASE_URL", "ARENA_MODEL")
DEFAULT_OUT = "runs/real-preview.json"
DEFAULT_TRACE_DIR = "runs/traces-real-preview"


def _has_option(args: list[str], option: str) -> bool:
    return option in args or any(arg.startswith(option + "=") for arg in args)


def _effective_model(args: list[str]) -> str:
    for index, arg in enumerate(args):
        if arg == "--model" and index + 1 < len(args):
            return args[index + 1]
        if arg.startswith("--model="):
            return arg.split("=", 1)[1]
    return "real"


def _real_args(extra: list[str]) -> list[str]:
    args = list(extra)
    defaults = (
        ("--model", "real"),
        ("--layers", "all"),
        ("--out", DEFAULT_OUT),
        ("--trace-dir", DEFAULT_TRACE_DIR),
    )
    for option, value in defaults:
        if not _has_option(args, option):
            args.extend((option, value))
    if "--prompt-addendum" not in args:
        args.append("--prompt-addendum")
    if "--strict" not in args:
        args.append("--strict")
    return args


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="show the resolved arguments without contacting the endpoint",
    )
    known, extra = parser.parse_known_args(argv)
    args = _real_args(extra)

    if known.dry_run:
        print("run_practice.py " + " ".join(args))
        return 0

    if _effective_model(args) == "real":
        missing = [name for name in REQUIRED_ENV if not os.environ.get(name, "").strip()]
        if missing:
            print(
                "Missing real-model configuration: " + ", ".join(missing),
                file=sys.stderr,
            )
            print(
                "Set an OpenAI-compatible endpoint, API key, and model name, "
                "then run this command again.",
                file=sys.stderr,
            )
            return 2

    return run_practice.main(args)


if __name__ == "__main__":
    raise SystemExit(main())
