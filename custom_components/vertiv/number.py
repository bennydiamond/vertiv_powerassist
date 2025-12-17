"""Number entities for the Vertiv PowerAssist integration."""

from __future__ import annotations

from typing import Any, Final

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import PERCENTAGE, UnitOfTime
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

BATTERY_TIME_MIN_DESCRIPTION: Final[NumberEntityDescription] = NumberEntityDescription(
    key=KEY_BATT_TIME_MIN,
    translation_key="shutdown_battery_time_min",
    icon="mdi:battery-clock",
    native_unit_of_measurement=UnitOfTime.MINUTES,
    mode=NumberMode.BOX,
    native_min_value=0,
    native_max_value=120,
    native_step=1,
)
BATTERY_CAPACITY_PERCENT_DESCRIPTION: Final[NumberEntityDescription] = (
    NumberEntityDescription(
        key=KEY_BATT_CAPACITY_PERCENT,
        translation_key="shutdown_battery_capacity_percent",
        icon="mdi:battery-20",
        native_unit_of_measurement=PERCENTAGE,
        mode=NumberMode.BOX,
        native_min_value=5,
        native_max_value=90,
        native_step=1,
    )
)
AFTER_X_MINUTES_DESCRIPTION: Final[NumberEntityDescription] = NumberEntityDescription(
    key=KEY_AFTER_X_MINUTES,
    translation_key="shutdown_after_x_minutes",
    icon="mdi:timer-sand-full",
    native_unit_of_measurement=UnitOfTime.MINUTES,
    mode=NumberMode.BOX,
    native_min_value=0,
    native_max_value=300,
    native_step=1,
)

NUMBER_DESCRIPTIONS: Final[list[NumberEntityDescription]] = [
    BATTERY_TIME_MIN_DESCRIPTION,
    BATTERY_CAPACITY_PERCENT_DESCRIPTION,
    AFTER_X_MINUTES_DESCRIPTION,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VertivPowerAssistConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Vertiv PowerAssist number entities."""
    coordinator = entry.runtime_data["coordinator"]

    async_add_entities(
        [
            VertivPowerAssistNumberEntity(entry, coordinator, description)
            for description in NUMBER_DESCRIPTIONS
        ]
    )


class VertivPowerAssistNumberEntity(VertivPowerAssistBaseEntity, NumberEntity):
    """Represents a configurable numeric threshold for UPS shutdown."""

    def __init__(
        self,
        entry: VertivPowerAssistConfigEntry,
        coordinator: DataUpdateCoordinator,
        description: NumberEntityDescription,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(entry, description)
        self.entity_description = description
        self._api = entry.runtime_data["api"]

    @property
    def native_value(self) -> float | None:
        """Return the current value of the number entity."""
        raw_value = self.coordinator.data.get(self.entity_description.key)

        if isinstance(raw_value, (int, float)):
            return float(raw_value)

        return None

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""

        current_config: dict[str, Any] = {
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
        current_config[self.entity_description.key] = int(value)
        await self._api.async_set_shutdown_config(current_config)
        await self.coordinator.async_request_refresh()
