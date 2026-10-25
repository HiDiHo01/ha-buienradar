# Buienradar Home Assistant Integration (`ha-buienradar`)

[![GitHub Release](https://img.shields.io/github/v/release/mjj4791/ha-buienradar?style=for-the-badge)](https://github.com/mjj4791/ha-buienradar/releases)
[![HACS Default](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/hacs/default)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1%2B-blue.svg?style=for-the-badge)](https://www.home-assistant.io)

An advanced Home Assistant custom component integration for **Buienradar** weather and radar data. This integration delivers hyper-local weather observations, high-resolution precipitation radar images, short-term precipitation forecasts, binary rain sensors, and detailed multi-day forecasts for the Netherlands (NL) and Belgium (BE).

---

## 🌟 Key Features

- **🌦️ Detailed Weather Entities**: Real-time temperature, humidity, wind speed, atmospheric pressure, visibility, precipitation, and detailed weather conditions.
- **🛰️ Radar Camera Entity**: High-resolution animated precipitation radar camera map centered on your location with customizable frame dimensions (`dimension`) and time span (`delta`).
- **☔ Rain Binary Sensor**: Detect incoming precipitation within a configurable timeframe (e.g., next 60 minutes) to trigger automated awnings, windows, or notification automations.
- **📈 Short-term & Daily Forecasts**: Provides hourly radar forecast intensity alongside daily multi-day weather forecasts.
- **⚙️ Full UI Configuration & Options Flow**: Simple setup via Home Assistant UI with full support for re-configuration and adjustable options.
- **🌍 Multi-language & Localization**: Translated into over 40 languages with native support for Dutch (`nl`) and English (`en`).

---

## 📦 Installation

### Option 1: HACS (Home Assistant Community Store) - Recommended

1. Ensure [HACS](https://hacs.xyz/) is installed and running in your Home Assistant instance.
2. Open **HACS** > **Integrations**.
3. Search for **Buienradar**.
4. Click **Download**.
5. Restart Home Assistant.

### Option 2: Manual Installation

1. Download the latest release from the [Releases](https://github.com/mjj4791/ha-buienradar/releases) page.
2. Copy the `custom_components/buienradar` directory to your Home Assistant configuration directory:
   ```bash
   <config_dir>/custom_components/buienradar/
   ```
3. Restart Home Assistant.

---

## ⚙️ Configuration

1. In Home Assistant, navigate to **Settings** -> **Devices & Services**.
2. Click **Add Integration** in the bottom right corner.
3. Search for **Buienradar** and select it.
4. Follow the setup wizard:
   - Select your Country (`NL` or `BE`).
   - Confirm or set location coordinates (Latitude / Longitude).
   - Configure radar image dimensions and forecast timeframes.

### Configuration Options

You can adjust the integration settings anytime via **Settings** -> **Devices & Services** -> **Buienradar** -> **Configure**:

| Option | Description | Default |
| :--- | :--- | :--- |
| **Timeframe** | Time window (minutes) for precipitation evaluation | `60` min |
| **Radar Dimension** | Image width and height (pixels) for radar map | `700` px |
| **Radar Delta** | Historical/forecast time span (seconds) for radar loop | `600` s |

---

## 🧩 Entities Provided

Depending on your selected configuration, `ha-buienradar` creates the following entities:

| Entity Type | Example Entity ID | Description |
| :--- | :--- | :--- |
| `weather` | `weather.buienradar` | Weather entity containing current state, temperature, pressure, wind, and forecast array. |
| `camera` | `camera.buienradar` | Animated rain radar loop map centered on configured coordinates. |
| `binary_sensor` | `binary_sensor.buienradar_rain` | Indicates `ON` if rain is predicted within configured timeframe. |
| `sensor` | `sensor.buienradar_temperature` | Individual sensors for temperature, humidity, wind speed, visibility, rain intensity, etc. |

---

## 🤖 Automations Example

### Close Awning / Smart Windows When Rain Is Incoming
```yaml
alias: "Close Awning when Rain Expected"
description: "Closes awning when Buienradar rain binary sensor turns on"
trigger:
  - platform: state
    entity_id: binary_sensor.buienradar_rain
    from: "off"
    to: "on"
action:
  - service: cover.close_cover
    target:
      entity_id: cover.living_room_awning
```

---

## 🛠️ Troubleshooting & Debugging

Enable debug logging in your Home Assistant `configuration.yaml` to diagnose issues:

```yaml
logger:
  default: warning
  logs:
    custom_components.buienradar: debug
    buienradar: debug
```

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
