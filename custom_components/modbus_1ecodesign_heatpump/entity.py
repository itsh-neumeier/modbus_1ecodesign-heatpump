"""Base entity helpers."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_NAME, DOMAIN
from .coordinator import Modbus1EcoDesignUpdateCoordinator
from .device_profile import get_profile_manufacturer, get_profile_model


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
        profile = self.coordinator.profile
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            via_device=gateway_device_identifier(self._entry),
            name=self._entry.data.get(CONF_NAME, DEFAULT_NAME),
            manufacturer=get_profile_manufacturer(profile),
            model=get_profile_model(profile),
            configuration_url=f"http://{self._entry.data[CONF_HOST]}:80",
        )

    def _read_register(self, register_type: str, address: int) -> int | None:
        data = self.coordinator.data or {}
        registers = data.get(register_type, {})
        value = registers.get(address)
        if value is None:
            return None
        return int(value)


def gateway_device_identifier(entry: ConfigEntry) -> tuple[str, str]:
    """Return stable gateway device identifier tuple."""
    return (DOMAIN, f"{entry.entry_id}_gateway")


def gateway_device_name(entry: ConfigEntry) -> str:
    """Build gateway device display name."""
    base_name = str(entry.data.get(CONF_NAME, DEFAULT_NAME))
    return f"{base_name} Modbus TCP Gateway"


def gateway_configuration_url(entry: ConfigEntry) -> str:
    """Gateway HTTP page for visit button."""
    return f"http://{entry.data[CONF_HOST]}:80"
