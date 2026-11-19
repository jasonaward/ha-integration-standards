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
    "first_date": "2026-11-19",
}
OWN = {
    "domain": "my_sensor",
    "product": "My Sensor",
    "device": "sensor",
    "description": "My Sensor is a homemade temperature sensor.",
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
    run_copy(str(ROOT), dst, data=answers, defaults=True, unsafe=True, quiet=True, vcs_ref="HEAD")
    brand = dst / "custom_components" / answers["domain"] / "brand"
    brand.mkdir()
    for prefix in ("", "dark_"):
        (brand / f"{prefix}icon.png").write_bytes(_png(256, 256))
        (brand / f"{prefix}icon@2x.png").write_bytes(_png(512, 512))
        (brand / f"{prefix}logo.png").write_bytes(_png(512, 256))
        (brand / f"{prefix}logo@2x.png").write_bytes(_png(1024, 512))
        (dst / "docs" / "brand" / f"{prefix}icon.svg").write_text("<svg/>")
    subprocess.run(["git", "init", "-q", str(dst)], check=True)
    subprocess.run(["git", "-C", str(dst), "add", "-A"], check=True)
    return dst


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
    assert "README.md: contains TODO" in report.warnings


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
    ("README.md", "use it at your own risk", "use it carefully", "5.2, hobby notice"),
    ("README.md", "may not be permitted", "is permitted", "5.2, unofficial notice"),
    ("README.md", "lengthy, iterative process", "quick process", "5.6, how it's made"),
    ("README.md", "even if advised", "unless advised", "5.8"),
    ("README.md", "repository=ha-acme-heater", "repository=ha-other", "5.7, HACS button"),
    ("README.md", "## Use cases", "## Ideas", "missing section '## Use cases'"),
    ("README.md", "### Reporting a problem", "### Getting help", "Reporting a problem"),
    ("CHANGELOG.md", "## 0.1.0b1 (2026-11-19, beta)", "## 0.1.0b1", "heading isn't"),
    ("custom_components/acme_heater/manifest.json", '"0.1.0b1"', '"1.0.0"', "isn't 0.MINOR"),
    ("custom_components/acme_heater/manifest.json", '"@jasonaward"', '"@someone"', "codeowners"),
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
    ("CODE_OF_CONDUCT.md", "Contributor Covenant 3.0", "Our rules", "Contributor Covenant"),
    ("CONTRIBUTING.md", "## Reporting", "## Reports", "Reporting section"),
    ("CONTRIBUTING.md", "Thanks for helping.", "Write to someone@mailhost.test.", "email address"),
    ("hacs.json", '"zip_release": true', '"zip_release": false', "zip_release"),
    ("LICENSE", "Apache License", "Other License", "LICENSE"),
    ("README.md", "### Marketplace or HACS", "### HACS", "Marketplace or HACS"),
    ("tests/conftest.py", "homeassistant.helpers.frame", "logging", "deprecated use"),
    (
        "CHANGELOG.md",
        "- TODO: user-facing changes",
        "- **Entities**: renamed.\n\n**Action needed:** update automations.\n- TODO: user-facing changes",
        "should come first",
    ),
]


@pytest.mark.parametrize(("name", "old", "new", "expected"), BREAKS)
def test_breaking_a_rule_fails(project, name, old, new, expected):
    _edit(project, name, old, new)
    errors = _errors(project)
    assert any(expected in error for error in errors), errors


def test_action_needed_first_passes(project):
    _edit(
        project,
        "CHANGELOG.md",
        "First test release",
        "**Action needed:** reinstall.\n\nFirst test release",
    )
    assert not [e for e in _errors(project) if "Action needed" in e]


def test_versions_must_match(project):
    _edit(project, "custom_components/acme_heater/manifest.json", "0.1.0b1", "0.1.0b2")
    assert any("newest entry should be 0.1.0b2" in e for e in _errors(project))


def test_release_needs_gold(project):
    _edit(project, "custom_components/acme_heater/manifest.json", "0.1.0b1", "0.1.0")
    _edit(project, "CHANGELOG.md", "## 0.1.0b1 (2026-11-19, beta)", "## 0.1.0 (2026-11-19)")
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
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout
    assert "0 error(s)" in result.stdout
