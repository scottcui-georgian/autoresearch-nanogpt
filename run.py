#!/usr/bin/env python3
"""
Task-specific runner for nanogpt experiments.

Usage:
    uv run python run.py train > run.log 2>&1
    uv run python run.py prepare --num-shards 10
"""

from __future__ import annotations

import argparse
import sys

from autoresearch.modal_runner import run_modal
from autoresearch.task import load_task_config


def main() -> int:
    parser = argparse.ArgumentParser(description="Run nanogpt experiments on Modal.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("train", help="Run a single training experiment on Modal L40S.")

    prepare_parser = subparsers.add_parser("prepare", help="Run one-time data preparation on Modal CPU.")
    prepare_parser.add_argument("--num-shards", type=int, default=10)
    prepare_parser.add_argument("--download-workers", type=int, default=8)

    args = parser.parse_args()
    config = load_task_config()

    return run_modal(config, args.command, quiet=(args.command != "train"))


if __name__ == "__main__":
    sys.exit(main())
