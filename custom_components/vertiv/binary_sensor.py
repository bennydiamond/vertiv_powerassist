"""Binary Sensor platform for Vertiv PowerAssist status flags."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import VertivPowerAssistConfigEntry
from .const import (
    KEY_IS_AC_PRESENT,
    KEY_IS_CHARGING,
    KEY_IS_DISCHARGING,
    KEY_IS_OVERLOAD,
    KEY_IS_UPS_ON,
    KEY_LOW_CAPACITY_LIMIT,
    KEY_NEEDS_REPLACEMENT,
    STATUS_KEY,
)
from .entity import VertivPowerAssistBaseEntity


@dataclass(frozen=True, kw_only=True)
class VertivPowerAssistBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a Vertiv PowerAssist Binary Sensor Entity."""

    api_key: str


BINARY_SENSOR_DESCRIPTIONS: tuple[
    VertivPowerAssistBinarySensorEntityDescription, ...
] = (
    VertivPowerAssistBinarySensorEntityDescription(
        key="ac_power_present",
        api_key=KEY_IS_AC_PRESENT,
        translation_key="ac_power_present",
        device_class=BinarySensorDeviceClass.POWER,
    ),
    VertivPowerAssistBinarySensorEntityDescription(
        key="battery_charging",
        api_key=KEY_IS_CHARGING,
        translation_key="battery_charging",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
    ),
    VertivPowerAssistBinarySensorEntityDescription(
        key="battery_discharging",
        api_key=KEY_IS_DISCHARGING,
        translation_key="battery_discharging",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    VertivPowerAssistBinarySensorEntityDescription(
        key="battery_needs_replacement",
        api_key=KEY_NEEDS_REPLACEMENT,
        translation_key="battery_needs_replacement",
        device_class=BinarySensorDeviceClass.BATTERY,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VertivPowerAssistBinarySensorEntityDescription(
        key="system_overload",
        api_key=KEY_IS_OVERLOAD,
        translation_key="system_overload",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VertivPowerAssistBinarySensorEntityDescription(
        key="system_running",
        api_key=KEY_IS_UPS_ON,
        translation_key="system_running",
        device_class=BinarySensorDeviceClass.RUNNING,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VertivPowerAssistBinarySensorEntityDescription(
        key="battery_low",
        api_key=KEY_LOW_CAPACITY_LIMIT,
        translation_key="battery_low",
        device_class=BinarySensorDeviceClass.BATTERY,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: VertivPowerAssistConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Vertiv PowerAssist binary sensors."""

    entities = [
        VertivPowerAssistBinarySensor(config_entry, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
    ]

    async_add_entities(entities)


class VertivPowerAssistBinarySensor(VertivPowerAssistBaseEntity, BinarySensorEntity):
    """Representation of a binary sensor entity for Vertiv PowerAssist status."""

    entity_description: VertivPowerAssistBinarySensorEntityDescription

    def __init__(
        self,
        entry: VertivPowerAssistConfigEntry,
        description: VertivPowerAssistBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(entry, description)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        data = self.coordinator.data
        if not data:
            return None

        # Data is nested under "status"
        status_data: dict[str, Any] | None = data.get(STATUS_KEY)
        if status_data is None:
            return None

        # The API returns a boolean (true/false) directly
        return status_data.get(self.entity_description.api_key)
