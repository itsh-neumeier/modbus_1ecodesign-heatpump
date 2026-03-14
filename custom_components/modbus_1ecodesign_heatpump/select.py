"""Select platform for Modbus 1EcoDesign Heatpump."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import Modbus1EcoDesignEntity
from .modbus import REGISTER_TYPE_HOLDING


@dataclass(frozen=True, kw_only=True)
class ModbusSelectDescription(SelectEntityDescription):
    """Description for enum-like writable holding registers."""

    address: int
    option_map: dict[int, str]
    register_type: str = REGISTER_TYPE_HOLDING


SELECT_TYPES: tuple[ModbusSelectDescription, ...] = (
    ModbusSelectDescription(
        key="heating_mode",
        name="Heating Mode",
        address=12,
        option_map={
            0: "Off",
            1: "Only HP",
            2: "Only EL",
            3: "HP + EL",
            4: "Boiler",
            5: "HP + Boiler",
        },
        entity_category=EntityCategory.CONFIG,
    ),
    ModbusSelectDescription(
        key="legionella_function",
        name="Legionella Function",
        address=13,
        option_map={0: "Off", 1: "60 C", 2: "65 C"},
        entity_category=EntityCategory.CONFIG,
    ),
    ModbusSelectDescription(
        key="fan_operation",
        name="Fan Operation",
        address=15,
        option_map={0: "Off", 1: "EC Low", 2: "EC Mid", 3: "EC High"},
        entity_category=EntityCategory.CONFIG,
    ),
    ModbusSelectDescription(
        key="ventilation_control",
        name="Ventilation Control",
        address=16,
        option_map={0: "Off", 1: "EC Low", 2: "EC Mid", 3: "EC High"},
        entity_category=EntityCategory.CONFIG,
    ),
    ModbusSelectDescription(
        key="pv_mode",
        name="PV Mode",
        address=17,
        option_map={0: "Off", 1: "Only HP", 2: "Only EL", 3: "HP + EL"},
    ),
    ModbusSelectDescription(
        key="holiday_mode",
        name="Holiday Mode",
        address=20,
        option_map={0: "Off", 1: "1 Week", 2: "2 Weeks", 3: "3 Weeks", 4: "3 Days", 5: "Manual"},
    ),
    ModbusSelectDescription(
        key="fan_pause",
        name="Fan Pause",
        address=23,
        option_map={
            0: "Off",
            1: "30m/15s",
            2: "30m/30s",
            3: "60m/15s",
            4: "60m/30s",
            5: "90m/15s",
            6: "90m/30s",
        },
        entity_category=EntityCategory.CONFIG,
    ),
    ModbusSelectDescription(
        key="language",
        name="Language",
        address=25,
        option_map={
            0: "English",
            1: "German",
            2: "French",
            3: "Dutch",
            4: "Spanish",
            5: "Italian",
            6: "Danish",
            7: "Swedish",
            8: "Norwegian",
            9: "Polish",
            10: "Slovenian",
            11: "Croatian",
        },
        entity_category=EntityCategory.CONFIG,
    ),
    ModbusSelectDescription(
        key="defrost_mode",
        name="Defrost Mode",
        address=26,
        option_map={0: "Air", 1: "Gas", 2: "Tmin RF"},
        entity_category=EntityCategory.CONFIG,
    ),
    ModbusSelectDescription(
        key="fan_type",
        name="Fan Type",
        address=29,
        option_map={0: "AC", 1: "EC"},
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities(
        Modbus1EcoDesignSelect(coordinator=coordinator, entry=entry, description=description)
        for description in SELECT_TYPES
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
