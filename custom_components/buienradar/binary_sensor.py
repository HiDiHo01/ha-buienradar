"""Rain detection using Buienradar precipitation forecasts."""

from buienradar.constants import PRECIPITATION_FORECAST, TOTAL
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import BuienRadarConfigEntry
from .const import DOMAIN
from .rain import BuienradarRainCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BuienRadarConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the rain sensor with the coordinator prepared by the integration."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([BuienradarRainSensor(coordinator, entry)])


class BuienradarRainSensor(
    CoordinatorEntity[BuienradarRainCoordinator], BinarySensorEntity
):
    """Indicate precipitation within the configured forecast timeframe."""

    _attr_name = "Buienradar rain"
    _attr_icon = "mdi:weather-rainy"

    def __init__(
        self, coordinator: BuienradarRainCoordinator, entry: BuienRadarConfigEntry
    ) -> None:
        """Initialize the rain sensor with a stable ID for the config entry."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_rain"

    @property
    def is_on(self) -> bool:
        """Return whether precipitation is forecast in the configured window."""
        return self.coordinator.data[PRECIPITATION_FORECAST][TOTAL] > 0
