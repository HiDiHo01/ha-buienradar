# CLAUDE.md - AI Assistant Development Guide

**Required guidance:** Read [AI_POLICY.md](AI_POLICY.md), [AGENTS.md](AGENTS.md), and [home-assistant.md](home-assistant.md) before changes or reviews. The policy governs authorization, privacy, and review integrity; this guide provides supplementary implementation context.

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

- **Active data flow**: `__init__.py` sets up a shared `BrData` from `util.py` in `ConfigEntry.runtime_data` for binary sensors, sensors, and weather entities. `camera.py` fetches radar imagery separately.
- **Config flow**: `config_flow.py` handles location coordinates and options for country, precipitation timeframe, and radar refresh interval.
- **Entity classes**: `BrWeather` (`weather.py`), `BrSensor` (`sensor.py`), `BuienradarBinarySensor` (`binary_sensor.py`), and `BuienradarCam` (`camera.py`).
- **Further details**: See [home-assistant.md](home-assistant.md) for the maintained module map. Do not assume the older `coordinator.py` defines the active polling path.

---

## 🎨 Coding Conventions & Style

1. **Async First**: Use `async_setup_entry`, `async_update`, and async callbacks for Home Assistant lifecycle hooks.
2. **Type Annotations**: Provide explicit return type annotations and parameter types for functions.
3. **Strings & Translations**:
   - Master strings live in `custom_components/buienradar/strings.json`.
   - Translations live in `custom_components/buienradar/translations/<lang>.json`.
4. **Error Handling**: Use Home Assistant exceptions (`HomeAssistantError`, `ConfigEntryNotReady`) where appropriate.
