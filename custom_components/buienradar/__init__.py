"""The buienradar integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .rain import BuienradarRainCoordinator
from .util import BrData

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.CAMERA,
    Platform.SENSOR,
    Platform.WEATHER,
]

type BuienRadarConfigEntry = ConfigEntry[dict[Platform, BrData]]


async def async_setup_entry(hass: HomeAssistant, entry: BuienRadarConfigEntry) -> bool:
    """Set up buienradar from a config entry."""
    entry.runtime_data = {}
    coordinator = BuienradarRainCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: BuienRadarConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        for platform in PLATFORMS:
            if (data := entry.runtime_data.get(platform)) and (
                unsub := data.unsub_schedule_update
            ):
                unsub()
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok


async def async_update_options(
    hass: HomeAssistant, config_entry: BuienRadarConfigEntry
) -> None:
    """Update options."""
    await hass.config_entries.async_reload(config_entry.entry_id)
