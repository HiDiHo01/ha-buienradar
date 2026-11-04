"""The buienradar integration."""

from __future__ import annotations

import math

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, Platform
from homeassistant.core import HomeAssistant

from .const import CONF_TIMEFRAME, DEFAULT_TIMEFRAME
from .util import BrData

PLATFORMS = [Platform.BINARY_SENSOR, Platform.CAMERA, Platform.SENSOR, Platform.WEATHER]

type BuienRadarConfigEntry = ConfigEntry[dict[Platform, BrData]]


def _create_shared_data(hass: HomeAssistant, entry: BuienRadarConfigEntry) -> BrData:
    """Create one weather-data source for all non-camera platforms."""
    config = entry.data
    latitude = config.get(CONF_LATITUDE, hass.config.latitude)
    longitude = config.get(CONF_LONGITUDE, hass.config.longitude)

    try:
        latitude_value = float(latitude)
        longitude_value = float(longitude)
    except (ValueError, TypeError, OverflowError) as err:
        raise ValueError(
            "Buienradar requires valid latitude and longitude coordinates"
        ) from err

    if (
        not math.isfinite(latitude_value)
        or not -90 <= latitude_value <= 90
        or not math.isfinite(longitude_value)
        or not -180 <= longitude_value <= 180
    ):
        raise ValueError("Buienradar coordinates must be finite and within range")

    raw_timeframe = entry.options.get(
        CONF_TIMEFRAME, config.get(CONF_TIMEFRAME, DEFAULT_TIMEFRAME)
    )
    try:
        timeframe = int(raw_timeframe)
    except (TypeError, ValueError, OverflowError):
        timeframe = DEFAULT_TIMEFRAME
    if not 5 <= timeframe <= 120:
        timeframe = DEFAULT_TIMEFRAME

    coordinates = {CONF_LATITUDE: latitude_value, CONF_LONGITUDE: longitude_value}
    return BrData(hass, coordinates, timeframe, [])


async def async_setup_entry(hass: HomeAssistant, entry: BuienRadarConfigEntry) -> bool:
    """Set up all platforms with one shared weather-data polling source."""
    shared_data = _create_shared_data(hass, entry)
    entry.runtime_data = {
        Platform.BINARY_SENSOR: shared_data,
        Platform.SENSOR: shared_data,
        Platform.WEATHER: shared_data,
    }
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await shared_data.async_update()
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: BuienRadarConfigEntry) -> bool:
    """Unload platforms and cancel each shared polling timer exactly once."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        seen_data_ids: set[int] = set()
        for data in entry.runtime_data.values():
            if id(data) in seen_data_ids:
                continue
            seen_data_ids.add(id(data))
            if unsub := data.unsub_schedule_update:
                unsub()
    return unload_ok


async def async_update_options(
    hass: HomeAssistant, config_entry: BuienRadarConfigEntry
) -> None:
    """Update options."""
    await hass.config_entries.async_reload(config_entry.entry_id)
