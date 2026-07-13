"""The Vertiv PowerAssist integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any, Final, TypedDict
from urllib.parse import urlsplit

import aiohttp
from aiohttp import ClientTimeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_ENDPOINT,
    DEFAULT_PORT,
    DOMAIN,
    KEY_UNIQUE_ID,
    PLATFORMS,
    REQUEST_TIMEOUT,
    SCAN_INTERVAL_SECONDS,  # Use the constant for the interval
)


class VertivPowerAssistRuntimeData(TypedDict):
    """Runtime data for the Vertiv PowerAssist integration."""

    api: VertivPowerAssistApi
    coordinator: DataUpdateCoordinator
    unique_id: str


VertivPowerAssistConfigEntry = ConfigEntry[VertivPowerAssistRuntimeData]

_LOGGER = logging.getLogger(__name__)

HEADERS: Final = {"Content-type": "application/json"}
SCAN_INTERVAL: Final = timedelta(seconds=SCAN_INTERVAL_SECONDS)


def normalize_host_and_port(host: str, port: int = DEFAULT_PORT) -> tuple[str, int]:
    """Normalize PowerAssist host values entered during config flow."""
    value = str(host).strip()
    parsed = urlsplit(value if "://" in value else f"//{value}")

    normalized_host = parsed.hostname
    if not normalized_host:
        raise ValueError("Invalid host")

    try:
        normalized_port = parsed.port or int(port)
    except ValueError as err:
        raise ValueError("Invalid port") from err

    return normalized_host, normalized_port


class VertivPowerAssistApi:
    """Class to communicate with the Vertiv PowerAssist API."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        unique_id: str,
        port: int = DEFAULT_PORT,
    ) -> None:
        """Initialize the API object."""
        self._hass = hass
        self._host, self._port = normalize_host_and_port(host, port)
        self._unique_id = unique_id
        self._url = f"https://{self._host}:{self._port}{API_ENDPOINT}"

    async def async_test_connection(self) -> dict[str, Any]:
        """Test the connection and fetch initial data."""
        data = await self.async_update_data()
        if not data or not data.get(KEY_UNIQUE_ID):
            raise UpdateFailed("Invalid response or missing device data.")

        return data

    async def _async_call_api(
        self, endpoint: str, method: str = "GET", payload: dict[str, Any] | None = None
    ) -> Any:
        """Centralized method for API calls."""
        try:
            session = async_get_clientsession(self._hass)
            url = f"https://{self._host}:{self._port}/api/PowerAssist{endpoint}"
            async with session.request(
                method,
                url,
                json=payload,
                timeout=ClientTimeout(total=REQUEST_TIMEOUT),
                headers=HEADERS,
                ssl=False,
            ) as response:
                response.raise_for_status()
                if response.content_type == "application/json":
                    return await response.json()
                return None

        except aiohttp.ClientConnectorError as err:
            _LOGGER.warning("Connection failed for %s: %s", self._host, err)
            raise UpdateFailed(f"Connection failed to {self._host}") from err
        except aiohttp.ClientResponseError as err:
            _LOGGER.warning("Invalid response from %s: %s", self._host, err)
            try:
                error_body = await response.text()
                _LOGGER.error("API response content on failure: %s", error_body)
            except (aiohttp.ClientError, UnicodeDecodeError, RuntimeError):
                pass
            raise UpdateFailed(f"Invalid response from {self._host}") from err
        except TimeoutError as err:
            _LOGGER.warning("Request timed out for %s: %s", self._host, err)
            raise UpdateFailed("Request timed out") from err
        except aiohttp.ClientError as err:
            _LOGGER.warning("API request failed for %s: %s", self._host, err)
            raise UpdateFailed(f"API request failed for {self._host}") from err

    async def async_update_data(self) -> dict[str, Any]:
        """Fetch all necessary data from the Vertiv PowerAssist API."""
        results = {}
        main_data = await self._async_call_api("", method="GET")
        if not main_data or not isinstance(main_data, list) or not main_data:
            raise UpdateFailed("API returned empty or unexpected main data")
        results.update(main_data[0])
        shutdown_config_response = await self._async_call_api(
            "/ShutdownConfig", method="GET"
        )
        if shutdown_config_response and "shutdownConfig" in shutdown_config_response:
            results.update(shutdown_config_response["shutdownConfig"])
        maintenance_mode = await self._async_call_api(
            "/InMaintenanceMode", method="GET"
        )
        results["maintenanceModeActive_get"] = maintenance_mode

        return results

    async def async_set_shutdown_config(self, config: dict[str, Any]) -> None:
        """Post the shutdown configuration to the API."""
        await self._async_call_api("/ShutdownConfig", method="POST", payload=config)

    async def async_set_ups_name(self, name: str) -> None:
        """Post the UPS name to the API."""
        payload = {"upsUniqueIdentifier": self._unique_id, "name": name}
        await self._async_call_api("/UpsName", method="POST", payload=payload)


async def async_setup_entry(
    hass: HomeAssistant, entry: VertivPowerAssistConfigEntry
) -> bool:
    """Set up Vertiv PowerAssist from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)
    unique_id = entry.unique_id if entry.unique_id else host

    try:
        api = VertivPowerAssistApi(hass, host, unique_id, port)
        await api.async_test_connection()
    except (ValueError, TimeoutError, UpdateFailed, aiohttp.ClientError) as ex:
        _LOGGER.error("Initial connection to Vertiv PowerAssist failed: %s", ex)
        raise ConfigEntryNotReady(
            f"Could not connect to Vertiv PowerAssist at {host}"
        ) from ex

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=api.async_update_data,
        update_interval=SCAN_INTERVAL,
        config_entry=entry,
    )

    entry.runtime_data = VertivPowerAssistRuntimeData(
        api=api,
        coordinator=coordinator,
        unique_id=unique_id,
    )

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: VertivPowerAssistConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
