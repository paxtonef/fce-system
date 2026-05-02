#!/usr/bin/env python3
"""CLI wrapper for FCE."""
import sys
import os
import json
import argparse

# Ajouter src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fce.engine import Engine


def main():
    parser = argparse.ArgumentParser(description="Freedom Constraint Engine CLI")
    parser.add_argument("pack_id", help="Pack ID to evaluate")
    parser.add_argument("--context", "-c", type=str, help="JSON context string")
    parser.add_argument("--context-file", "-f", type=str, help="Path to JSON context file")

    args = parser.parse_args()

    context = None
    if args.context:
        context = json.loads(args.context)
    elif args.context_file:
        with open(args.context_file, "r") as f:
            context = json.load(f)

    engine = Engine()
    result = engine.evaluate(args.pack_id, context)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
