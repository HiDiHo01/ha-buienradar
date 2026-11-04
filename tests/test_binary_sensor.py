"""Regression tests for the Buienradar binary sensor platform."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, call

import pytest
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, Platform

from custom_components.buienradar.const import SCHEDULE_NOK, SCHEDULE_OK
from custom_components.buienradar.util import BrData

from custom_components.buienradar.binary_sensor import (
    BINARY_SENSOR_TYPES,
    BuienradarBinarySensor,
    _current_precipitation,
    _precipitation_expected,
    async_setup_entry,
)


@pytest.mark.parametrize(
    ("forecast", "expected"),
    [
        ({"average": 0.2, "total": 0.0}, True),
        ({"average": 0.0, "total": 0.1}, True),
        ({"average": 0.0, "total": 0.0}, False),
        ({"average": None, "total": 0.1}, None),
        ({"average": float("nan"), "total": 0.1}, None),
        ({"average": 0.1, "total": float("inf")}, None),
        ({"average": -1, "total": 1}, None),
    ],
)
def test_precipitation_expected(
    forecast: dict[str, object], expected: bool | None
) -> None:
    """Preserve unknown measurements instead of reporting false dryness."""
    assert _precipitation_expected({"precipitation_forecast": forecast}) is expected


@pytest.mark.parametrize(
    ("weather_data", "snow", "expected"),
    [
        ({"precipitation": 0}, False, False),
        ({"precipitation": 0}, True, False),
        (
            {
                "precipitation": 0,
                "condition": {"condition": "snowy", "detailed": "snowy"},
            },
            True,
            True,
        ),
        (
            {
                "precipitation": 0,
                "condition": {"condition": "snowy", "detailed": "snowy"},
            },
            False,
            False,
        ),
        (
            {
                "precipitation": 0.5,
                "condition": {"condition": "rainy", "detailed": "rainy"},
            },
            False,
            True,
        ),
        (
            {
                "precipitation": 0.5,
                "condition": {"condition": "rainy", "detailed": "rainy"},
            },
            True,
            False,
        ),
        (
            {
                "precipitation": 0.5,
                "condition": {"condition": "snowy", "detailed": "snowy"},
            },
            True,
            True,
        ),
        (
            {
                "precipitation": 0.5,
                "condition": {"condition": "rainy", "detailed": "snowy-rainy"},
            },
            False,
            True,
        ),
        (
            {
                "precipitation": 0.5,
                "condition": {"condition": "rainy", "detailed": "snowy-rainy"},
            },
            True,
            True,
        ),
        ({"precipitation": 0.5}, False, None),
        (
            {
                "precipitation": 0.5,
                "condition": {"condition": "cloudy", "detailed": "cloudy"},
            },
            False,
            None,
        ),
        ({"precipitation": float("nan")}, False, None),
        ({"precipitation": -0.5}, False, None),
    ],
)
def test_current_precipitation(
    weather_data: dict[str, object], snow: bool, expected: bool | None
) -> None:
    """Identify rain and snow only with valid station observations."""
    assert _current_precipitation(weather_data, snow=snow) is expected

@pytest.mark.parametrize(
    ("sensor_key", "expected_icon"),
    [
        ("precipitation_expected", "mdi:weather-snowy-rainy"),
        ("currently_raining", "mdi:weather-rainy"),
        ("currently_snowing", "mdi:weather-snowy"),
    ],
)
def test_binary_sensor_icons(sensor_key: str, expected_icon: str) -> None:
    """Keep descriptive MDI icons on all Buienradar binary sensors."""
    description = next(
        description for description in BINARY_SENSOR_TYPES if description.key == sensor_key
    )
    assert description.icon == expected_icon


def test_binary_sensor_initially_unavailable_and_updates() -> None:
    """Track data availability and keep the entry's unique identifiers."""
    entry = SimpleNamespace(entry_id="example")
    entity = BuienradarBinarySensor(entry, BINARY_SENSOR_TYPES[0])
    assert entity.unique_id == "example_precipitation_expected"
    assert not entity.available

    entity.data_updated(
        SimpleNamespace(data={"precipitation_forecast": {"average": 0.1, "total": 0.1}})
    )
    assert entity.available
    assert entity.is_on

    entity.data_updated(SimpleNamespace(data={"precipitation_forecast": None}))
    assert not entity.available
    assert entity.is_on is None


@pytest.mark.asyncio
async def test_setup_entry_uses_shared_data() -> None:
    """Register binary sensors without starting a second API polling loop."""
    shared_data = SimpleNamespace(devices=[], async_update=AsyncMock())
    entry = SimpleNamespace(
        entry_id="example",
        runtime_data={Platform.BINARY_SENSOR: shared_data},
    )
    entities_added: list[object] = []

    await async_setup_entry(None, entry, entities_added.extend)

    assert len(entities_added) == 3
    assert shared_data.devices == entities_added
    shared_data.async_update.assert_not_awaited()


@pytest.mark.asyncio
async def test_all_weather_platforms_share_one_data_source() -> None:
    """Register numeric, weather and binary entities on the same source."""
    from custom_components.buienradar import sensor, weather

    coordinates = {CONF_LATITUDE: 52.0, CONF_LONGITUDE: 5.0}
    shared_data = SimpleNamespace(coordinates=coordinates, devices=[])
    entry = SimpleNamespace(
        entry_id="example",
        data={"name": "Buienradar"},
        runtime_data={
            Platform.BINARY_SENSOR: shared_data,
            Platform.SENSOR: shared_data,
            Platform.WEATHER: shared_data,
        },
    )
    numeric_entities: list[object] = []
    weather_entities: list[object] = []
    binary_entities: list[object] = []

    await sensor.async_setup_entry(None, entry, numeric_entities.extend)
    await weather.async_setup_entry(None, entry, weather_entities.extend)
    await async_setup_entry(None, entry, binary_entities.extend)

    assert shared_data.devices == (
        numeric_entities + weather_entities + binary_entities
    )
    assert len(binary_entities) == 3


@pytest.mark.asyncio
async def test_parent_entry_setup_polls_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """Initialize the shared source before forwarding and poll it once."""
    from custom_components import buienradar as integration

    shared_data = SimpleNamespace(async_update=AsyncMock())
    monkeypatch.setattr(
        integration, "_create_shared_data", lambda _hass, _entry: shared_data
    )
    forward = AsyncMock()
    hass = SimpleNamespace(
        config_entries=SimpleNamespace(async_forward_entry_setups=forward)
    )
    entry = SimpleNamespace(
        runtime_data={},
        add_update_listener=MagicMock(),
        async_on_unload=MagicMock(),
    )

    assert await integration.async_setup_entry(hass, entry)
    assert entry.runtime_data[Platform.BINARY_SENSOR] is shared_data
    assert entry.runtime_data[Platform.SENSOR] is shared_data
    assert entry.runtime_data[Platform.WEATHER] is shared_data
    forward.assert_awaited_once_with(entry, integration.PLATFORMS)
    shared_data.async_update.assert_awaited_once()


@pytest.mark.asyncio
async def test_binary_state_recovery_after_api_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Invalidate stale values after failed polling and recover on success."""
    entry = SimpleNamespace(entry_id="example")
    sensor = BuienradarBinarySensor(entry, BINARY_SENSOR_TYPES[0])
    data = BrData(
        None, {CONF_LATITUDE: 52.0, CONF_LONGITUDE: 5.0}, 60, [sensor]
    )
    responses = iter(
        [
            {"precipitation_forecast": {"average": 0.1, "total": 0.1}},
            None,
            {"precipitation_forecast": {"average": 0.0, "total": 0.0}},
        ]
    )

    async def fake_refresh() -> dict[str, object] | None:
        """Return success, failure, and recovery payloads in order."""
        return next(responses)

    schedule_update = MagicMock()
    monkeypatch.setattr(data, "_async_update", fake_refresh)
    monkeypatch.setattr(data, "async_schedule_update", schedule_update)

    await data.async_update()
    assert data.last_update_success
    assert sensor.available and sensor.is_on is True

    await data.async_update()
    assert not data.last_update_success
    assert not sensor.available
    assert sensor.is_on is None

    await data.async_update()
    assert data.last_update_success
    assert sensor.available and sensor.is_on is False
    assert schedule_update.call_args_list == [
        call(SCHEDULE_OK),
        call(SCHEDULE_NOK),
        call(SCHEDULE_OK),
    ]


@pytest.mark.asyncio
async def test_unload_cancels_shared_timer_once() -> None:
    """Avoid unsubscribing the same BrData timer three times."""
    from custom_components import buienradar as integration

    unsub = MagicMock()
    shared_data = SimpleNamespace(unsub_schedule_update=unsub)
    hass = SimpleNamespace(
        config_entries=SimpleNamespace(
            async_unload_platforms=AsyncMock(return_value=True)
        )
    )
    entry = SimpleNamespace(
        runtime_data={
            Platform.BINARY_SENSOR: shared_data,
            Platform.SENSOR: shared_data,
            Platform.WEATHER: shared_data,
        }
    )
    assert await integration.async_unload_entry(hass, entry)
    unsub.assert_called_once()
