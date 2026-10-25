# Agent Guidelines for ha-buienradar

Welcome to the **ha-buienradar** repository. This document provides guidance, context, and operational rules for AI coding agents (such as Claude, Codex, GPT, etc.) working on this codebase.

---

## 📌 Repository Overview

- **Project Name**: `ha-buienradar`
- **Domain**: `buienradar`
- **Type**: Home Assistant Custom Component (`custom_components/buienradar`)
- **Primary Function**: Integrates weather data, precipitation forecast, rain sensors, and animated radar camera maps from Buienradar (Netherlands / Belgium) into Home Assistant.

---

## 📂 Codebase Structure

```
.
├── custom_components/
│   └── buienradar/
│       ├── __init__.py         # Component setup, unload, and entry lifecycle
│       ├── api.py              # Buienradar API interaction wrappers
│       ├── binary_sensor.py    # Rain binary sensor entity
│       ├── camera.py           # Animated radar camera entity
│       ├── config_flow.py      # UI configuration and options flow handler
│       ├── const.py            # Component constants and default settings
│       ├── coordinator.py      # DataUpdateCoordinator for polling API
│       ├── entity.py           # Base entity class for Buienradar
│       ├── manifest.json       # Home Assistant integration metadata
│       ├── quality_scale.yaml  # Quality scale standard tracking
│       ├── sensor.py           # Individual weather sensors
│       ├── strings.json        # Base localization strings
│       ├── util.py             # Utility functions
│       ├── weather.py          # Weather entity with forecasts
│       └── translations/       # Translated string JSON files (40+ languages)
├── README.md                   # Main documentation
└── home-assistant.md           # Home Assistant architecture guide
```

---

## 🛠 Rules for AI Agents

1. **Follow Home Assistant Standards**:
   - Always use async patterns (`async_setup_entry`, `async_update`, `async_forward_entry_setups`).
   - Derive entities from Home Assistant base classes (`CoordinatorEntity`, `SensorEntity`, `WeatherEntity`, `Camera`).
   - Do not perform blocking I/O on the event loop; use `async_add_executor_job` or async libraries if necessary.

2. **Maintain Code Quality**:
   - Use strict Python typing wherever applicable.
   - Respect constants defined in `const.py`.
   - Ensure strings are properly added to `strings.json` and key translations updated.

3. **Validation & Verification**:
   - Always run syntax checks (`python3 -m py_compile custom_components/buienradar/*.py`) after making edits.
   - Verify non-breaking behavior with existing entities and config flows.

4. **Safety & Security**:
   - Never expose API keys or hardcode personal credentials.
   - Respect Home Assistant's security model and IoT guidelines.
