"""Select entities for the Vertiv PowerAssist integration."""

from __future__ import annotations

from typing import Final

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import VertivPowerAssistConfigEntry
from .const import (
    KEY_AFTER_X_MINUTES,
    KEY_BATT_CAPACITY_PERCENT,
    KEY_BATT_TIME_MIN,
    KEY_ENABLE_SCRIPTED_SHUTDOWN,
    KEY_MAINTENANCE_MODE_POST,
    KEY_SCRIPTED_SHUTDOWN_PATH,
    KEY_SHUTDOWN_IF_ALL,
    KEY_SHUTDOWN_TYPE,
)
from .entity import VertivPowerAssistBaseEntity

TYPE_INT_TO_KEY: Final[dict[int, str]] = {
    0: "by_minutes",
    1: "by_percent",
    2: "after_x",
    3: "immediately",
}

TYPE_KEY_TO_INT: Final[dict[str, int]] = {v: k for k, v in TYPE_INT_TO_KEY.items()}

SHUTDOWN_TRIGGER_TYPE_DESCRIPTION: Final[SelectEntityDescription] = (
    SelectEntityDescription(
        key=KEY_SHUTDOWN_TYPE,
        translation_key="shutdown_trigger",
        icon="mdi:power-settings",
    )
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VertivPowerAssistConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Vertiv PowerAssist select entities."""
    coordinator = entry.runtime_data["coordinator"]

    async_add_entities(
        [
            VertivPowerAssistSelectEntity(
                entry, coordinator, SHUTDOWN_TRIGGER_TYPE_DESCRIPTION
            )
        ]
    )


class VertivPowerAssistSelectEntity(VertivPowerAssistBaseEntity, SelectEntity):
    """Represents the configurable Shutdown Trigger Type for the UPS."""

    def __init__(
        self,
        entry: VertivPowerAssistConfigEntry,
        coordinator: DataUpdateCoordinator,
        description: SelectEntityDescription,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(entry, description)
        self.entity_description = description
        self._api = entry.runtime_data["api"]

        self._attr_options = list(TYPE_INT_TO_KEY.values())

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        raw_value = self.coordinator.data.get(self.entity_description.key)

        if isinstance(raw_value, int) and raw_value in TYPE_INT_TO_KEY:
            return TYPE_INT_TO_KEY[raw_value]

        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""

        new_shutdown_type_int = TYPE_KEY_TO_INT.get(option)

        if new_shutdown_type_int is None:
            # Should not happen if the options list is correct
            return

        current_config = {
            KEY_SHUTDOWN_TYPE: self.coordinator.data.get(KEY_SHUTDOWN_TYPE, 0),
            KEY_BATT_TIME_MIN: self.coordinator.data.get(KEY_BATT_TIME_MIN, 0),
            KEY_BATT_CAPACITY_PERCENT: self.coordinator.data.get(
                KEY_BATT_CAPACITY_PERCENT, 0
            ),
            KEY_AFTER_X_MINUTES: self.coordinator.data.get(KEY_AFTER_X_MINUTES, 0),
            KEY_SHUTDOWN_IF_ALL: self.coordinator.data.get(KEY_SHUTDOWN_IF_ALL, False),
            KEY_MAINTENANCE_MODE_POST: self.coordinator.data.get(
                KEY_MAINTENANCE_MODE_POST, False
            ),
            KEY_ENABLE_SCRIPTED_SHUTDOWN: self.coordinator.data.get(
                KEY_ENABLE_SCRIPTED_SHUTDOWN, False
            ),
            KEY_SCRIPTED_SHUTDOWN_PATH: self.coordinator.data.get(
                KEY_SCRIPTED_SHUTDOWN_PATH, ""
            ),
        }

        current_config[KEY_SHUTDOWN_TYPE] = new_shutdown_type_int

        await self._api.async_set_shutdown_config(current_config)

        await self.coordinator.async_request_refresh()
