# Localization & Internationalization Guide

The `ha-buienradar` custom component supports multi-language localization to provide native UI labels, options flow descriptions, entity names, and error messages for Home Assistant users worldwide.

---

## 📁 Translation File Architecture

All localization files are contained within the component directory:

```
custom_components/buienradar/
├── strings.json             # Source master template for UI strings & config flows
└── translations/            # Language-specific JSON translation files
    ├── en.json              # English (Default / Base)
    ├── nl.json              # Dutch (Native region translation)
    ├── de.json              # German
    ├── fr.json              # French
    └── ...                  # 40+ supported locale JSON files
```

---

## 🔑 Key Translation Structure (`strings.json` / `<lang>.json`)

Translations follow standard Home Assistant JSON schemas:

```json
{
  "config": {
    "step": {
      "user": {
        "title": "Buienradar Configuration",
        "description": "Set up Buienradar weather data for your location.",
        "data": {
          "latitude": "Latitude",
          "longitude": "Longitude",
          "country": "Country Code (NL or BE)"
        }
      }
    },
    "error": {
      "cannot_connect": "Failed to connect to Buienradar API",
      "invalid_country": "Unsupported country code specified"
    }
  },
  "options": {
    "step": {
      "init": {
        "title": "Buienradar Options",
        "data": {
          "timeframe": "Timeframe for rain forecast (minutes)",
          "dimension": "Radar image resolution dimension (pixels)",
          "delta": "Radar animation delta span (seconds)"
        }
      }
    }
  },
  "entity": {
    "sensor": {
      "temperature": {
        "name": "Temperature"
      },
      "humidity": {
        "name": "Humidity"
      }
    }
  }
}
```

---

## 🌐 Adding or Updating Translations

1. **Master String Changes**:
   When adding new configuration options or entity attributes, update `custom_components/buienradar/strings.json` and `custom_components/buienradar/translations/en.json` first.

2. **Language Specific Updates**:
   To fix or add translations for a specific language (e.g., Dutch `nl.json`), modify `custom_components/buienradar/translations/nl.json`.

3. **Validation**:
   Ensure JSON files are strictly valid standard JSON (no trailing commas, properly closed quotes).
