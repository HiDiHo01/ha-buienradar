"""Tests for timeframe parameter handling in Buienradar integration."""

from custom_components.buienradar.const import DEFAULT_TIMEFRAME
from custom_components.buienradar.util import BrData


def test_brdata_timeframe_handling():
    """Test that BrData converts various timeframe inputs into an integer."""
    coordinates = {"latitude": 52.0, "longitude": 5.0}

    # Integer timeframe
    data_int = BrData(None, coordinates, 60, [])
    assert data_int.timeframe == 60
    assert isinstance(data_int.timeframe, int)

    # Float timeframe
    data_float = BrData(None, coordinates, 60.0, [])
    assert data_float.timeframe == 60
    assert isinstance(data_float.timeframe, int)

    # String timeframe
    data_str = BrData(None, coordinates, "45", [])
    assert data_str.timeframe == 45
    assert isinstance(data_str.timeframe, int)

    # Invalid timeframe values fallback to DEFAULT_TIMEFRAME
    data_none = BrData(None, coordinates, None, [])
    assert data_none.timeframe == DEFAULT_TIMEFRAME
    assert isinstance(data_none.timeframe, int)

    data_invalid = BrData(None, coordinates, "invalid", [])
    assert data_invalid.timeframe == DEFAULT_TIMEFRAME
    assert isinstance(data_invalid.timeframe, int)
