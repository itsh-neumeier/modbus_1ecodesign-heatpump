"""Base entity helpers."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_NAME, DOMAIN, MANUFACTURER, MODEL
from .coordinator import Modbus1EcoDesignUpdateCoordinator


class Modbus1EcoDesignEntity(CoordinatorEntity[Modbus1EcoDesignUpdateCoordinator]):
    """Common base for all entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: Modbus1EcoDesignUpdateCoordinator,
        entry: ConfigEntry,
        key: str,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{key}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._entry.data.get(CONF_NAME, DEFAULT_NAME),
            manufacturer=MANUFACTURER,
            model=MODEL,
            configuration_url=f"http://{self._entry.data[CONF_HOST]}:{self._entry.data[CONF_PORT]}",
        )

    def _read_register(self, register_type: str, address: int) -> int | None:
        data = self.coordinator.data or {}
        registers = data.get(register_type, {})
        value = registers.get(address)
        if value is None:
            return None
        return int(value)

