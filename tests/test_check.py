"""The check and the template agree: a project made from the template passes the check
(once it has brand images), and breaking a rule makes the check fail."""

from __future__ import annotations

import shutil
import struct
import subprocess
import sys
import zlib
from pathlib import Path

import pytest
from copier import run_copy

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "check"))

import check_standard  # noqa: E402

VENDOR = {
    "domain": "acme_heater",
    "product": "Acme Heater",
    "company": "Acme",
    "trademarks": "Acme and HeatPro",
    "device": "heater",
    "equipment": "heaters, pool equipment",
    "description": "The Acme Heater is a pool heater with Wi-Fi.",
    "website": "https://www.acme.example",
    "first_date": "2026-11-19",
}
OWN = {
    "domain": "my_sensor",
    "product": "My Sensor",
    "device": "sensor",
    "description": "My Sensor is a homemade temperature sensor.",
    "website": "https://sensor.example",
    "iot_class": "local_polling",
    "first_date": "2026-11-19",
}


def _png(width: int, height: int) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
        )

    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    rows = b"".join(b"\0" + b"\0\0\0\0" * width for _ in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(rows))
        + chunk(b"IEND", b"")
    )


def _make(tmp_path: Path, answers: dict[str, str]) -> Path:
    dst = tmp_path / "project"
    run_copy(
        str(ROOT),
        dst,
        data=answers,
        defaults=True,
        unsafe=True,
        quiet=True,
        vcs_ref="HEAD",
    )
    brand = dst / "custom_components" / answers["domain"] / "brand"
    brand.mkdir()
    for prefix in ("", "dark_"):
        (brand / f"{prefix}icon.png").write_bytes(_png(256, 256))
        (brand / f"{prefix}icon@2x.png").write_bytes(_png(512, 512))
        (brand / f"{prefix}logo.png").write_bytes(_png(512, 256))
        (brand / f"{prefix}logo@2x.png").write_bytes(_png(1024, 512))
        (dst / "docs" / "brand" / f"{prefix}icon.svg").write_text("<svg/>")
    _git(dst, "init", "-q")
    _git(dst, "add", "-A")
    _git(dst, "commit", "-q", "-m", "First commit")
    return dst


def _git(path: Path, *args: str) -> None:
    identity = ["-c", "user.name=Jason Ward", "-c", f"user.email={NOREPLY}"]
    subprocess.run(["git", *identity, "-C", str(path), *args], check=True)


NOREPLY = "1+jasonaward@users.noreply.github.com"


@pytest.fixture(scope="module")
def vendor(tmp_path_factory) -> Path:
    return _make(tmp_path_factory.mktemp("vendor"), VENDOR)


@pytest.fixture
def project(vendor, tmp_path) -> Path:
    copy = tmp_path / "copy"
    shutil.copytree(vendor, copy)
    return copy


def _errors(path: Path) -> list[str]:
    return check_standard.run(path).errors


def _edit(path: Path, name: str, old: str, new: str) -> None:
    file = path / name
    text = file.read_text(encoding="utf-8")
    assert old in text, f"{old!r} not in {name}"
    file.write_text(text.replace(old, new, 1), encoding="utf-8")


def test_vendor_project_passes(vendor):
    report = check_standard.run(vendor)
    assert report.errors == []
    assert any(w.startswith("README.md: contains TODO") for w in report.warnings)


def test_own_product_passes(tmp_path):
    project = _make(tmp_path, OWN)
    assert _errors(project) == []
    readme = (project / "README.md").read_text(encoding="utf-8")
    assert "**Unofficial.**" not in readme
    assert "## Load on" not in readme


def test_template_license_is_the_standards_license():
    assert (ROOT / "template" / "LICENSE").read_bytes() == (ROOT / "LICENSE").read_bytes()


def test_template_standard_version_matches():
    assert (ROOT / "template" / ".standard-version").read_text().strip() == (
        check_standard.standard_version()
    )


BREAKS = [
    ("README.md", "offered as is", "offered freely", "5.2, hobby notice"),
    ("README.md", "may not be permitted", "is permitted", "5.2, how it connects"),
    ("README.md", "used here only to say", "used to say", "5.2, unofficial notice"),
    ("README.md", "lengthy, iterative process", "quick process", "5.6, how it's made"),
    ("README.md", "even if advised", "unless advised", "5.8"),
    (
        "README.md",
        "repository=ha-acme-heater",
        "repository=ha-other",
        "5.7, HACS button",
    ),
    ("README.md", "## Use cases", "## Ideas", "missing section '## Use cases'"),
    ("README.md", "### Reporting a problem", "### Getting help", "Reporting a problem"),
    ("CHANGELOG.md", "## 0.1.0b1 (2026-11-19, beta)", "## 0.1.0b1", "heading isn't"),
    (
        "custom_components/acme_heater/manifest.json",
        '"0.1.0b1"',
        '"1.0.0"',
        "isn't 0.MINOR",
    ),
    (
        "custom_components/acme_heater/manifest.json",
        '"@jasonaward"',
        '"@someone"',
        "codeowners",
    ),
    (
        "custom_components/acme_heater/quality_scale.yaml",
        "  config-flow: done\n",
        "",
        "config-flow isn't listed",
    ),
    (
        ".github/workflows/tests.yml",
        "@3d3c42e5aac5ba805825da76410c181273ba90b1",
        "@v7",
        "not pinned",
    ),
    (".github/ISSUE_TEMPLATE/config.yml", "false", "true", "blank_issues_enabled"),
    (".gitignore", "*.har\n", "", "should exclude *.har"),
    ("NOTICE", "Jason Ward and contributors", "Someone", "Copyright"),
    (
        "CODE_OF_CONDUCT.md",
        "Contributor Covenant 3.0",
        "Our rules",
        "Contributor Covenant",
    ),
    ("CONTRIBUTING.md", "## Reporting", "## Reports", "Reporting section"),
    (
        "CONTRIBUTING.md",
        "Thanks for helping.",
        "Write to someone@mailhost.test.",
        "email address",
    ),
    ("hacs.json", '"zip_release": true', '"zip_release": false', "zip_release"),
    ("LICENSE", "Apache License", "Other License", "LICENSE"),
    ("README.md", "### Marketplace or HACS", "### HACS", "Marketplace or HACS"),
    ("tests/conftest.py", "used from {DOMAIN}", "called from {DOMAIN}", "deprecated use"),
    (
        "CHANGELOG.md",
        "- **TODO**: user-facing changes",
        (
            "- **Entities**: renamed.\n- **Action needed:** update automations.\n- **TODO**: "
            "user-facing changes"
        ),
        "should be the first bullet",
    ),
    ("CHANGELOG.md", "- **First test release**", "First test release", "only bullets"),
    ("README.md", "See [Acme's website](https://www.acme.example).", "", "website"),
    ("README.md", "### Symptom: ", "### Problem: ", "Symptom"),
    ("requirements_ci.txt", "pytest-cov==7.1.0", "pytest-cov", "not pinned exactly"),
    ("hacs.json", '"hide_default_branch": true', '"hide_default_branch": false', "hide_default"),
    ("hacs.json", '"2026.3.0"', '"2025.12.0"', "at least 2026.3.0"),
    ("README.md", "Home Assistant 2026.3 or later", "Home Assistant", "minimum version"),
    ("README.md", "a pool heater with Wi-Fi.", "a pool heater, e.g. a big one.", "e.g."),
    ("README.md", "a pool heater with Wi-Fi.", "a heater, pump, etc.", "etc."),
    ("NOTICE", "original artwork", "artwork", "brand images are original"),
    (".standard-version", "0.2.0", "0.1.0", "change the two together"),
    (
        "pyproject.toml",
        '"if TYPE_CHECKING:"]',
        '"if TYPE_CHECKING:", "except ImportError:"]',
        "mark version code",
    ),
    (
        ".github/workflows/release.yml",
        "environment: release",
        "environment: other",
        "release environment",
    ),
    (".github/workflows/release.yml", "default_branch", "any_branch", "default branch"),
    (
        ".github/workflows/release.yml",
        "uses: ./.github/workflows/tests.yml",
        "run: echo",
        "full tests",
    ),
    (
        "CHANGELOG.md",
        "## 0.1.0b1 (2026-11-19, beta)",
        "## 0.1.0b1 (2026-11-19, beta)\n\n- **x**: y.\n\n## 0.1.0b2 (2026-11-20, beta)",
        "newest first",
    ),
    (
        "custom_components/acme_heater/quality_scale.yaml",
        "  strict-typing:\n    status: todo",
        "  strict-typing:\n    status: todo",
        None,
    ),
]


@pytest.mark.parametrize(("name", "old", "new", "expected"), BREAKS)
def test_breaking_a_rule_fails(project, name, old, new, expected):
    _edit(project, name, old, new)
    if expected is None:  # a should rule: a warning, not an error
        report = check_standard.run(project)
        assert report.errors == []
        assert report.warnings
        return
    errors = _errors(project)
    assert any(expected in error for error in errors), errors


def test_strings_json_fails(project):
    (project / "custom_components/acme_heater/strings.json").write_text("{}")
    assert any("strings.json" in e for e in _errors(project))


def test_bundled_library_fails(project):
    library = project / "custom_components/acme_heater/pyacme"
    library.mkdir()
    (library / "__init__.py").write_text('__version__ = "0.1.0"\n')
    assert any("bundled client library" in e for e in _errors(project))


def test_polling_option_fails(project):
    flow = project / "custom_components/acme_heater/config_flow.py"
    flow.write_text(flow.read_text() + '\nCONF_SCAN_INTERVAL = "scan_interval"\n')
    assert any("appropriate-polling" in e for e in _errors(project))


def test_commit_trailers_fail(project):
    (project / "x.txt").write_text("x")
    _git(project, "add", "x.txt")
    _git(
        project,
        "commit",
        "-q",
        "-m",
        "Change\n\nCo-Authored-By: Someone <a@mailhost.test>",
    )
    errors = _errors(project)
    assert any("trailer" in e for e in errors), errors
    assert any("email address" in e for e in errors), errors


def test_maintainer_commits_use_noreply(project):
    (project / "x.txt").write_text("x")
    subprocess.run(
        ["git", "-c", "user.name=Jason Ward", "-c", "user.email=jason@mailhost.test",
         "-C", str(project), "commit", "-q", "-am", "x", "--allow-empty"],
        check=True,
    )  # fmt: skip
    assert any("noreply address" in e for e in _errors(project))


def _audit_report(version: str = "0.1.0b1", rules: list[str] | None = None) -> str:
    if rules is None:
        rules = [rule for names in check_standard.QUALITY_SCALE.values() for rule in names]
    header = (
        f"# Audit of {version}\n\nVersion: {version}\nStandard: 0.2.0\nDate: 2026-11-26\n"
        "Reviewer: an AI agent without the author's context\nContext: the repository only\n\n"
    )
    return header + "".join(f"- {rule}: done. Evidence.\n" for rule in rules)


def _no_todo(project: Path) -> None:
    readme = project / "README.md"
    readme.write_text(readme.read_text().replace("TODO", "Filled in"))


def test_release_needs_the_audit_report(project):
    _no_todo(project)
    errors = check_standard.run(project, release=True).errors
    assert any("audit report" in e for e in errors), errors
    (project / "docs/audits/0.1.0b1.md").write_text(_audit_report())
    assert check_standard.run(project, release=True).errors == []


def test_audit_report_needs_its_header_and_every_rule(project):
    _no_todo(project)
    report = project / "docs/audits/0.1.0b1.md"
    report.write_text("# Audit of 0.1.0b1\n")
    errors = check_standard.run(project, release=True).errors
    assert any("'Reviewer:'" in e for e in errors), errors
    report.write_text(_audit_report(rules=["brands"]))
    errors = check_standard.run(project, release=True).errors
    assert any("no verdict for 53 rule(s)" in e for e in errors), errors
    report.write_text(_audit_report(version="0.1.0b0"))
    errors = check_standard.run(project, release=True).errors
    assert any("doesn't say it audits 0.1.0b1" in e for e in errors), errors


def test_release_has_no_todo(project):
    (project / "docs/audits/0.1.0b1.md").write_text(_audit_report())
    errors = check_standard.run(project, release=True).errors
    assert any("TODO" in e for e in errors), errors


def test_bot_and_contributor_commits_keep_their_lines(project):
    """Dependabot signs off; contributors may add co-authors (section 3)."""
    for name, email, message in (
        (
            "dependabot[bot]",
            "49699333+dependabot[bot]@users.noreply.github.com",
            "Bump x\n\nSigned-off-by: dependabot[bot] <support@github.com>",
        ),
        (
            "A Contributor",
            "contributor@mailhost.test",
            "Fix y\n\nCo-authored-by: Friend <friend@mailhost.test>",
        ),
    ):
        subprocess.run(
            ["git", "-c", f"user.name={name}", "-c", f"user.email={email}",
             "-C", str(project), "commit", "-q", "--allow-empty", "-m", message],
            check=True,
        )  # fmt: skip
    assert _errors(project) == []


def test_other_branches_arent_checked(project):
    _git(project, "checkout", "-q", "-b", "elsewhere")
    _git(project, "commit", "-q", "--allow-empty", "-m", "x\n\nClaude-Session: abc")
    _git(project, "checkout", "-q", "-")
    assert _errors(project) == []


def test_empty_readme_is_an_error_not_a_crash(project):
    (project / "README.md").write_text("")
    assert any("README.md: empty" in e for e in _errors(project))


def test_missing_workflow_fails(project):
    (project / ".github/workflows/codeql.yml").unlink()
    assert any("codeql.yml: missing" in e for e in _errors(project))


def test_changelog_order(project):
    _edit(
        project,
        "CHANGELOG.md",
        "## 0.1.0b1 (2026-11-19, beta)",
        "## 0.1.0b0 (2026-11-20, beta)\n\n- **x**: y.\n\n## 0.1.0b1 (2026-11-19, beta)",
    )
    _edit(project, "custom_components/acme_heater/manifest.json", "0.1.0b1", "0.1.0b0")
    errors = _errors(project)
    assert any("newest first" in e or "isn't 0.MINOR" in e for e in errors), errors


def test_changelog_order_by_version():
    key = check_standard.version_key
    assert key("0.1.0b1") < key("0.1.0b2") < key("0.1.0") < key("0.1.1b1") < key("0.2.0")


def test_notice_may_credit_an_address(project):
    _edit(
        project,
        "NOTICE",
        "Jason Ward and contributors",
        "Jason Ward and contributors\n\nAdapts code by A Person <person@mailhost.test>",
    )
    assert _errors(project) == []


def test_local_device_of_another_company(tmp_path):
    """5.2: no connection sentence and no load section for a local device."""
    project = _make(tmp_path, {**VENDOR, "iot_class": "local_polling"})
    assert _errors(project) == []
    readme = (project / "README.md").read_text(encoding="utf-8")
    assert "**Unofficial.**" in readme
    assert "## Load on" not in readme
    assert "terms of service" not in readme.split("## Use cases")[0]


def test_public_interface(tmp_path):
    project = _make(tmp_path, {**VENDOR, "service_interface": "public"})
    assert _errors(project) == []
    readme = (project / "README.md").read_text(encoding="utf-8")
    assert "public interface, so it can stop working" in readme
    assert "the way Acme's app does" not in readme


def test_action_needed_first_passes(project):
    _edit(
        project,
        "CHANGELOG.md",
        "- **First test release**",
        "- **Action needed:** reinstall.\n- **First test release**",
    )
    assert not [e for e in _errors(project) if "Action needed" in e]


def test_versions_must_match(project):
    _edit(project, "custom_components/acme_heater/manifest.json", "0.1.0b1", "0.1.0b2")
    assert any("newest entry should be 0.1.0b2" in e for e in _errors(project))


def test_release_needs_gold(project):
    _edit(project, "custom_components/acme_heater/manifest.json", "0.1.0b1", "0.1.0")
    _edit(
        project,
        "CHANGELOG.md",
        "## 0.1.0b1 (2026-11-19, beta)",
        "## 0.1.0 (2026-11-19)",
    )
    assert any("a release needs Gold" in e for e in _errors(project))


def test_secrets_files_fail(project):
    (project / "capture.har").write_text("{}")
    subprocess.run(["git", "-C", str(project), "add", "-f", "capture.har"], check=True)
    assert any("capture.har" in e for e in _errors(project))


def test_brand_image_size(project):
    icon = project / "custom_components/acme_heater/brand/icon.png"
    icon.write_bytes(_png(300, 300))
    assert any("256×256" in e for e in _errors(project))


def test_command_line(vendor):
    result = subprocess.run(
        [sys.executable, str(ROOT / "check" / "check_standard.py"), str(vendor)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout
    assert "0 error(s)" in result.stdout
