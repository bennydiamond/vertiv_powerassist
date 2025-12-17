"""Config flow for Vertiv PowerAssist integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers import selector

from . import VertivPowerAssistApi
from .const import DEFAULT_NAME, DEFAULT_PORT, DOMAIN, KEY_UNIQUE_ID

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): selector.TextSelector(),
        vol.Required(CONF_PORT, default=DEFAULT_PORT): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=1, max=65535, mode=selector.NumberSelectorMode.BOX
            )
        ),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): selector.TextSelector(),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate connectivity and get unique id from the device."""
    host = data[CONF_HOST]
    port = data[CONF_PORT]

    temp_api = VertivPowerAssistApi(hass, host, f"{host}:{port}")

    try:
        info = await temp_api.async_test_connection()
    except aiohttp.ClientConnectorError as err:
        raise ConnectionError("cannot_connect") from err
    except TimeoutError as err:
        raise ConnectionError("timeout") from err
    except Exception as exc:
        _LOGGER.exception("Unexpected error during config validation")
        raise ConnectionError("unknown") from exc

    unique_id = info.get(KEY_UNIQUE_ID)
    if not unique_id:
        raise ValueError("invalid_response")

    return {"title": info.get("name", host), "unique_id": unique_id}


class VertivPowerAssistConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Vertiv PowerAssist."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(data_schema=DATA_SCHEMA)

        errors: dict[str, str] = {}
        info: dict[str, Any] | None = None

        try:
            info = await validate_input(self.hass, user_input)
            await self.async_set_unique_id(info["unique_id"])
            self._abort_if_unique_id_configured()
        except ConnectionError as err:
            errors["base"] = str(err)
        except ValueError as err:
            errors["base"] = str(err)
        except Exception:
            _LOGGER.exception("Unexpected exception during validation")
            errors["base"] = "unknown"

        if not errors and info:
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(data_schema=DATA_SCHEMA, errors=errors)
