"""Regression tests for the Buienradar binary sensor platform."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, Platform

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


def test_binary_sensor_initially_unavailable_and_updates() -> None:
    """Track data availability and keep the entry's unique identifiers."""
    entry = SimpleNamespace(entry_id="example")
    entity = BuienradarBinarySensor(entry, BINARY_SENSOR_TYPES[0])
    assert entity.unique_id == "example_precipitation_expected"
    assert not entity.available

    entity.data_updated(
        SimpleNamespace(
            data={"precipitation_forecast": {"average": 0.1, "total": 0.1}}
        )
    )
    assert entity.available
    assert entity.is_on

    entity.data_updated(SimpleNamespace(data={"precipitation_forecast": None}))
    assert not entity.available
    assert entity.is_on is None


@pytest.mark.asyncio
async def test_setup_entry_uses_buienradar_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Set up all binary sensors via BrData without Buienalarm modules."""
    from custom_components.buienradar import binary_sensor

    async_update = AsyncMock()
    created: list[object] = []

    class FakeBrData:
        """Record the arguments passed to Buienradar's polling helper."""

        def __init__(
            self,
            hass: object,
            coordinates: dict[str, float],
            timeframe: int,
            devices: list[object],
        ) -> None:
            """Capture the setup input for assertions."""
            created.extend((hass, coordinates, timeframe, devices))
            self.async_update = async_update

    monkeypatch.setattr(binary_sensor, "BrData", FakeBrData)
    hass = SimpleNamespace(config=SimpleNamespace(latitude=52.0, longitude=5.0))
    entry = SimpleNamespace(
        entry_id="example",
        data={CONF_LATITUDE: 52.0, CONF_LONGITUDE: 5.0},
        options={"timeframe": 60.0},
        runtime_data={},
    )
    entities_added: list[object] = []

    await async_setup_entry(hass, entry, entities_added.extend)

    assert created[:3] == [hass, {CONF_LATITUDE: 52.0, CONF_LONGITUDE: 5.0}, 60]
    assert created[3] == entities_added
    assert len(entities_added) == 3
    assert entry.runtime_data[Platform.BINARY_SENSOR].async_update is async_update
    async_update.assert_awaited_once()
