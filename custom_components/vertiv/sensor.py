"""Sensor platform for Vertiv PowerAssist."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, cast

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfElectricPotential, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import VertivPowerAssistConfigEntry
from .const import (
    KEY_BATTERY_VOLTAGE,
    KEY_CAPACITY,
    KEY_INPUT_VOLTAGES,
    KEY_OUTPUT_VOLTAGES,
    KEY_PERCENT_LOAD,
    KEY_RUN_TIME,
    STATUS_KEY,
)
from .entity import VertivPowerAssistBaseEntity


@dataclass(frozen=True, kw_only=True)
class VertivPowerAssistSensorEntityDescription(SensorEntityDescription):
    """Describes a Vertiv PowerAssist Sensor Entity."""

    api_key: str


SENSOR_DESCRIPTIONS: tuple[VertivPowerAssistSensorEntityDescription, ...] = (
    VertivPowerAssistSensorEntityDescription(
        key="runtime_remaining",
        api_key=KEY_RUN_TIME,
        translation_key="runtime_remaining",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VertivPowerAssistSensorEntityDescription(
        key="battery_capacity_percent",
        api_key=KEY_CAPACITY,
        translation_key="battery_capacity_percent",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    VertivPowerAssistSensorEntityDescription(
        key="battery_voltage_reading",
        api_key=KEY_BATTERY_VOLTAGE,
        translation_key="battery_voltage_reading",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VertivPowerAssistSensorEntityDescription(
        key="output_load_percent",
        api_key=KEY_PERCENT_LOAD,
        translation_key="output_load_percent",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:gauge",  # Changed icon to better reflect load percentage
        state_class=SensorStateClass.MEASUREMENT,
    ),
    VertivPowerAssistSensorEntityDescription(
        key="input_voltage_reading",
        api_key=KEY_INPUT_VOLTAGES,
        translation_key="input_voltage_reading",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    VertivPowerAssistSensorEntityDescription(
        key="output_voltage_reading",
        api_key=KEY_OUTPUT_VOLTAGES,
        translation_key="output_voltage_reading",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: VertivPowerAssistConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Vertiv PowerAssist sensors."""

    entities = [
        VertivPowerAssistSensor(config_entry, description)
        for description in SENSOR_DESCRIPTIONS
    ]

    async_add_entities(entities)


class VertivPowerAssistSensor(VertivPowerAssistBaseEntity, SensorEntity):
    """Representation of a sensor entity for the Vertiv PowerAssist device."""

    entity_description: VertivPowerAssistSensorEntityDescription

    def __init__(
        self,
        entry: VertivPowerAssistConfigEntry,
        description: VertivPowerAssistSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(entry, description)
        self.entity_description = description

    @property
    def native_value(self) -> str | int | float | datetime | None:
        """Return the state of the sensor."""

        data = self.coordinator.data
        if not data:
            return None
        status_data: dict[str, Any] | None = data.get(STATUS_KEY)
        if status_data is None:
            return None
        raw_value = status_data.get(self.entity_description.api_key)

        # Handle nested voltage structures: {"voltages": [..]}
        if isinstance(raw_value, dict) and "voltages" in raw_value:
            voltages = raw_value.get("voltages")
            if isinstance(voltages, list) and voltages:
                first = voltages[0]
                if isinstance(first, (int, float, str)):
                    return cast(int | float | str, first)
            return None

        # Only return scalar types supported by the entity
        if isinstance(raw_value, (str, int, float, datetime)):
            return cast(str | int | float | datetime, raw_value)

        return None
