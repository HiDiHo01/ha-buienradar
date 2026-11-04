"""Binary precipitation sensors backed by the Buienradar weather feed."""

from __future__ import annotations

import math
from collections.abc import Mapping

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from buienradar.constants import (
    AVERAGE,
    CONDITION,
    DETAILED,
    PRECIPITATION,
    PRECIPITATION_FORECAST,
    TOTAL,
)

from . import BuienRadarConfigEntry
from .util import BrData

BINARY_SENSOR_TYPES: tuple[BinarySensorEntityDescription, ...] = (
    BinarySensorEntityDescription(
        key="precipitation_expected",
        translation_key="precipitation_expected",
        icon="mdi:weather-snowy-rainy",
    ),
    BinarySensorEntityDescription(
        key="currently_raining",
        translation_key="currently_raining",
        icon="mdi:weather-rainy",
    ),
    BinarySensorEntityDescription(
        key="currently_snowing",
        translation_key="currently_snowing",
        icon="mdi:weather-snowy",
    ),
)


def _nonnegative_rate(value: object) -> float | None:
    """Accept only finite nonnegative numeric precipitation measurements."""
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    if not math.isfinite(value) or value < 0:
        return None
    return float(value)


def _precipitation_expected(data: Mapping[str, object]) -> bool | None:
    """Evaluate the configured forecast window, or return unknown data."""
    forecast = data.get(PRECIPITATION_FORECAST)
    if not isinstance(forecast, Mapping):
        return None

    average = _nonnegative_rate(forecast.get(AVERAGE))
    total = _nonnegative_rate(forecast.get(TOTAL))
    if average is None or total is None:
        return None
    return average > 0 or total > 0


def _current_precipitation(data: Mapping[str, object], *, snow: bool) -> bool | None:
    """Use station precipitation and weather type, not forecast summaries."""
    intensity = _nonnegative_rate(data.get(PRECIPITATION))
    if intensity is None:
        return None
    if intensity == 0 and not snow:
        return False

    condition = data.get(CONDITION)
    if not isinstance(condition, Mapping):
        return False if intensity == 0 else None
    general = condition.get(CONDITION)
    detailed = condition.get(DETAILED)
    if not isinstance(general, str) or not isinstance(detailed, str):
        return False if intensity == 0 else None

    has_rain = general == "rainy" or "rain" in detailed
    has_snow = general == "snowy" or "snow" in detailed
    if intensity == 0:
        return has_snow if snow else False
    if not (has_rain or has_snow):
        return None
    return has_snow if snow else has_rain


class BuienradarBinarySensor(BinarySensorEntity):
    """Expose forecast precipitation or current weather-station precipitation."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_available = False
    _attr_is_on = None

    def __init__(
        self,
        entry: BuienRadarConfigEntry,
        description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize a Buienradar binary sensor with a stable entity ID."""
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

    @callback
    def data_updated(self, data: BrData) -> None:
        """Update binary state from the parsed Buienradar response."""
        weather_data = data.data
        state: bool | None = None
        if isinstance(weather_data, Mapping):
            match self.entity_description.key:
                case "precipitation_expected":
                    state = _precipitation_expected(weather_data)
                case "currently_raining":
                    state = _current_precipitation(weather_data, snow=False)
                case "currently_snowing":
                    state = _current_precipitation(weather_data, snow=True)

        self._set_state(state)

    @callback
    def data_update_failed(self) -> None:
        """Invalidate the current state when shared API polling fails."""
        self._set_state(None)

    @callback
    def _set_state(self, state: bool | None) -> None:
        """Publish a validated state and its availability."""
        self._attr_is_on = state
        self._attr_available = state is not None
        if getattr(self, "hass", None) is not None:
            self.async_write_ha_state()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BuienRadarConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Register Buienradar binary sensors with the shared data source."""
    data = entry.runtime_data[Platform.BINARY_SENSOR]
    entities = [
        BuienradarBinarySensor(entry, description)
        for description in BINARY_SENSOR_TYPES
    ]
    data.devices.extend(entities)
    async_add_entities(entities)
