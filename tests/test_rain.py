"""Regression tests for rain setup, forecast handling, and cleanup."""

from importlib import import_module
from types import MappingProxyType, SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from buienradar.constants import PRECIPITATION_FORECAST, TOTAL
import pytest
import pytest_asyncio
from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from custom_components.buienradar import async_setup_entry, async_unload_entry
from custom_components.buienradar.binary_sensor import BuienradarRainSensor
from custom_components.buienradar.const import CONF_TIMEFRAME, DOMAIN
from custom_components.buienradar.rain import BuienradarRainCoordinator
from custom_components.buienradar.util import BrData


@pytest.fixture
def entry():
    """Create a real Home Assistant entry with a nondefault timeframe."""
    return ConfigEntry(
        domain=DOMAIN,
        title="Buienradar",
        data={CONF_LATITUDE: 52.1, CONF_LONGITUDE: 5.1},
        options={CONF_TIMEFRAME: 15},
        source="user",
        unique_id="52.1-5.1",
        version=1,
        minor_version=1,
        discovery_keys=MappingProxyType({}),
        subentries_data=[],
        state=ConfigEntryState.SETUP_IN_PROGRESS,
    )


@pytest_asyncio.fixture
async def hass(tmp_path):
    """Use real coordinator scheduling and a Home Assistant event loop."""
    instance = HomeAssistant(str(tmp_path))
    instance.config_entries = SimpleNamespace(
        async_forward_entry_setups=AsyncMock(),
        async_unload_platforms=AsyncMock(return_value=True),
        async_reload=AsyncMock(),
    )
    yield instance
    for coordinator in instance.data.get(DOMAIN, {}).values():
        await coordinator.async_shutdown()
    await instance.async_stop(force=True)


@pytest.mark.asyncio
async def test_setup_forwards_all_platforms_and_unloads(hass, entry):
    """The public entry setup creates rain and preserves all existing platforms."""
    entities = {}

    async def forward(config_entry, platforms):
        assert hass.data[DOMAIN][entry.entry_id].last_update_success
        for platform in platforms:
            module = import_module(f"custom_components.buienradar.{platform}")
            added = []
            await module.async_setup_entry(hass, config_entry, added.extend)
            entities[platform] = added

    hass.config_entries.async_forward_entry_setups.side_effect = forward
    with patch.object(
        BrData, "_async_update", AsyncMock(return_value={PRECIPITATION_FORECAST: {TOTAL: 0.2}})
    ):
        assert await async_setup_entry(hass, entry)
    assert set(entities) == {
        Platform.BINARY_SENSOR, Platform.CAMERA, Platform.SENSOR, Platform.WEATHER
    }
    sensor = entities[Platform.BINARY_SENSOR][0]
    assert isinstance(sensor, BuienradarRainSensor)
    assert sensor.is_on and sensor.available
    assert sensor.unique_id == f"{entry.entry_id}_rain"
    coordinator = hass.data[DOMAIN][entry.entry_id]
    assert coordinator._source.timeframe == 15
    assert coordinator._source.coordinates == entry.data
    sensor.hass = hass
    sensor.entity_id = "binary_sensor.buienradar_rain"
    sensor.async_write_ha_state = Mock()
    await sensor.async_added_to_hass()
    coordinator.async_set_updated_data({PRECIPITATION_FORECAST: {TOTAL: 0}})
    assert not sensor.is_on
    sensor.async_write_ha_state.assert_called_once()
    assert coordinator._listeners

    # Mimic HA removing the platform entity, which unsubscribes the coordinator.
    async def unload(config_entry, platforms):
        sensor._call_on_remove_callbacks()
        return True

    hass.config_entries.async_unload_platforms.side_effect = unload
    timers = [data.unsub_schedule_update for data in entry.runtime_data.values()]
    assert timers and all(timers)
    assert await async_unload_entry(hass, entry)
    assert entry.entry_id not in hass.data[DOMAIN]
    assert not coordinator._listeners
    assert coordinator._unsub_refresh is None
    await coordinator.async_shutdown()


@pytest.mark.asyncio
@pytest.mark.parametrize("total, expected", [(0, False), (0.1, True)])
async def test_rain_state(hass, entry, total, expected):
    """Dry and wet forecasts produce the documented binary state."""
    coordinator = BuienradarRainCoordinator(hass, entry)
    try:
        coordinator.async_set_updated_data({PRECIPITATION_FORECAST: {TOTAL: total}})
        sensor = BuienradarRainSensor(coordinator, entry)
        assert sensor.is_on is expected
        assert sensor.available
    finally:
        await coordinator.async_shutdown()


@pytest.mark.asyncio
@pytest.mark.parametrize("forecast", [None, {}, {TOTAL: None}, {TOTAL: -1}, {TOTAL: float("nan")}])
async def test_bad_initial_forecast_retries_before_forwarding(hass, entry, forecast):
    """Failed or malformed initial data cannot create a falsely dry sensor."""
    data = {PRECIPITATION_FORECAST: forecast} if forecast is not None else None
    with patch.object(BrData, "_async_update", AsyncMock(return_value=data)):
        with pytest.raises(ConfigEntryNotReady):
            await async_setup_entry(hass, entry)
    hass.config_entries.async_forward_entry_setups.assert_not_awaited()
    assert entry.entry_id not in hass.data.get(DOMAIN, {})


@pytest.mark.asyncio
async def test_failed_refresh_marks_unavailable_and_recovers(hass, entry):
    """A later outage does not leave a rain entity available with stale data."""
    coordinator = BuienradarRainCoordinator(hass, entry)
    try:
        coordinator.async_set_updated_data({PRECIPITATION_FORECAST: {TOTAL: 0.2}})
        sensor = BuienradarRainSensor(coordinator, entry)
        with patch.object(BrData, "_async_update", AsyncMock(return_value=None)):
            await coordinator.async_refresh()
        assert not sensor.available
        with patch.object(
            BrData, "_async_update", AsyncMock(return_value={PRECIPITATION_FORECAST: {TOTAL: 0}})
        ):
            await coordinator.async_refresh()
        assert sensor.available and not sensor.is_on
    finally:
        await coordinator.async_shutdown()


@pytest.mark.asyncio
async def test_failed_unload_retains_data(hass, entry):
    """An unload refusal leaves the active entry's coordinator and timers intact."""
    with patch.object(
        BrData, "_async_update", AsyncMock(return_value={PRECIPITATION_FORECAST: {TOTAL: 0}})
    ):
        assert await async_setup_entry(hass, entry)
    cancel = Mock()
    entry.runtime_data[Platform.SENSOR] = SimpleNamespace(unsub_schedule_update=cancel)
    hass.config_entries.async_unload_platforms.return_value = False
    assert not await async_unload_entry(hass, entry)
    cancel.assert_not_called()
    assert entry.entry_id in hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_shared_loader_uses_pinned_parser_contract(hass):
    """The real pinned parser accepts the shared loader's arguments."""
    source = BrData(hass, {CONF_LATITUDE: 52.1, CONF_LONGITUDE: 5.1}, 15, [])
    source.get_data = AsyncMock(return_value={"success": True, "content": "{}"})
    # Invalid weather data returns None; an unsupported keyword would raise TypeError.
    assert await source._async_update() is None
