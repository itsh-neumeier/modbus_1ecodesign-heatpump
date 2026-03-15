"""Select platform for Modbus 1EcoDesign Heatpump."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .device_profile import get_entity_override, is_entity_excluded
from .entity import Modbus1EcoDesignEntity
from .modbus import REGISTER_TYPE_HOLDING


@dataclass(frozen=True, kw_only=True)
class ModbusSelectDescription(SelectEntityDescription):
    """Description for enum-like writable holding registers."""

    address: int
    option_map: dict[int, str]
    register_type: str = REGISTER_TYPE_HOLDING


BASE_SELECT_TYPES: tuple[ModbusSelectDescription, ...] = (
    ModbusSelectDescription(
        key="heating_mode",
        translation_key="heating_mode",
        address=12,
        option_map={
            0: "off",
            1: "only_hp",
            2: "only_el",
            3: "hp_plus_el",
            4: "boiler",
            5: "hp_plus_boiler",
        },
        entity_category=EntityCategory.CONFIG,
    ),
    ModbusSelectDescription(
        key="legionella_function",
        translation_key="legionella_function",
        address=13,
        option_map={0: "off", 1: "temp_60c", 2: "temp_65c"},
        entity_category=EntityCategory.CONFIG,
    ),
    ModbusSelectDescription(
        key="fan_operation",
        translation_key="fan_operation",
        address=15,
        option_map={0: "off", 1: "ec_low", 2: "ec_mid", 3: "ec_high"},
        entity_category=EntityCategory.CONFIG,
    ),
    ModbusSelectDescription(
        key="ventilation_control",
        translation_key="ventilation_control",
        address=16,
        option_map={0: "off", 1: "ec_low", 2: "ec_mid", 3: "ec_high"},
        entity_category=EntityCategory.CONFIG,
    ),
    ModbusSelectDescription(
        key="pv_mode",
        translation_key="pv_mode",
        address=17,
        option_map={0: "off", 1: "only_hp", 2: "only_el", 3: "hp_plus_el"},
    ),
    ModbusSelectDescription(
        key="holiday_mode",
        translation_key="holiday_mode",
        address=20,
        option_map={
            0: "off",
            1: "one_week",
            2: "two_weeks",
            3: "three_weeks",
            4: "three_days",
            5: "manual",
        },
        entity_registry_enabled_default=False,
    ),
    ModbusSelectDescription(
        key="fan_pause",
        translation_key="fan_pause",
        address=23,
        option_map={
            0: "off",
            1: "m30_s15",
            2: "m30_s30",
            3: "m60_s15",
            4: "m60_s30",
            5: "m90_s15",
            6: "m90_s30",
        },
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    ModbusSelectDescription(
        key="language",
        translation_key="language",
        address=25,
        option_map={
            0: "english",
            1: "german",
            2: "french",
            3: "dutch",
            4: "spanish",
            5: "italian",
            6: "danish",
            7: "swedish",
            8: "norwegian",
            9: "polish",
            10: "slovenian",
            11: "croatian",
        },
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    ModbusSelectDescription(
        key="defrost_mode",
        translation_key="defrost_mode",
        address=26,
        option_map={0: "air", 1: "gas", 2: "tmin_rf"},
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    ModbusSelectDescription(
        key="fan_type",
        translation_key="fan_type",
        address=29,
        option_map={0: "ac", 1: "ec"},
        entity_category=EntityCategory.DIAGNOSTIC,
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
    select_types = _build_select_types(profile)
    async_add_entities(
        Modbus1EcoDesignSelect(coordinator=coordinator, entry=entry, description=description)
        for description in select_types
    )


class Modbus1EcoDesignSelect(Modbus1EcoDesignEntity, SelectEntity):
    """Select entity mapped to enum-like holding register."""

    entity_description: ModbusSelectDescription

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        description: ModbusSelectDescription,
    ) -> None:
        super().__init__(coordinator=coordinator, entry=entry, key=description.key)
        self.entity_description = description
        self._attr_options = list(description.option_map.values())

    @property
    def current_option(self) -> str | None:
        raw = self._read_register(
            register_type=self.entity_description.register_type,
            address=self.entity_description.address,
        )
        if raw is None:
            return None
        return self.entity_description.option_map.get(raw)

    async def async_select_option(self, option: str) -> None:
        for raw, mapped_option in self.entity_description.option_map.items():
            if mapped_option == option:
                await self.coordinator.async_write_holding_register(
                    address=self.entity_description.address,
                    value=raw,
                )
                return
        raise ValueError(f"Unsupported option '{option}' for {self.entity_description.key}")


def _build_select_types(profile: dict[str, Any]) -> tuple[ModbusSelectDescription, ...]:
    result: list[ModbusSelectDescription] = []
    for description in BASE_SELECT_TYPES:
        if is_entity_excluded(profile, "select", description.key):
            continue
        override = get_entity_override(profile, "select", description.key)
        result.append(_apply_select_override(description, override))
    return tuple(result)


def _apply_select_override(
    description: ModbusSelectDescription,
    override: dict[str, Any],
) -> ModbusSelectDescription:
    if not override:
        return description
    allowed = {
        "translation_key",
        "icon",
        "address",
        "register_type",
        "option_map",
        "entity_registry_enabled_default",
    }
    update_data: dict[str, Any] = {key: value for key, value in override.items() if key in allowed}
    if "address" in update_data:
        update_data["address"] = int(update_data["address"])
    if "register_type" in update_data:
        update_data["register_type"] = str(update_data["register_type"]).strip().lower()
    if "option_map" in update_data and isinstance(update_data["option_map"], dict):
        update_data["option_map"] = {
            int(raw): str(option) for raw, option in update_data["option_map"].items()
        }
    if "translation_key" in update_data:
        update_data["translation_key"] = str(update_data["translation_key"])
    if "icon" in update_data:
        update_data["icon"] = str(update_data["icon"])
    if "entity_registry_enabled_default" in update_data:
        update_data["entity_registry_enabled_default"] = bool(
            update_data["entity_registry_enabled_default"]
        )
    return replace(description, **update_data)
