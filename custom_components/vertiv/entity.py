"""Base entity for the Vertiv PowerAssist integration."""

from __future__ import annotations

from homeassistant.const import CONF_NAME
from homeassistant.helpers.entity import DeviceInfo, EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import VertivPowerAssistConfigEntry
from .const import DEFAULT_NAME, DOMAIN, KEY_FIRMWARE_VERSION, KEY_MODEL


class VertivPowerAssistBaseEntity(CoordinatorEntity):
    """Base class for all Vertiv PowerAssist entities."""

    _attr_has_entity_name = True

    def __init__(
        self, entry: VertivPowerAssistConfigEntry, description: EntityDescription
    ) -> None:
        """Initialize the Vertiv entity."""

        super().__init__(entry.runtime_data["coordinator"])
        self._runtime_data = entry.runtime_data
        coordinator = self._runtime_data["coordinator"]
        ups_data = coordinator.data
        unique_id = self._runtime_data["unique_id"]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            name=entry.data.get(CONF_NAME) or DEFAULT_NAME,
            manufacturer=ups_data.get("manufacturer"),
            model=ups_data.get(KEY_MODEL),
            sw_version=ups_data.get(KEY_FIRMWARE_VERSION),
            serial_number=ups_data.get("serialNumber"),
        )
        self._attr_unique_id = f"{unique_id}_{description.key}"
