"""Check that every test job of a generated project can install what it asks for.

Generates a project for a minimum before and after Home Assistant 2026.11, reads each
job's packages from its tests.yml, and resolves them with uv, without installing. The
jobs install with pip; uv only stands in as a fast resolver here.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from copier import run_copy

ROOT = Path(__file__).resolve().parent.parent
ANSWERS = {
    "domain": "acme_heater",
    "product": "Acme Heater",
    "company": "Acme",
    "trademarks": "Acme",
    "device": "heater",
    "equipment": "heaters",
    "description": "The Acme Heater is a heater.",
    "website": "https://www.acme.example",
    "first_date": "2026-11-19",
}


def resolve(project: Path, packages: str, prerelease: str) -> str | None:
    """None if the packages resolve, otherwise uv's error."""
    tokens = packages.split()
    lines = []
    while tokens:
        item = tokens.pop(0)
        lines.append(f"-r {tokens.pop(0)}" if item == "-r" else item)
    wanted = project / "wanted.in"
    wanted.write_text("\n".join(lines) + "\n")
    result = subprocess.run(
        ["uv", "pip", "compile", "--quiet", "--python-version", "3.14.6",
         f"--prerelease={prerelease}", str(wanted)],
        cwd=project, capture_output=True, text=True, check=False,
    )  # fmt: skip
    return None if result.returncode == 0 else result.stderr.strip()


def main() -> int:
    failures = 0
    for minimum in ("2026.3.0", "2026.11.0"):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            run_copy(
                str(ROOT),
                project,
                data={**ANSWERS, "minimum_ha": minimum},
                defaults=True,
                unsafe=True,
                quiet=True,
                vcs_ref="HEAD",
            )
            workflow = yaml.safe_load((project / ".github/workflows/tests.yml").read_text())
            for job in workflow["jobs"]["pytest"]["strategy"]["matrix"]["include"]:
                error = resolve(project, job["packages"], job["prerelease"])
                status = "ok" if error is None else f"FAILS\n{error}"
                print(f"minimum {minimum}, {job['name']}: {status}")
                failures += error is not None
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
