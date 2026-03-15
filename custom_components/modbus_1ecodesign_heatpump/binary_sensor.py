"""Binary sensor platform for Modbus 1EcoDesign Heatpump."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .device_profile import get_entity_override, is_entity_excluded
from .entity import Modbus1EcoDesignEntity
from .modbus import REGISTER_TYPE_INPUT


@dataclass(frozen=True, kw_only=True)
class ModbusBinarySensorDescription(BinarySensorEntityDescription):
    """Description for boolean status registers."""

    address: int
    register_type: str = REGISTER_TYPE_INPUT


BASE_BINARY_SENSOR_TYPES: tuple[ModbusBinarySensorDescription, ...] = (
    ModbusBinarySensorDescription(
        key="di1_pressostat",
        translation_key="di1_pressostat",
        address=0,
        icon="mdi:gauge",
    ),
    ModbusBinarySensorDescription(
        key="di2_pv_input",
        translation_key="di2_pv_input",
        address=1,
        icon="mdi:solar-power-variant",
    ),
    ModbusBinarySensorDescription(
        key="relay_compressor",
        translation_key="relay_compressor",
        address=9,
        icon="mdi:engine",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ModbusBinarySensorDescription(
        key="relay_electric_heater",
        translation_key="relay_electric_heater",
        address=10,
        icon="mdi:heating-coil",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ModbusBinarySensorDescription(
        key="relay_boiler",
        translation_key="relay_boiler",
        address=11,
        icon="mdi:water-boiler",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ModbusBinarySensorDescription(
        key="relay_solenoid_valve",
        translation_key="relay_solenoid_valve",
        address=12,
        icon="mdi:valve",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ModbusBinarySensorDescription(
        key="relay_condenser",
        translation_key="relay_condenser",
        address=13,
        icon="mdi:snowflake",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ModbusBinarySensorDescription(
        key="relay_fan",
        translation_key="relay_fan",
        address=14,
        icon="mdi:fan",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    profile = hass.data[DOMAIN][entry.entry_id]["profile"]
    binary_sensor_types = _build_binary_sensor_types(profile)
    async_add_entities(
        Modbus1EcoDesignBinarySensor(coordinator=coordinator, entry=entry, description=description)
        for description in binary_sensor_types
    )


class Modbus1EcoDesignBinarySensor(Modbus1EcoDesignEntity, BinarySensorEntity):
    """Binary sensor from one Modbus register."""

    entity_description: ModbusBinarySensorDescription

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        description: ModbusBinarySensorDescription,
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
        return bool(raw)


def _build_binary_sensor_types(
    profile: dict[str, Any],
) -> tuple[ModbusBinarySensorDescription, ...]:
    result: list[ModbusBinarySensorDescription] = []
    for description in BASE_BINARY_SENSOR_TYPES:
        if is_entity_excluded(profile, "binary_sensor", description.key):
            continue
        override = get_entity_override(profile, "binary_sensor", description.key)
        result.append(_apply_binary_override(description, override))
    return tuple(result)


def _apply_binary_override(
    description: ModbusBinarySensorDescription,
    override: dict[str, Any],
) -> ModbusBinarySensorDescription:
    if not override:
        return description
    allowed = {
        "translation_key",
        "icon",
        "address",
        "register_type",
        "entity_registry_enabled_default",
    }
    update_data: dict[str, Any] = {key: value for key, value in override.items() if key in allowed}
    if "address" in update_data:
        update_data["address"] = int(update_data["address"])
    if "register_type" in update_data:
        update_data["register_type"] = str(update_data["register_type"]).strip().lower()
    if "translation_key" in update_data:
        update_data["translation_key"] = str(update_data["translation_key"])
    if "icon" in update_data:
        update_data["icon"] = str(update_data["icon"])
    if "entity_registry_enabled_default" in update_data:
        update_data["entity_registry_enabled_default"] = bool(
            update_data["entity_registry_enabled_default"]
        )
    return replace(description, **update_data)
