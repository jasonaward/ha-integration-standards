"""Home Assistant's test helpers, from whichever test package is installed.

Home Assistant 2026.11 and later: Home Assistant's own pytest-homeassistant. Earlier
versions (for the minimum-version tests): the retired pytest-homeassistant-custom-component.
Tests import helpers from here, for example `from .ha_test import MockConfigEntry`.
"""

from __future__ import annotations

try:  # Home Assistant 2026.11 and later
    from pytest_homeassistant.common import MockConfigEntry, async_fire_time_changed
except ImportError:  # earlier versions
    from pytest_homeassistant_custom_component.common import (  # type: ignore[no-redef]
        MockConfigEntry,
        async_fire_time_changed,
    )

__all__ = ["MockConfigEntry", "async_fire_time_changed"]
