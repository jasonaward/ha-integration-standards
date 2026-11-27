#!/usr/bin/env python3
"""Check a project against the Home Assistant integration standard.

    python check/check_standard.py PATH_TO_PROJECT

Errors are **must** rules that aren't met; warnings are _should_ rules. Exits 1 when
there are errors. Uses only the Python standard library (3.12 or later). The standard
text the README must contain is read from STANDARD.md next to this script, so the check
always matches the version of the standard it comes with.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import struct
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
STANDARD = HERE.parent / "STANDARD.md"
LICENSE = HERE.parent / "LICENSE"

OWNER = "jasonaward"
AUTHOR = "Jason Ward"
VERSION = re.compile(r"^0\.(0|[1-9]\d*)\.(0|[1-9]\d*)(b[1-9]\d*)?$")
HA_VERSION = re.compile(r"^20\d\d\.\d{1,2}\.\d+(b0)?$")
PINNED = re.compile(r"^[A-Za-z0-9_.\-]+(\[[A-Za-z0-9_,.\-]+\])?==[A-Za-z0-9_.+!\-]+$")

QUALITY_SCALE = {
    "bronze": [
        "action-setup", "appropriate-polling", "brands", "common-modules",
        "config-flow", "config-flow-test-coverage", "dependency-transparency",
        "docs-actions", "docs-conditions", "docs-high-level-description",
        "docs-installation-instructions", "docs-removal-instructions", "docs-triggers",
        "entity-event-setup", "entity-unique-id",
        "has-entity-name", "runtime-data", "test-before-configure", "test-before-setup",
        "unique-config-entry",
    ],
    "silver": [
        "action-exceptions", "config-entry-unloading", "docs-configuration-parameters",
        "docs-installation-parameters", "entity-unavailable", "integration-owner",
        "log-when-unavailable", "parallel-updates", "reauthentication-flow", "test-coverage",
    ],
    "gold": [
        "devices", "diagnostics", "discovery", "discovery-update-info", "docs-data-update",
        "docs-examples", "docs-known-limitations", "docs-supported-devices",
        "docs-supported-functions", "docs-troubleshooting", "docs-use-cases",
        "dynamic-devices", "entity-category", "entity-device-class",
        "entity-disabled-by-default", "entity-translations", "exception-translations",
        "icon-translations", "reconfiguration-flow", "repair-issues", "stale-devices",
    ],
    "platinum": ["async-dependency", "inject-websession", "strict-typing"],
}  # fmt: skip

NOREPLY = re.compile(r"@users\.noreply\.github\.com$", re.IGNORECASE)
TRAILER = re.compile(
    r"^(Co-Authored-By|Signed-off-by|Claude-Session):", re.IGNORECASE | re.MULTILINE
)

# (heading pattern, required); "cloud" means required when the integration uses a service.
README_SECTIONS: list[tuple[str, bool | str]] = [
    (r"Use cases", True),
    (r"Supported devices", True),
    (r"Unsupported devices", True),
    (r"Prerequisites", True),
    (r"Installation", True),
    (r"Configuration", True),
    (r"Configuration options", True),
    (r"Supported functionality", True),
    (r"Triggers", False),
    (r"Conditions", False),
    (r"Actions", False),
    (r"Examples", True),
    (r"Data updates", True),
    (r"Load on .+", "cloud"),
    (r"Security and privacy", True),
    (r"(.+ )?[Ss]afety", False),
    (r"Known limitations", True),
    (r"Troubleshooting", True),
    (r"Removing the integration", True),
    (r"Development", True),
    (r"Acknowledgments", False),
    (r"License and disclaimer", True),
]

REQUIRED_FILES = [
    "README.md", "CHANGELOG.md", "LICENSE", "NOTICE", "SECURITY.md", "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md", "hacs.json", ".gitignore", ".standard-version",
    ".github/pull_request_template.md", ".github/dependabot.yml",
    ".github/ISSUE_TEMPLATE/config.yml", "requirements_test.txt", "requirements_ci.txt",
]  # fmt: skip
GITIGNORE = [
    "answers.json", "config_entry-*.json", "*.har", "*.flow", "*.pcap", "*.log",
    "secrets.yaml", ".env",
]  # fmt: skip
# Workflows a project must have (section 7), by file name.
REQUIRED_WORKFLOWS = [
    "tests.yml",
    "validate.yml",
    "codeql.yml",
    "standard.yml",
    "release.yml",
]
# The header lines of an audit report (4.3.4).
AUDIT_HEADER = ["Version:", "Standard:", "Date:", "Reviewer:", "Context:"]
LATIN = re.compile(r"\b(e\.g\.|i\.e\.|etc\.|etcetera)", re.IGNORECASE)
BRAND_REQUIRED = {
    "icon.png": 256,
    "icon@2x.png": 512,
    "dark_icon.png": 256,
    "dark_icon@2x.png": 512,
}
BRAND_LOGOS = {"logo.png": (128, 256), "logo@2x.png": (256, 512)}
ALLOWED_EMAIL = re.compile(
    r"(@(example\.(com|org|net)|[a-z0-9-]+\.example)$)|(@users\.noreply\.github\.com$)|"
    r"(^opensource@)",
    re.IGNORECASE,
)
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}\b")
NOT_EMAIL_SUFFIX = (".png", ".svg", ".jpg", ".jpeg", ".webp", ".gif")
SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "node_modules",
}


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, where: str, message: str) -> None:
        self.errors.append(f"{where}: {message}")

    def warn(self, where: str, message: str) -> None:
        self.warnings.append(f"{where}: {message}")


@dataclass
class Project:
    root: Path
    report: Report
    domain: str = ""
    manifest: dict = field(default_factory=dict)
    version: str = ""
    minimum_ha: str = ""

    @property
    def repo(self) -> str:
        return "ha-" + self.domain.replace("_", "-")

    @property
    def cloud(self) -> bool:
        return str(self.manifest.get("iot_class", "")).startswith("cloud_")

    @property
    def unofficial(self) -> bool:
        return str(self.manifest.get("name", "")).endswith("(unofficial)")

    def path(self, name: str) -> Path:
        return self.root / name

    def read(self, name: str) -> str | None:
        p = self.path(name)
        return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else None


# ---------------------------------------------------------------------- helpers


def _norm(text: str) -> str:
    """Text without quote markers and with single spaces."""
    lines = [re.sub(r"^(\s*>)+\s?", "", line) for line in text.splitlines()]
    return " ".join(" ".join(lines).split())


def _pattern(text: str, fill: dict[str, str]) -> re.Pattern[str]:
    """A regex for standard text: known placeholders filled, others matching anything."""
    for key, value in fill.items():
        text = text.replace(key, value)
    parts = re.split(r"<[A-Za-z][^<>]*>", _norm(text))
    return re.compile(".+?".join(re.escape(part) for part in parts))


def _variants(text: str) -> list[str]:
    """Standard text with its allowed forms (5.2): a single trademark, no connection."""
    forms = [text]
    if "are trademarks" in text:
        forms.append(text.replace("are trademarks", "is a trademark"))
    if re.search(r"<How it\s+connects>", text):
        forms += [re.sub(r"<How it\s+connects>\s+", "", form) for form in forms]
    return forms


def standard_sections() -> list[str]:
    """Each section of the standard to audit: its numbered subsections, or the section."""
    text = STANDARD.read_text(encoding="utf-8")
    subsections = re.findall(r"^### (\d+\.\d+) ", text, re.MULTILINE)
    sections = []
    for number in re.findall(r"^## (\d+)\. ", text, re.MULTILINE):
        inside = [s for s in subsections if s.split(".")[0] == number]
        sections += inside or [number]
    return sections


def _section_named(number: str, report: str) -> bool:
    """True if a line of the report starts with the section's number, as a verdict does."""
    pattern = rf"(?m)^[\s>|#*-]*{re.escape(number)}(?:\.\d+)*(?![\d])(?!\.\d)"
    if "." not in number:
        pattern = rf"(?m)^[\s>|#*-]*{re.escape(number)}(?:\.\d+)*\b"
    return re.search(pattern, report) is not None


def standard_blocks() -> dict[str, list[str]]:
    """The standard text of each subsection of STANDARD.md, split into paragraphs."""
    text = STANDARD.read_text(encoding="utf-8")
    blocks: dict[str, list[str]] = {}
    for match in re.finditer(
        r"^### (\d\.\d) .*?\n(.*?)(?=^### |^## |\Z)", text, re.MULTILINE | re.DOTALL
    ):
        for body in re.finditer(
            r"> _Standard text_\n>\n> ```markdown\n(.*?)\n> ```", match[2], re.DOTALL
        ):
            lines = [
                line[2:] if line.startswith("> ") else line[1:] for line in body[1].splitlines()
            ]
            paragraphs = re.split(r"\n\s*(?:>\s*)?\n", "\n".join(lines))
            blocks.setdefault(match[1], []).extend(p for p in paragraphs if p.strip())
    return blocks


def version_key(version: str) -> tuple[int, int, float]:
    """Sort key for 0.MINOR.PATCH[bN]: a beta comes before its release."""
    found = VERSION.match(version)
    if not found:
        return (-1, -1, -1)
    _, minor, patch = version.split("b")[0].split(".")
    return (int(minor), int(patch), int(found[3][1:]) if found[3] else float("inf"))


def ha_key(version: str) -> tuple[int, int]:
    year, month = version.split(".")[:2]
    return (int(year), int(month))


def standard_version() -> str:
    found = re.search(r"\*\*Version (\d+\.\d+\.\d+)\*\*", STANDARD.read_text(encoding="utf-8"))
    return found[1] if found else "?"


def tracked_files(root: Path) -> list[Path]:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-co", "--exclude-standard", "-z"],
            capture_output=True, check=True, text=True,
        ).stdout  # fmt: skip
        return [
            root / name
            for name in out.split("\0")
            if name and not name.startswith(".standard/") and (root / name).is_file()
        ]
    except (OSError, subprocess.CalledProcessError):
        result = []
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and d != ".standard"]
            result += [Path(dirpath) / name for name in filenames]
        return result


def png_size(path: Path) -> tuple[int, int] | None:
    data = path.read_bytes()[:24]
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", data[16:24])


def quality_scale(text: str) -> dict[str, tuple[str, str]]:
    """rule -> (status, comment), from the simple YAML Home Assistant uses."""
    rules: dict[str, tuple[str, str]] = {}
    current = None
    in_comment = False
    for raw in text.splitlines():
        line = (
            raw.split(" #", 1)[0].rstrip()
            if not raw.lstrip().startswith("comment")
            else raw.rstrip()
        )
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()
        if indent == 2 and re.match(r"^[a-z0-9-]+:", stripped):
            name, _, value = stripped.partition(":")
            current, in_comment = name, False
            rules[name] = (value.strip(), "")
        elif indent >= 4 and current:
            key, _, value = stripped.partition(":")
            status, comment = rules[current]
            if key == "status" and not in_comment:
                rules[current] = (value.strip(), comment)
            elif key == "comment" and not in_comment:
                rules[current] = (status, value.strip().lstrip(">-|").strip())
                in_comment = True
            elif in_comment:
                rules[current] = (status, (comment + " " + stripped).strip())
    return rules


# ----------------------------------------------------------------------- checks


def check_basics(p: Project) -> None:
    r = p.report
    for name in REQUIRED_FILES:
        if not p.path(name).is_file():
            r.error(name, "missing")
    version_file = p.read(".standard-version")
    if version_file is not None:
        wanted = version_file.strip()
        if not re.fullmatch(r"\d+\.\d+\.\d+", wanted):
            r.error(".standard-version", f"not a version: {wanted!r}")
        elif wanted != standard_version():
            r.error(
                ".standard-version",
                f"follows {wanted}, but the workflow runs the check of {standard_version()}: "
                "change the two together (8.3)",
            )
    templates = p.path(".github/ISSUE_TEMPLATE")
    if (
        not [f for f in templates.glob("*.y*ml") if f.name != "config.yml"]
        if templates.is_dir()
        else True
    ):
        r.error(".github/ISSUE_TEMPLATE", "no bug report form")
    workflows = p.path(".github/workflows")
    for name in REQUIRED_WORKFLOWS:
        if not (workflows / name).is_file():
            r.error(f".github/workflows/{name}", "missing (section 7)")
    if not list(p.path("docs/brand").glob("*.svg")):
        r.error("docs/brand", "no SVG sources for the brand images")


def check_integration(p: Project) -> None:
    r = p.report
    components = p.path("custom_components")
    domains = (
        [d for d in components.iterdir() if d.is_dir() and not d.name.startswith(("_", "."))]
        if components.is_dir()
        else []
    )
    if len(domains) != 1:
        r.error(
            "custom_components",
            f"expected exactly one integration, found {len(domains)}",
        )
        return
    p.domain = domains[0].name
    base = f"custom_components/{p.domain}"
    for name in ("manifest.json", "quality_scale.yaml", "translations/en.json"):
        if not p.path(f"{base}/{name}").is_file():
            r.error(f"{base}/{name}", "missing")
    if p.path(f"{base}/strings.json").is_file():
        r.error(
            f"{base}/strings.json",
            "Home Assistant doesn't use strings.json for custom integrations",
        )
    try:
        p.manifest = json.loads(p.read(f"{base}/manifest.json") or "{}")
    except ValueError as err:
        r.error(f"{base}/manifest.json", f"invalid JSON: {err}")
        return
    m, where = p.manifest, f"{base}/manifest.json"
    url = f"https://github.com/{OWNER}/{p.repo}"
    if m.get("domain") != p.domain:
        r.error(where, f"domain should be {p.domain!r}")
    if m.get("codeowners") != [f"@{OWNER}"]:
        r.error(where, f'codeowners should be ["@{OWNER}"]')
    if m.get("documentation") != url:
        r.error(where, f"documentation should be {url}")
    if m.get("issue_tracker") != f"{url}/issues":
        r.error(where, f"issue_tracker should be {url}/issues")
    requirements = m.get("requirements")
    if not isinstance(requirements, list):
        r.error(where, "requirements should be a list (empty if none)")
        requirements = []
    for req in requirements:
        if not PINNED.match(str(req)):
            r.error(where, f"requirement not pinned exactly: {req}")
    loggers = m.get("loggers", [])
    if not isinstance(loggers, list):
        r.error(where, "loggers should be a list")
    elif requirements and not loggers:
        r.error(where, "loggers should name the loggers of the requirements")
    if not m.get("categories"):
        r.warn(where, "no categories, which 2.4 says it should have")
    p.version = str(m.get("version", ""))
    if not VERSION.match(p.version):
        r.error(where, f"version {p.version!r} isn't 0.MINOR.PATCH or 0.MINOR.PATCHbN")
    name = str(m.get("name", ""))
    if not name:
        r.error(where, "no name")
    for init in sorted(p.path(base).glob("*/__init__.py")):
        if re.search(r"^__version__ = ", init.read_text(encoding="utf-8"), re.MULTILINE):
            r.error(
                str(init.parent.relative_to(p.root)),
                "a bundled client library: it belongs in its own repository on PyPI (6.4)",
            )
    for flow in sorted(p.path(base).glob("*flow*.py")):
        if re.search(
            r"CONF_SCAN_INTERVAL|[\"']scan_interval[\"']|update_interval",
            flow.read_text(encoding="utf-8"),
        ):
            r.error(
                str(flow.relative_to(p.root)),
                "users mustn't set the polling interval (appropriate-polling)",
            )


def check_hacs(p: Project) -> None:
    text = p.read("hacs.json")
    if text is None:
        return
    try:
        hacs = json.loads(text)
    except ValueError as err:
        p.report.error("hacs.json", f"invalid JSON: {err}")
        return
    want = {
        "zip_release": True,
        "filename": f"{p.domain}.zip",
        "hide_default_branch": True,
    }
    for key, value in want.items():
        if hacs.get(key) != value:
            p.report.error("hacs.json", f"{key} should be {json.dumps(value)}")
    if hacs.get("name") != p.manifest.get("name"):
        p.report.error("hacs.json", "name should match the manifest's name")
    minimum = str(hacs.get("homeassistant", ""))
    if not HA_VERSION.match(minimum):
        p.report.error("hacs.json", "homeassistant should be the minimum version, like 2026.3.0")
    elif ha_key(minimum) < (2026, 3):
        p.report.error(
            "hacs.json",
            "the minimum is at least 2026.3.0, which shows the brand/ images (2.7)",
        )
    else:
        p.minimum_ha = minimum


def check_changelog(p: Project) -> None:
    text = p.read("CHANGELOG.md")
    if text is None:
        return
    headings = re.findall(r"^## (.+)$", text, re.MULTILINE)
    versions = []
    for heading in headings:
        if heading == "Unreleased":
            continue
        found = re.fullmatch(r"(\S+) \((\d{4}-\d\d-\d\d)(, beta)?\)", heading)
        if not found or not VERSION.match(found[1]):
            p.report.error(
                "CHANGELOG.md",
                f"heading isn't '## <version> (YYYY-MM-DD[, beta])': {heading}",
            )
            continue
        if bool(found[3]) != ("b" in found[1]):
            p.report.error(
                "CHANGELOG.md",
                f"'beta' should mark exactly the beta versions: {heading}",
            )
        versions.append(found[1])
    if len(set(versions)) != len(versions):
        p.report.error("CHANGELOG.md", "a version appears twice")
    elif versions != sorted(versions, key=version_key, reverse=True):
        p.report.error("CHANGELOG.md", "versions aren't newest first")
    for heading, body in re.findall(r"^## (.+?)\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL):
        for line in body.splitlines():
            if line.strip() and not line.startswith(("- ", "  ")):
                p.report.error("CHANGELOG.md", f"'## {heading}' should contain only bullets")
                break
        if "**Action needed:**" in body and not body.strip().startswith("- **Action needed:**"):
            p.report.error(
                "CHANGELOG.md",
                f"**Action needed:** should be the first bullet in '## {heading}'",
            )
    if p.version and (not versions or versions[0] != p.version):
        p.report.error("CHANGELOG.md", f"the newest entry should be {p.version}")


def check_quality_scale(p: Project) -> None:
    where = f"custom_components/{p.domain}/quality_scale.yaml"
    text = p.read(where)
    if text is None:
        return
    rules = quality_scale(text)
    release = bool(p.version) and "b" not in p.version
    for tier, names in QUALITY_SCALE.items():
        for name in names:
            if name not in rules:
                p.report.error(where, f"{name} isn't listed")
                continue
            status, comment = rules[name]
            if status not in ("done", "todo", "exempt"):
                p.report.error(where, f"{name}: status should be done, todo or exempt")
            elif status != "done" and not comment:
                p.report.error(where, f"{name}: {status} needs a comment")
            if status == "todo" and release and tier != "platinum":
                p.report.error(where, f"{name} is todo; a release needs Gold")
            if status == "todo" and tier == "platinum":
                p.report.warn(where, f"{name} is todo; the project should reach Platinum (2.1)")


def check_brand(p: Project) -> None:
    folder = f"custom_components/{p.domain}/brand"
    for name, size in BRAND_REQUIRED.items():
        path = p.path(f"{folder}/{name}")
        if not path.is_file():
            p.report.error(f"{folder}/{name}", "missing")
        elif png_size(path) != (size, size):
            p.report.error(f"{folder}/{name}", f"should be a {size}×{size} PNG")
    for base, (low, high) in BRAND_LOGOS.items():
        for name in (base, f"dark_{base}"):
            path = p.path(f"{folder}/{name}")
            if not path.is_file():
                p.report.warn(f"{folder}/{name}", "missing")
            elif (dims := png_size(path)) is None or not low <= min(dims) <= high:
                p.report.error(
                    f"{folder}/{name}",
                    f"should be a PNG with its shortest side {low}–{high}",
                )


def check_readme(p: Project) -> None:
    text = p.read("README.md")
    if text is None:
        return
    r, where = p.report, "README.md"
    title = f"# {p.manifest.get('name', '')} for Home Assistant"
    if not text.strip():
        r.error(where, "empty")
        return
    if text.splitlines()[0].strip() != title:
        r.error(where, f"first line should be '{title}'")

    intro = text.split("\n## ", 1)[0].split("\n> ", 1)[0]
    if not re.search(r"\]\(https?://", intro):
        r.error(
            where,
            "the introduction should link the manufacturer's or service's website",
        )

    found = re.findall(r"^## (.+?)\s*$", text, re.MULTILINE)
    positions = []
    for heading in found:
        index = next(
            (i for i, (pat, _) in enumerate(README_SECTIONS) if re.fullmatch(pat, heading)),
            None,
        )
        if index is None:
            r.warn(where, f"section not in the standard: '## {heading}'")
        else:
            positions.append(index)
    if positions != sorted(positions):
        r.error(where, "sections aren't in the standard's order")
    for i, (pat, required) in enumerate(README_SECTIONS):
        needed = required is True or (required == "cloud" and p.cloud)
        if needed and i not in positions:
            r.error(where, f"missing section '## {pat}'")

    sections = dict(re.findall(r"^## (.+?)\s*\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL))
    subsections = {
        "Supported devices": ["Tested", "Likely to work, not tested"],
        "Installation": ["Marketplace or HACS", "Manual"],
    }
    for section, subs in subsections.items():
        found_subs = re.findall(r"^### (.+?)\s*$", sections.get(section, ""), re.MULTILINE)
        if found_subs[: len(subs)] != subs:
            r.error(
                where,
                f"'## {section}' should start with " + ", ".join(f"'### {s}'" for s in subs),
            )
    marked = re.search(
        r"<!-- ha-marketplace:exclude-start -->\s*\n## Installation\n.*?"
        r"<!-- ha-marketplace:exclude-end -->\s*\n## ",
        text,
        re.DOTALL,
    )
    if not marked:
        r.error(where, "'## Installation' isn't between the ha-marketplace:exclude markers (5.7)")
    likely = re.search(
        r"### Likely to work, not tested\n(.*?)(?=^#|\Z)",
        sections.get("Supported devices", ""),
        re.MULTILINE | re.DOTALL,
    )
    if likely and "CONTRIBUTING.md" not in likely[1]:
        r.error(
            where,
            "'Likely to work, not tested' should link the reporting guide in CONTRIBUTING.md",
        )
    trouble = sections.get("Troubleshooting", "")
    subs = re.findall(r"^### (.+?)\s*$", trouble, re.MULTILINE)
    if not any(s.startswith("Symptom: ") for s in subs):
        r.error(where, "'## Troubleshooting' should describe problems as '### Symptom: ...'")
    if not subs or subs[-1] != "Reporting a problem":
        r.error(where, "'## Troubleshooting' should end with '### Reporting a problem'")
    else:
        last = trouble.split("### Reporting a problem", 1)[1]
        if "CONTRIBUTING.md" not in last or "/issues" not in last:
            r.error(
                where,
                "'Reporting a problem' should link the issue tracker and CONTRIBUTING.md",
            )

    blocks = standard_blocks()
    fill = {"<version>": p.version, "ha-<domain>": p.repo, "<domain>": p.domain}
    body = _norm(text)

    def need(section: str, index: int, label: str, alternative: str | None = None) -> None:
        paragraphs = blocks.get(section, [])
        if index >= len(paragraphs):
            r.error("STANDARD.md", f"standard text {section} not found")
            return
        if any(_pattern(text, fill).search(body) for text in _variants(paragraphs[index])):
            return
        if alternative and alternative in body:
            return
        r.error(where, f"standard text ({section}, {label}) is missing or changed")

    need("5.2", 0, "hobby notice")
    if p.unofficial:
        need("5.2", 1, "unofficial notice")
        if p.cloud:
            notices = blocks.get("5.2", [])
            if not any(_pattern(s, fill).search(body) for s in notices[3:5]):
                r.error(
                    where,
                    "standard text (5.2, how it connects to the service) is missing",
                )
    need("5.2", 2, "no-warranty notice")
    if p.minimum_ha:
        prerequisites = sections.get("Prerequisites", "")
        year_month = ".".join(p.minimum_ha.split(".")[:2])
        if not re.search(rf"\b{re.escape(year_month)}(\.\d+)?\b", prerequisites):
            r.error(
                where,
                f"'## Prerequisites' should give the minimum version, {p.minimum_ha}",
            )
    statement = blocks.get("5.6", [])
    if statement:
        first = statement[0]
        alt_first = re.sub(
            r"^All of the maintainer's code in this integration is written by AI, as part of "
            r"learning when and how\s+AI-written code",
            "This integration is developed with AI assistance, as part of learning when and "
            "how AI-assisted code",
            first,
        )
        if not (_pattern(first, fill).search(body) or _pattern(alt_first, fill).search(body)):
            r.error(where, "standard text (5.6, how it's made) is missing or changed")
    need("5.6", 1, "maintenance", "This integration is no longer actively maintained.")
    need("5.6", 2, "aims, not a guarantee")
    need("5.7", 0, "HACS button")
    need("5.7", 1, "setup button")
    license_paragraphs = blocks.get("5.8", [])
    for i in range(1, len(license_paragraphs)):
        if i == len(license_paragraphs) - 1 and not p.unofficial:
            continue
        need("5.8", i, "license and disclaimer")
    development = sections.get("Development", "")
    if (
        statement
        and not _norm(development).startswith(_norm(statement[0])[:40])
        and not _norm(development).startswith("This integration is developed with AI")
    ):
        r.error(where, "'## Development' should start with the how-it's-made statement")

    badges = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)
    others = [
        b
        for b in badges
        if "my.home-assistant.io/badges" not in b and ("badge" in b or "shields.io" in b)
    ]
    if others:
        r.warn(where, f"badges other than the install buttons: {len(others)}")
    if re.search(r"\bTODO\b", text):
        r.warn(where, "contains TODO, which a release can't have (4.3.4)")
    for name in ["README.md", "CHANGELOG.md"] + [
        f.relative_to(p.root).as_posix() for f in sorted(p.path("docs").rglob("*.md"))
    ]:
        if found := LATIN.search(p.read(name) or ""):
            r.error(
                name,
                f"uses '{found[0]}' (5.9: write 'for example', 'that is' or 'and so on')",
            )


def check_docs(p: Project) -> None:
    r = p.report
    text = p.read("LICENSE")
    if text is not None:
        reference = LICENSE.read_text(encoding="utf-8")
        cut = "END OF TERMS AND CONDITIONS"
        if cut not in text or _norm(text.split(cut)[0]) != _norm(reference.split(cut)[0]):
            r.error("LICENSE", "should be the Apache License 2.0, unmodified")
    text = p.read("NOTICE")
    if text is not None:
        if not re.search(rf"Copyright \d{{4}}(-\d{{4}})? {AUTHOR} and contributors", text):
            r.error("NOTICE", f"needs 'Copyright <year> {AUTHOR} and contributors'")
        if '"AS IS"' not in text or "liab" not in text.lower():
            r.error("NOTICE", "needs the AS IS and no-liability lines")
        if p.unofficial and "trademark" not in text.lower():
            r.error("NOTICE", "needs the trademark paragraph")
        if (
            p.domain
            and p.path(f"custom_components/{p.domain}/brand").is_dir()
            and not re.search(
                r"\b(brand|icon|logo)\b[^.]*\boriginal\b",
                text,
                re.IGNORECASE,
            )
        ):
            r.error("NOTICE", "should say the brand images are original (section 7)")
    text = p.read("CODE_OF_CONDUCT.md")
    if text is not None:
        if "Contributor Covenant 3.0" not in text:
            r.error("CODE_OF_CONDUCT.md", "should be the Contributor Covenant 3.0")
        if "[NOTE:" in text:
            r.error(
                "CODE_OF_CONDUCT.md",
                "still has the Covenant's [NOTE: ...] placeholders",
            )
        if not re.search(r"opensource@[a-z0-9.-]+\.[a-z]{2,}", text):
            r.error(
                "CODE_OF_CONDUCT.md",
                "the reporting contact should be the opensource@ address",
            )
    text = p.read("SECURITY.md")
    if (
        text is not None
        and "security/advisories/new" not in text
        and "Report a vulnerability" not in text
    ):
        r.error("SECURITY.md", "should explain private reporting (Report a vulnerability)")
    text = p.read("CONTRIBUTING.md")
    if text is not None:
        if not re.search(r"^#+ Reporting\s*$", text, re.MULTILINE):
            r.error("CONTRIBUTING.md", "needs a Reporting section")
        if "AI" not in text:
            r.error("CONTRIBUTING.md", "needs the policy on AI-assisted contributions")
        if "Apache" not in text:
            r.error(
                "CONTRIBUTING.md",
                "should say contributions are licensed under the Apache License 2.0",
            )
    text = p.read(".github/pull_request_template.md")
    if text is not None and "AI" not in text:
        r.error(
            ".github/pull_request_template.md",
            "the checklist should ask about AI assistance",
        )
    text = p.read(".github/ISSUE_TEMPLATE/config.yml")
    if text is not None:
        if not re.search(r"^blank_issues_enabled:\s*false", text, re.MULTILINE):
            r.error(
                ".github/ISSUE_TEMPLATE/config.yml",
                "blank_issues_enabled should be false",
            )
        if "security" not in text.lower():
            r.error(
                ".github/ISSUE_TEMPLATE/config.yml",
                "should link private security reporting",
            )
    forms = (
        [f for f in p.path(".github/ISSUE_TEMPLATE").glob("*.y*ml") if f.name != "config.yml"]
        if p.path(".github/ISSUE_TEMPLATE").is_dir()
        else []
    )
    if forms and not any(
        "new or untested model" in f.read_text(encoding="utf-8").lower() for f in forms
    ):
        r.error(
            ".github/ISSUE_TEMPLATE",
            "the bug form needs a 'new or untested model' checkbox",
        )


def check_tests(p: Project) -> None:
    tests = [f for f in p.path("tests").rglob("*.py")] if p.path("tests").is_dir() else []
    conftest = p.read("tests/conftest.py") or ""
    if not tests:
        p.report.error("tests", "no tests")
    elif not (
        "autouse=True" in conftest and "deprecated" in conftest and "used from {DOMAIN}" in conftest
    ):
        p.report.error(
            "tests/conftest.py",
            "needs an autouse fixture that fails tests when Home Assistant reports a "
            "deprecated use, by its frame helper or a deprecated constant (2.6)",
        )
    for name in ("requirements_test.txt", "requirements_ci.txt"):
        for line in (p.read(name) or "").splitlines():
            line = line.split("#", 1)[0].strip()
            if line and not line.startswith("-") and not PINNED.match(line):
                p.report.error(name, f"not pinned exactly: {line}")
    pyproject = p.read("pyproject.toml") or ""
    if re.search(r"exclude_also[^\]]*except ImportError", pyproject, re.DOTALL):
        p.report.error(
            "pyproject.toml",
            "don't exclude every 'except ImportError' from coverage; mark version code (2.7)",
        )


def git(p: Project, *args: str) -> str | None:
    try:
        return subprocess.run(
            ["git", "-C", str(p.root), *args],
            capture_output=True,
            check=True,
            text=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None


def is_maintainer(name: str, email: str) -> bool:
    return name == AUTHOR or bool(
        re.search(rf"\+{OWNER}@users\.noreply\.github\.com$", email, re.IGNORECASE)
    )


def check_history(p: Project) -> None:
    """The maintainer's commits on this branch: noreply address, no trailers, no addresses.

    Commits by contributors and bots (Dependabot signs off its commits) keep their own
    lines and addresses, as section 3 says.
    """
    if git(p, "rev-parse", "--is-shallow-repository") == "true\n":
        p.report.warn("git history", "shallow clone: only part of the history was checked")
    log = git(p, "log", "HEAD", "--format=%H%x1f%an%x1f%ae%x1f%cn%x1f%ce%x1f%B%x1e")
    if log is None:
        p.report.warn("git history", "not a git repository; commits weren't checked")
        return
    for record in filter(None, (r.strip() for r in log.split("\x1e"))):
        sha, author, author_email, committer, committer_email, message = record.split("\x1f", 5)
        where = f"commit {sha[:7]}"
        people = ((author, author_email), (committer, committer_email))
        for name, email in people:
            if name == AUTHOR and not NOREPLY.search(email):
                p.report.error(where, f"{AUTHOR}'s commits should use the noreply address")
        if not is_maintainer(author, author_email):
            continue
        if TRAILER.search(message):
            p.report.error(where, "the message has co-author or other trailer lines (section 3)")
        for match in EMAIL.finditer(message):
            if not ALLOWED_EMAIL.search(match[0]):
                p.report.error(where, "the message has an email address (section 3)")
                break


def check_release(p: Project) -> None:
    """Only when releasing: the audit report for this version (4.3.4)."""
    name = f"docs/audits/{p.version}.md"
    text = p.read(name)
    if text is None:
        p.report.error(name, "missing: every release needs an audit report")
    else:
        for label in AUDIT_HEADER:
            if not re.search(rf"^{re.escape(label)} .+", text, re.MULTILINE):
                p.report.error(name, f"no '{label}' line in the header")
        if not re.search(rf"^Version: {re.escape(p.version)}\s*$", text, re.MULTILINE):
            p.report.error(name, f"doesn't say it audits {p.version}")
        missing = [
            rule
            for names in QUALITY_SCALE.values()
            for rule in names
            if not re.search(rf"(?<![\w-]){re.escape(rule)}(?![\w-])", text)
        ]
        if missing:
            p.report.error(name, f"no verdict for {len(missing)} rule(s), such as {missing[0]}")
        sections = [s for s in standard_sections() if not _section_named(s, text)]
        if sections:
            p.report.error(name, f"no verdict for section(s) {', '.join(sections)} (4.3.4)")
    readme = p.read("README.md") or ""
    if re.search(r"\bTODO\b", readme):
        p.report.error("README.md", "a release can't have TODO left (4.3.4)")


def check_repository(p: Project, files: list[Path]) -> None:
    r = p.report
    text = p.read(".gitignore")
    if text is not None:
        lines = {line.strip() for line in text.splitlines()}
        for pattern in GITIGNORE:
            if pattern not in lines:
                r.error(".gitignore", f"should exclude {pattern}")
    text = p.read(".github/dependabot.yml")
    if text is not None:
        for ecosystem in ("github-actions", "pip"):
            if not re.search(rf"package-ecosystem:\s*[\"']?{ecosystem}", text):
                r.error(".github/dependabot.yml", f"no version updates for {ecosystem}")
    scheduled = False
    for workflow in sorted(p.path(".github/workflows").glob("*.y*ml")):
        where = str(workflow.relative_to(p.root))
        content = workflow.read_text(encoding="utf-8")
        top = re.search(r"^permissions:[ \t]*(\S.*)?\n((?:[ \t]+.*\n)*)", content, re.MULTILINE)
        if top is None:
            r.error(where, "needs top-level permissions (contents: read)")
        else:
            inline, block = (top[1] or "").split("#")[0].strip(), top[2]
            granted = re.findall(r"^\s+[\w-]+:\s*(\w+)", block, re.MULTILINE)
            if inline not in ("", "{}", "read-all") or any(
                g not in ("read", "none") for g in granted
            ):
                r.error(where, "top-level permissions must be read-only (6.2.2)")
        for use in re.findall(r"^\s*-?\s*uses:\s*([^\s#]+)", content, re.MULTILINE):
            if use.startswith(("./", "docker://")):
                continue
            if not re.fullmatch(r"[\w.-]+/[\w./-]+@[0-9a-f]{40}", use):
                r.error(where, f"not pinned to a full commit SHA: {use}")
        scheduled = scheduled or "schedule:" in content
    if not scheduled:
        r.warn(
            ".github/workflows",
            "no scheduled run (weekly against the latest beta, 2.6)",
        )
    pins = {
        name: re.findall(
            r"ha-integration-standards/\.github/workflows/check\.yml@([0-9a-f]{40})", text
        )
        for name in ("standard.yml", "release.yml")
        if (text := p.read(f".github/workflows/{name}") or "")
    }
    if len({sha for found in pins.values() for sha in found}) > 1:
        r.error(".github/workflows", "standard.yml and release.yml pin different commits (8.3)")
    standard = p.read(".github/workflows/standard.yml") or ""
    if standard and "ha-integration-standards/.github/workflows/check.yml@" not in standard:
        r.error(".github/workflows/standard.yml", "doesn't run the standard's shared check")
    release = p.read(".github/workflows/release.yml") or ""
    if release:
        for needed, why in (
            ("release: true", "the standard's release check"),
            ("environment: release", "the release environment (6.2.3)"),
            ("default_branch", "a guard to release only from the default branch"),
            ("tests.yml", "the full tests"),
            ("validate.yml", "hassfest and HACS validation"),
        ):
            if needed not in release:
                r.error(".github/workflows/release.yml", f"doesn't run or set {why} (4.3.1)")

    for path in files:
        rel = path.relative_to(p.root).as_posix()
        for pattern in GITIGNORE:
            if fnmatch.fnmatch(path.name, pattern):
                r.error(rel, "personal data or secrets file is in the repository")
        if path.suffix.lower() in (
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".webp",
            ".ico",
            ".zip",
            ".pyc",
        ):
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if rel == "NOTICE":
            continue  # credit for adapted code may name its author's address (section 3)
        for match in EMAIL.finditer(content):
            address = match[0]
            if address.lower().endswith(NOT_EMAIL_SUFFIX) or ALLOWED_EMAIL.search(address):
                continue
            r.error(rel, "email address that isn't allowed by the standard (section 3)")
            break


def run(root: Path, release: bool = False) -> Report:
    report = Report()
    p = Project(root=root, report=report)
    check_basics(p)
    check_integration(p)
    if p.domain:
        check_hacs(p)
        check_changelog(p)
        check_quality_scale(p)
        check_brand(p)
        check_readme(p)
    check_docs(p)
    check_tests(p)
    check_repository(p, tracked_files(root))
    check_history(p)
    if release and p.domain:
        check_release(p)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("path", nargs="?", default=".", help="the project to check")
    parser.add_argument(
        "--release", action="store_true", help="also check what a release needs (4.3.4)"
    )
    args = parser.parse_args(argv)
    root = Path(args.path).resolve()
    report = run(root, release=args.release)
    github = os.environ.get("GITHUB_ACTIONS") == "true"
    for message in report.errors:
        print(f"::error::{message}" if github else f"error: {message}")
    for message in report.warnings:
        print(f"::warning::{message}" if github else f"warning: {message}")
    print(
        f"Standard {standard_version()}: {len(report.errors)} error(s), "
        f"{len(report.warnings)} warning(s)."
    )
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
