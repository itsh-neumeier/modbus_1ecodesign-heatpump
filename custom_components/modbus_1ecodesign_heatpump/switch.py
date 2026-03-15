"""Switch platform for Modbus 1EcoDesign Heatpump."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .device_profile import get_entity_override, is_entity_excluded
from .entity import Modbus1EcoDesignEntity
from .modbus import REGISTER_TYPE_HOLDING


@dataclass(frozen=True, kw_only=True)
class ModbusSwitchDescription(SwitchEntityDescription):
    """Description for writable switch-like holding registers."""

    address: int
    on_value: int = 1
    off_value: int = 0
    register_type: str = REGISTER_TYPE_HOLDING


BASE_SWITCH_TYPES: tuple[ModbusSwitchDescription, ...] = (
    ModbusSwitchDescription(
        key="timer_enabled",
        translation_key="timer_enabled",
        address=7,
        icon="mdi:timer-outline",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    ModbusSwitchDescription(
        key="boost_enabled",
        translation_key="boost_enabled",
        address=22,
        icon="mdi:rocket-launch-outline",
    ),
    ModbusSwitchDescription(
        key="anode_enabled",
        translation_key="anode_enabled",
        address=27,
        icon="mdi:lightning-bolt-outline",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    profile = hass.data[DOMAIN][entry.entry_id]["profile"]
    switch_types = _build_switch_types(profile)
    async_add_entities(
        Modbus1EcoDesignSwitch(coordinator=coordinator, entry=entry, description=description)
        for description in switch_types
    )


class Modbus1EcoDesignSwitch(Modbus1EcoDesignEntity, SwitchEntity):
    """Switch mapped to writable holding register."""

    entity_description: ModbusSwitchDescription

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        description: ModbusSwitchDescription,
    ) -> None:
        super().__init__(coordinator=coordinator, entry=entry, key=description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        raw = self._read_register(
            register_type=self.entity_description.register_type,
            address=self.entity_description.address,
        )
        if raw is None:
            return None
        return raw == self.entity_description.on_value

    async def async_turn_on(self, **kwargs) -> None:  # noqa: ANN003
        await self.coordinator.async_write_holding_register(
            address=self.entity_description.address,
            value=self.entity_description.on_value,
        )

    async def async_turn_off(self, **kwargs) -> None:  # noqa: ANN003
        await self.coordinator.async_write_holding_register(
            address=self.entity_description.address,
            value=self.entity_description.off_value,
        )


def _build_switch_types(profile: dict[str, Any]) -> tuple[ModbusSwitchDescription, ...]:
    result: list[ModbusSwitchDescription] = []
    for description in BASE_SWITCH_TYPES:
        if is_entity_excluded(profile, "switch", description.key):
            continue
        override = get_entity_override(profile, "switch", description.key)
        result.append(_apply_switch_override(description, override))
    return tuple(result)


def _apply_switch_override(
    description: ModbusSwitchDescription,
    override: dict[str, Any],
) -> ModbusSwitchDescription:
    if not override:
        return description
    allowed = {
        "translation_key",
        "icon",
        "address",
        "register_type",
        "on_value",
        "off_value",
        "entity_registry_enabled_default",
    }
    update_data: dict[str, Any] = {key: value for key, value in override.items() if key in allowed}
    if "address" in update_data:
        update_data["address"] = int(update_data["address"])
    if "register_type" in update_data:
        update_data["register_type"] = str(update_data["register_type"]).strip().lower()
    if "on_value" in update_data:
        update_data["on_value"] = int(update_data["on_value"])
    if "off_value" in update_data:
        update_data["off_value"] = int(update_data["off_value"])
    if "translation_key" in update_data:
        update_data["translation_key"] = str(update_data["translation_key"])
    if "icon" in update_data:
        update_data["icon"] = str(update_data["icon"])
    if "entity_registry_enabled_default" in update_data:
        update_data["entity_registry_enabled_default"] = bool(
            update_data["entity_registry_enabled_default"]
        )
    return replace(description, **update_data)
