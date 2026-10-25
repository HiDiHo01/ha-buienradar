"""Config flow for buienradar integration."""

from __future__ import annotations

import copy
import logging
from typing import Any, cast

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult
from homeassistant.const import (
    CONF_COUNTRY_CODE,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_NAME,
)
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaCommonFlowHandler,
    SchemaFlowFormStep,
    SchemaOptionsFlowHandler,
)

from buienradar.buienradar import parse_data
from buienradar.urls import json_precipitation_forecast_url

from .const import (
    CONF_DELTA,
    CONF_TIMEFRAME,
    DEFAULT_COUNTRY,
    DEFAULT_DELTA,
    DEFAULT_TIMEFRAME,
    DOMAIN,
    SUPPORTED_COUNTRY_CODES,
)

_LOGGER = logging.getLogger(__name__)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Optional(
            CONF_COUNTRY_CODE, default=DEFAULT_COUNTRY
        ): selector.CountrySelector(
            selector.CountrySelectorConfig(countries=SUPPORTED_COUNTRY_CODES)
        ),
        vol.Optional(CONF_DELTA, default=DEFAULT_DELTA): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0,
                step=1,
                mode=selector.NumberSelectorMode.BOX,
                unit_of_measurement="seconds",
            ),
        ),
        vol.Optional(
            CONF_TIMEFRAME, default=DEFAULT_TIMEFRAME
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=5,
                max=120,
                step=5,
                mode=selector.NumberSelectorMode.BOX,
                unit_of_measurement="minutes",
            ),
        ),
    }
)


async def _options_suggested_values(handler: SchemaCommonFlowHandler) -> dict[str, Any]:
    parent_handler = cast(SchemaOptionsFlowHandler, handler.parent_handler)
    suggested_values = copy.deepcopy(dict(parent_handler.config_entry.data))
    suggested_values.update(parent_handler.options)
    return suggested_values


OPTIONS_FLOW = {
    "init": SchemaFlowFormStep(
        OPTIONS_SCHEMA, suggested_values=_options_suggested_values
    ),
}


class BuienradarFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Buienradar."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> SchemaOptionsFlowHandler:
        """Get the options flow for this handler."""
        return SchemaOptionsFlowHandler(config_entry, OPTIONS_FLOW)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors = {}

        if user_input is not None:
            latitude = user_input.get(CONF_LATITUDE)
            longitude = user_input.get(CONF_LONGITUDE)

            # Ensure unique entry per coordinates
            await self.async_set_unique_id(f"{latitude}-{longitude}")
            self._abort_if_unique_id_configured()

            # Fetch station info
            station_name = await self._get_station_name(latitude, longitude)
            if not station_name:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=station_name,  # Displayed in HA UI
                    data={
                        CONF_LATITUDE: latitude,
                        CONF_LONGITUDE: longitude,
                        CONF_NAME: "Buienradar",  # used as integration prefix
                        "stationname": station_name,  # optional: store station name
                    },
                )

        # Show form if first run or on error
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_LATITUDE, default=self.hass.config.latitude
                ): cv.latitude,
                vol.Required(
                    CONF_LONGITUDE, default=self.hass.config.longitude
                ): cv.longitude,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def _get_station_name(self, latitude: float, longitude: float) -> str | None:
        """Fetch the Buienradar station name for the given coordinates."""
        url = json_precipitation_forecast_url(latitude, longitude)
        _LOGGER.debug("Fetching station name from Buienradar API: %s", url)
        # __parse_ws_data
        # __select_nearest_ws
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(url) as resp:
                if resp.status != 200:
                    _LOGGER.error("Buienradar returned HTTP %s", resp.status)
                    return None
                content = await resp.text()
                _LOGGER.debug(
                    "Received response from Buienradar: %s", content[:200]
                )  # log first 200 chars
                # parse_data requires both content args for rain and weather
                result = parse_data(
                    content, content, latitude, longitude, 60, api="json"
                )
                if result.get("success"):
                    return result["data"].get("stationname")
        except Exception:
            _LOGGER.exception("Error fetching station name from Buienradar API")
            return None

        return None
