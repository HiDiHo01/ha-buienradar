"""Unit tests for buienradar constants and helper utilities."""

from custom_components.buienradar.const import (
    DOMAIN,
    DEFAULT_TIMEFRAME,
    DEFAULT_DIMENSION,
    DEFAULT_DELTA,
    SUPPORTED_COUNTRY_CODES,
    STATE_CONDITIONS,
    STATE_DETAILED_CONDITIONS,
)


def test_domain_constant():
    """Test DOMAIN constant value."""
    assert DOMAIN == "buienradar"


def test_default_values():
    """Test default configuration parameters."""
    assert DEFAULT_TIMEFRAME == 60
    assert DEFAULT_DIMENSION == 700
    assert DEFAULT_DELTA == 600


def test_supported_countries():
    """Test supported country codes list."""
    assert "NL" in SUPPORTED_COUNTRY_CODES
    assert "BE" in SUPPORTED_COUNTRY_CODES


def test_state_conditions():
    """Test state conditions definitions."""
    assert "clear" in STATE_CONDITIONS
    assert "rainy" in STATE_CONDITIONS
    assert "lightning" in STATE_CONDITIONS
    assert len(STATE_CONDITIONS) > 0


def test_detailed_state_conditions():
    """Test detailed state conditions definitions."""
    assert "partlycloudy" in STATE_DETAILED_CONDITIONS
    assert "light-rain" in STATE_DETAILED_CONDITIONS
    assert len(STATE_DETAILED_CONDITIONS) > len(STATE_CONDITIONS)
