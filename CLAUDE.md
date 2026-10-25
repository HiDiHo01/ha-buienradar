# CLAUDE.md - AI Assistant Development Guide

This guide provides technical context, commands, and architecture insights for Claude and AI assistants working on `ha-buienradar`.

---

## 🚀 Quick Reference Commands

### Syntax & Compilation Checks
```bash
# Check Python syntax for all component files
python3 -m py_compile custom_components/buienradar/*.py
```

### Testing
```bash
# Run pytest (if test suite is configured)
pytest
```

---

## 🏗 Architecture Overview

`ha-buienradar` is structured as a standard Home Assistant custom component under `custom_components/buienradar/`:

- **Data Flow**: `coordinator.py` (`BuienradarDataUpdateCoordinator`) fetches weather and precipitation data periodically from the Buienradar API library (`buienradar`).
- **Config Flow**: `config_flow.py` handles UI configuration entry creation and options flow updates (timeframe, dimensions, delta).
- **Entities**:
  - `weather.py`: Integrates `BuienRadarWeather` implementing `WeatherEntity` with forecast support.
  - `camera.py`: Integrates `BuienradarCamera` producing radar map image loops.
  - `binary_sensor.py`: Integrates `BuienradarRainSensor` evaluating forecast rain intensity.
  - `sensor.py`: Exposes individual meteorological metrics (temperature, humidity, pressure, visibility, etc.).

---

## 🎨 Coding Conventions & Style

1. **Async First**: Use `async_setup_entry`, `async_update`, and async callbacks for Home Assistant lifecycle hooks.
2. **Type Annotations**: Provide explicit return type annotations and parameter types for functions.
3. **Strings & Translations**:
   - Master strings live in `custom_components/buienradar/strings.json`.
   - Translations live in `custom_components/buienradar/translations/<lang>.json`.
4. **Error Handling**: Use Home Assistant exceptions (`HomeAssistantError`, `ConfigEntryNotReady`) where appropriate.
