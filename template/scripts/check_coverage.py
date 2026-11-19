"""Fail unless every module's line coverage is above the given percentage.

Home Assistant's quality scale asks for above 95% test coverage for every module.
Usage: python scripts/check_coverage.py coverage.json 95
"""

from __future__ import annotations

import json
import sys


def main(path: str, minimum: float) -> int:
    with open(path, encoding="utf-8") as file:
        report = json.load(file)
    failed = False
    for name, data in sorted(report["files"].items()):
        summary = data["summary"]
        statements = summary["num_statements"]
        if not statements:
            continue
        percent = 100 * summary["covered_lines"] / statements
        if percent <= minimum:
            print(f"{name}: {percent:.1f}% (needs above {minimum:g}%)")
            failed = True
    if not failed:
        print(f"Every module is above {minimum:g}% line coverage.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], float(sys.argv[2])))
