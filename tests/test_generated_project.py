"""A generated project's own tests pass on Home Assistant, and its deprecation fixture works.

Runs only where HA_PYTHON names a Python with Home Assistant's test package installed (the
standard's CI sets it up); elsewhere it's skipped.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
from test_check import VENDOR, _make

HA_PYTHON = os.environ.get("HA_PYTHON")
pytestmark = pytest.mark.skipif(not HA_PYTHON, reason="HA_PYTHON isn't set")


def _pytest(project: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(HA_PYTHON), "-m", "pytest", "-q", "-p", "no:cacheprovider"],
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture(scope="module")
def generated(tmp_path_factory) -> Path:
    return _make(tmp_path_factory.mktemp("generated"), VENDOR)


def test_generated_tests_pass(generated):
    result = _pytest(generated)
    assert result.returncode == 0, result.stdout[-3000:]


def test_deprecated_constant_fails_the_tests(generated, tmp_path):
    """Home Assistant logs a deprecated constant through that module's logger.

    ATTR_VIA_DEVICE is deprecated in the latest release, which CI runs this against.
    """
    import shutil

    project = tmp_path / "copy"
    shutil.copytree(generated, project)
    init = project / "custom_components/acme_heater/__init__.py"
    text = init.read_text()
    marker = "async def async_setup_entry("
    assert marker in text
    init.write_text(
        text.replace(
            marker,
            "async def _use_deprecated() -> None:\n"
            "    from homeassistant import const\n\n"
            "    const.ATTR_VIA_DEVICE  # deprecated in Home Assistant 2026.x\n\n\n" + marker,
        ).replace(
            "    entry.runtime_data",
            "    await _use_deprecated()\n    entry.runtime_data",
            1,
        )
    )
    result = _pytest(project)
    assert result.returncode != 0, result.stdout[-3000:]
    assert "ATTR_VIA_DEVICE" in result.stdout
