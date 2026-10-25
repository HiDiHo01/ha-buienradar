# Home Assistant Architecture & Integration Notes: `ha-buienradar`

This document outlines the architectural implementation details for the `ha-buienradar` custom component within Home Assistant.

---

## 🏛 Integration Lifecycle & Architecture

The `ha-buienradar` custom component integrates into Home Assistant using modern `async_setup_entry` patterns and `DataUpdateCoordinator`.

```
                  ┌────────────────────────┐
                  │    Buienradar API      │
                  └───────────┬────────────┘
                              │ Async Polling
                              ▼
                  ┌────────────────────────┐
                  │ DataUpdateCoordinator  │
                  │   (coordinator.py)     │
                  └───────────┬────────────┘
                              │ Centralized Data Dispatch
            ┌─────────────────┼─────────────────┬─────────────────┐
            ▼                 ▼                 ▼                 ▼
     ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
     │   Weather   │   │   Camera    │   │Binary Sensor│   │   Sensors   │
     │   Entity    │   │   Entity    │   │   (Rain)    │   │(Temp/Press) │
     └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘
```

---

## ⚙️ Core Modules Breakdown

1. **`__init__.py`**:
   - Handles `async_setup_entry` and `async_unload_entry`.
   - Initializes `BuienradarDataUpdateCoordinator`.
   - Forwards entry setup to platform components (`weather`, `camera`, `binary_sensor`, `sensor`).

2. **`coordinator.py` (`BuienradarDataUpdateCoordinator`)**:
   - Manages periodic polling schedule (`SCHEDULE_OK` or `SCHEDULE_NOK` intervals).
   - Wraps async API calls to fetch observations and precipitation forecast grids.

3. **`config_flow.py`**:
   - Implements `BuienradarFlowHandler` for UI-based setup.
   - Implements `BuienradarOptionsFlowHandler` allowing users to tune timeframe, radar image dimensions, and delta without deleting entities.

4. **`weather.py` (`BuienRadarWeather`)**:
   - Extends Home Assistant's `WeatherEntity`.
   - Exposes daily weather forecast arrays (temperature, precipitation, condition, wind) and current atmospheric state.

5. **`camera.py` (`BuienradarCamera`)**:
   - Extends Home Assistant's `Camera` class.
   - Fetches animated loop map images representing precipitation radar scans.

6. **`binary_sensor.py` (`BuienradarRainSensor`)**:
   - Evaluates short-term rain forecast for the configured timeframe.
   - Changes state to `ON` when rain exceeds sensitivity threshold.

---

## 🔒 Home Assistant Core Standards Compliance

- **Storage**: Integrates via `config_entry` (`hass.data[DOMAIN][entry.entry_id]`).
- **Unload Cleanliness**: Properly unloads platform listeners upon entry removal.
- **Diagnostics & Logging**: Uses structured logger `custom_components.buienradar`.
