"""Coordinate Buienradar precipitation forecasts for the rain sensor."""

from datetime import timedelta
import logging
from math import isfinite
from typing import Any

from buienradar.constants import PRECIPITATION_FORECAST, TOTAL
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_TIMEFRAME, DEFAULT_TIMEFRAME, SCHEDULE_OK
from .util import BrData

_LOGGER = logging.getLogger(__name__)


class BuienradarRainCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll the existing Buienradar data source without scheduling BrData timers."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the forecast source with the configured timeframe."""
        coordinates = {
            CONF_LATITUDE: entry.data.get(CONF_LATITUDE, hass.config.latitude),
            CONF_LONGITUDE: entry.data.get(CONF_LONGITUDE, hass.config.longitude),
        }
        timeframe = entry.options.get(
            CONF_TIMEFRAME, entry.data.get(CONF_TIMEFRAME, DEFAULT_TIMEFRAME)
        )
        self._source = BrData(hass, coordinates, timeframe, [])
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name="Buienradar rain",
            update_interval=timedelta(minutes=SCHEDULE_OK),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch a forecast or mark the sensor unavailable on invalid data."""
        data = await self._source._async_update()
        forecast = data.get(PRECIPITATION_FORECAST) if isinstance(data, dict) else None
        total = forecast.get(TOTAL) if isinstance(forecast, dict) else None
        if (
            isinstance(total, bool)
            or not isinstance(total, (int, float))
            or not isfinite(total)
            or total < 0
        ):
            raise UpdateFailed("No valid precipitation forecast from Buienradar")
        return data
