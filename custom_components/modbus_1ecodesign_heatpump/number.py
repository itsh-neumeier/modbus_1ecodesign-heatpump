"""Number platform for Modbus 1EcoDesign Heatpump."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .device_profile import get_entity_override, is_entity_excluded
from .entity import Modbus1EcoDesignEntity
from .modbus import REGISTER_TYPE_HOLDING


@dataclass(frozen=True, kw_only=True)
class ModbusNumberDescription(NumberEntityDescription):
    """Description for writable numeric holding registers."""

    address: int
    register_type: str = REGISTER_TYPE_HOLDING
    scale: float = 1.0
    offset: float = 0.0


BASE_NUMBER_TYPES: tuple[ModbusNumberDescription, ...] = (
    ModbusNumberDescription(
        key="water_setpoint",
        translation_key="water_setpoint",
        address=4,
        native_min_value=5,
        native_max_value=62,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    ModbusNumberDescription(
        key="t_min",
        translation_key="t_min",
        address=5,
        native_min_value=5,
        native_max_value=62,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_category=EntityCategory.CONFIG,
    ),
    ModbusNumberDescription(
        key="t2_min",
        translation_key="t2_min",
        address=6,
        native_min_value=5,
        native_max_value=62,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_category=EntityCategory.CONFIG,
    ),
    ModbusNumberDescription(
        key="pv_hp_setpoint",
        translation_key="pv_hp_setpoint",
        address=18,
        native_min_value=5,
        native_max_value=62,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    ModbusNumberDescription(
        key="pv_el_setpoint",
        translation_key="pv_el_setpoint",
        address=19,
        native_min_value=5,
        native_max_value=62,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    ModbusNumberDescription(
        key="manual_holiday_days",
        translation_key="manual_holiday_days",
        address=21,
        native_min_value=1,
        native_max_value=99,
        native_step=1,
        icon="mdi:calendar-arrow-right",
        entity_registry_enabled_default=False,
    ),
    ModbusNumberDescription(
        key="t_max",
        translation_key="t_max",
        address=28,
        native_min_value=5,
        native_max_value=62,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_category=EntityCategory.CONFIG,
    ),
    ModbusNumberDescription(
        key="ec_fan_level1",
        translation_key="ec_fan_level1",
        address=30,
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    ModbusNumberDescription(
        key="ec_fan_level2",
        translation_key="ec_fan_level2",
        address=31,
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    ModbusNumberDescription(
        key="ec_fan_level3",
        translation_key="ec_fan_level3",
        address=32,
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
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
    number_types = _build_number_types(profile)
    async_add_entities(
        Modbus1EcoDesignNumber(coordinator=coordinator, entry=entry, description=description)
        for description in number_types
    )


class Modbus1EcoDesignNumber(Modbus1EcoDesignEntity, NumberEntity):
    """Number mapped to writable holding register."""

    entity_description: ModbusNumberDescription

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        description: ModbusNumberDescription,
    ) -> None:
        super().__init__(coordinator=coordinator, entry=entry, key=description.key)
        self.entity_description = description

    @property
    def native_value(self) -> float | None:
        raw = self._read_register(
            register_type=self.entity_description.register_type,
            address=self.entity_description.address,
        )
        if raw is None:
            return None
        return (raw * self.entity_description.scale) + self.entity_description.offset

    async def async_set_native_value(self, value: float) -> None:
        raw = int(round((value - self.entity_description.offset) / self.entity_description.scale))
        await self.coordinator.async_write_holding_register(
            address=self.entity_description.address,
            value=raw,
        )


def _build_number_types(profile: dict[str, Any]) -> tuple[ModbusNumberDescription, ...]:
    result: list[ModbusNumberDescription] = []
    for description in BASE_NUMBER_TYPES:
        if is_entity_excluded(profile, "number", description.key):
            continue
        override = get_entity_override(profile, "number", description.key)
        result.append(_apply_number_override(description, override))
    return tuple(result)


def _apply_number_override(
    description: ModbusNumberDescription,
    override: dict[str, Any],
) -> ModbusNumberDescription:
    if not override:
        return description
    allowed = {
        "translation_key",
        "icon",
        "address",
        "register_type",
        "scale",
        "offset",
        "native_min_value",
        "native_max_value",
        "native_step",
        "entity_registry_enabled_default",
    }
    update_data: dict[str, Any] = {key: value for key, value in override.items() if key in allowed}
    if "address" in update_data:
        update_data["address"] = int(update_data["address"])
    if "register_type" in update_data:
        update_data["register_type"] = str(update_data["register_type"]).strip().lower()
    if "scale" in update_data:
        update_data["scale"] = float(update_data["scale"])
    if "offset" in update_data:
        update_data["offset"] = float(update_data["offset"])
    if "native_min_value" in update_data:
        update_data["native_min_value"] = float(update_data["native_min_value"])
    if "native_max_value" in update_data:
        update_data["native_max_value"] = float(update_data["native_max_value"])
    if "native_step" in update_data:
        update_data["native_step"] = float(update_data["native_step"])
    if "translation_key" in update_data:
        update_data["translation_key"] = str(update_data["translation_key"])
    if "icon" in update_data:
        update_data["icon"] = str(update_data["icon"])
    if "entity_registry_enabled_default" in update_data:
        update_data["entity_registry_enabled_default"] = bool(
            update_data["entity_registry_enabled_default"]
        )
    return replace(description, **update_data)
