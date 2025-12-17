"""Switch entities for the Vertiv PowerAssist integration."""

from __future__ import annotations

from typing import Any, Final

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import VertivPowerAssistConfigEntry
from .const import (
    KEY_AFTER_X_MINUTES,
    KEY_BATT_CAPACITY_PERCENT,
    KEY_BATT_TIME_MIN,
    KEY_ENABLE_SCRIPTED_SHUTDOWN,
    KEY_MAINTENANCE_MODE_GET,
    KEY_MAINTENANCE_MODE_POST,
    KEY_SCRIPTED_SHUTDOWN_PATH,
    KEY_SHUTDOWN_IF_ALL,
    KEY_SHUTDOWN_TYPE,
)
from .entity import VertivPowerAssistBaseEntity

MAINTENANCE_MODE_DESCRIPTION: Final[SwitchEntityDescription] = SwitchEntityDescription(
    key=KEY_MAINTENANCE_MODE_GET,  # Use the GET key for reading state from coordinator data
    translation_key="maintenance_mode",
    icon="mdi:wrench",
    entity_category=EntityCategory.CONFIG,
)
SHUTDOWN_IF_ALL_DESCRIPTION: Final[SwitchEntityDescription] = SwitchEntityDescription(
    key=KEY_SHUTDOWN_IF_ALL,
    translation_key="shutdown_if_all_loses_power",
    icon="mdi:server-network-off",
    entity_category=EntityCategory.CONFIG,
)
ENABLE_SCRIPTED_SHUTDOWN_DESCRIPTION: Final[SwitchEntityDescription] = (
    SwitchEntityDescription(
        key=KEY_ENABLE_SCRIPTED_SHUTDOWN,
        translation_key="enable_scripted_shutdown",
        icon="mdi:script-text-outline",
    )
)

SWITCH_DESCRIPTIONS: Final[list[SwitchEntityDescription]] = [
    MAINTENANCE_MODE_DESCRIPTION,
    SHUTDOWN_IF_ALL_DESCRIPTION,
    ENABLE_SCRIPTED_SHUTDOWN_DESCRIPTION,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VertivPowerAssistConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Vertiv PowerAssist switch entities."""
    coordinator = entry.runtime_data["coordinator"]

    async_add_entities(
        [
            VertivPowerAssistSwitchEntity(entry, coordinator, description)
            for description in SWITCH_DESCRIPTIONS
        ]
    )


class VertivPowerAssistSwitchEntity(VertivPowerAssistBaseEntity, SwitchEntity):
    """Represents a configurable boolean setting for UPS shutdown."""

    def __init__(
        self,
        entry: VertivPowerAssistConfigEntry,
        coordinator: DataUpdateCoordinator,
        description: SwitchEntityDescription,
    ) -> None:
        """Initialize the switch entity."""
        super().__init__(entry, description)
        self.entity_description = description
        self._api = entry.runtime_data["api"]

        if description.key == KEY_MAINTENANCE_MODE_GET:
            self._attr_unique_id = (
                f"{entry.runtime_data['unique_id']}_{KEY_MAINTENANCE_MODE_POST}"
            )

    @property
    def is_on(self) -> bool | None:
        """Return True if the switch is on (config is enabled)."""
        raw_value = self.coordinator.data.get(self.entity_description.key)

        if isinstance(raw_value, bool):
            return raw_value

        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on (set the config parameter to True)."""
        await self._async_set_config_value(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off (set the config parameter to False)."""
        await self._async_set_config_value(False)

    async def _async_set_config_value(self, value: bool) -> None:
        """Helper to create and send the full configuration payload."""

        payload_key = (
            KEY_MAINTENANCE_MODE_POST
            if self.entity_description.key == KEY_MAINTENANCE_MODE_GET
            else self.entity_description.key
        )

        current_config: dict[str, Any] = {
            KEY_SHUTDOWN_TYPE: self.coordinator.data.get(KEY_SHUTDOWN_TYPE, 0),
            KEY_BATT_TIME_MIN: self.coordinator.data.get(KEY_BATT_TIME_MIN, 0),
            KEY_BATT_CAPACITY_PERCENT: self.coordinator.data.get(
                KEY_BATT_CAPACITY_PERCENT, 0
            ),
            KEY_AFTER_X_MINUTES: self.coordinator.data.get(KEY_AFTER_X_MINUTES, 0),
            # Use the data values for the other switches
            KEY_SHUTDOWN_IF_ALL: self.coordinator.data.get(KEY_SHUTDOWN_IF_ALL, False),
            KEY_ENABLE_SCRIPTED_SHUTDOWN: self.coordinator.data.get(
                KEY_ENABLE_SCRIPTED_SHUTDOWN, False
            ),
            KEY_MAINTENANCE_MODE_POST: self.coordinator.data.get(
                KEY_MAINTENANCE_MODE_GET, False
            ),
            KEY_SCRIPTED_SHUTDOWN_PATH: self.coordinator.data.get(
                KEY_SCRIPTED_SHUTDOWN_PATH, ""
            ),
        }

        current_config[payload_key] = value

        await self._api.async_set_shutdown_config(current_config)

        await self.coordinator.async_request_refresh()
