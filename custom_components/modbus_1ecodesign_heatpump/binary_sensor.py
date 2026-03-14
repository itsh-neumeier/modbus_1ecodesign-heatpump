"""Binary sensor platform for Modbus 1EcoDesign Heatpump."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import Modbus1EcoDesignEntity
from .modbus import REGISTER_TYPE_INPUT


@dataclass(frozen=True, kw_only=True)
class ModbusBinarySensorDescription(BinarySensorEntityDescription):
    """Description for boolean status registers."""

    address: int
    register_type: str = REGISTER_TYPE_INPUT
    bitmask: int | None = None


BINARY_SENSOR_TYPES: tuple[ModbusBinarySensorDescription, ...] = (
    ModbusBinarySensorDescription(
        key="di1_pressostat",
        name="DI1 Pressostat",
        address=0,
        icon="mdi:gauge",
    ),
    ModbusBinarySensorDescription(
        key="di2_pv_input",
        name="DI2 PV Input",
        address=1,
        icon="mdi:solar-power-variant",
    ),
    ModbusBinarySensorDescription(
        key="relay_compressor",
        name="Relay Compressor",
        address=9,
        icon="mdi:engine",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ModbusBinarySensorDescription(
        key="relay_electric_heater",
        name="Relay Electric Heater",
        address=10,
        icon="mdi:heating-coil",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ModbusBinarySensorDescription(
        key="relay_boiler",
        name="Relay Boiler",
        address=11,
        icon="mdi:water-boiler",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ModbusBinarySensorDescription(
        key="relay_solenoid_valve",
        name="Relay Solenoid Valve",
        address=12,
        icon="mdi:valve",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ModbusBinarySensorDescription(
        key="relay_condenser",
        name="Relay Condenser",
        address=13,
        icon="mdi:snowflake",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ModbusBinarySensorDescription(
        key="relay_fan",
        name="Relay Fan",
        address=14,
        icon="mdi:fan",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ModbusBinarySensorDescription(
        key="status_bit_off",
        translation_key="status_bit_off",
        address=16,
        bitmask=1,
        icon="mdi:power",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ModbusBinarySensorDescription(
        key="status_bit_ready",
        translation_key="status_bit_ready",
        address=16,
        bitmask=2,
        icon="mdi:check-circle-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ModbusBinarySensorDescription(
        key="status_bit_running",
        translation_key="status_bit_running",
        address=16,
        bitmask=4,
        icon="mdi:play-circle-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ModbusBinarySensorDescription(
        key="status_bit_legionella",
        translation_key="status_bit_legionella",
        address=16,
        bitmask=8,
        icon="mdi:bacteria-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ModbusBinarySensorDescription(
        key="status_bit_legionella_end",
        translation_key="status_bit_legionella_end",
        address=16,
        bitmask=32,
        icon="mdi:bacteria",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ModbusBinarySensorDescription(
        key="status_bit_defrost",
        translation_key="status_bit_defrost",
        address=16,
        bitmask=64,
        icon="mdi:snowflake-melt",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ModbusBinarySensorDescription(
        key="status_bit_defrost_end",
        translation_key="status_bit_defrost_end",
        address=16,
        bitmask=128,
        icon="mdi:snowflake-check",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ModbusBinarySensorDescription(
        key="status_bit_fault",
        translation_key="status_bit_fault",
        address=16,
        bitmask=256,
        icon="mdi:alert-circle-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ModbusBinarySensorDescription(
        key="status_bit_boost",
        translation_key="status_bit_boost",
        address=16,
        bitmask=512,
        icon="mdi:rocket-launch-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ModbusBinarySensorDescription(
        key="status_bit_hp_locked",
        translation_key="status_bit_hp_locked",
        address=16,
        bitmask=1024,
        icon="mdi:lock-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ModbusBinarySensorDescription(
        key="status_bit_holiday",
        translation_key="status_bit_holiday",
        address=16,
        bitmask=2048,
        icon="mdi:beach",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ModbusBinarySensorDescription(
        key="status_bit_sg_enabled",
        translation_key="status_bit_sg_enabled",
        address=16,
        bitmask=4096,
        icon="mdi:transmission-tower",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ModbusBinarySensorDescription(
        key="status_bit_pv_hp",
        translation_key="status_bit_pv_hp",
        address=16,
        bitmask=8192,
        icon="mdi:solar-power-variant",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ModbusBinarySensorDescription(
        key="status_bit_pv_el",
        translation_key="status_bit_pv_el",
        address=16,
        bitmask=16384,
        icon="mdi:solar-power",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ModbusBinarySensorDescription(
        key="status_bit_pv_hp_el",
        translation_key="status_bit_pv_hp_el",
        address=16,
        bitmask=32768,
        icon="mdi:solar-power",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ModbusBinarySensorDescription(
        key="alarm_bit_tank_sensor_short",
        translation_key="alarm_bit_tank_sensor_short",
        address=18,
        bitmask=1 << 0,
        icon="mdi:alert-circle-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    ModbusBinarySensorDescription(
        key="alarm_bit_tank_sensor_open",
        translation_key="alarm_bit_tank_sensor_open",
        address=18,
        bitmask=1 << 1,
        icon="mdi:alert-circle-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    ModbusBinarySensorDescription(
        key="alarm_bit_evaporator_sensor_short",
        translation_key="alarm_bit_evaporator_sensor_short",
        address=18,
        bitmask=1 << 2,
        icon="mdi:alert-circle-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    ModbusBinarySensorDescription(
        key="alarm_bit_evaporator_sensor_open",
        translation_key="alarm_bit_evaporator_sensor_open",
        address=18,
        bitmask=1 << 3,
        icon="mdi:alert-circle-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    ModbusBinarySensorDescription(
        key="alarm_bit_pressostat_first",
        translation_key="alarm_bit_pressostat_first",
        address=18,
        bitmask=1 << 4,
        icon="mdi:alert-circle-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    ModbusBinarySensorDescription(
        key="alarm_bit_pressostat_fault",
        translation_key="alarm_bit_pressostat_fault",
        address=18,
        bitmask=1 << 5,
        icon="mdi:alert-circle-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    ModbusBinarySensorDescription(
        key="alarm_bit_check_anode",
        translation_key="alarm_bit_check_anode",
        address=18,
        bitmask=1 << 6,
        icon="mdi:alert-circle-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    ModbusBinarySensorDescription(
        key="alarm_bit_legio_temp_not_reached",
        translation_key="alarm_bit_legio_temp_not_reached",
        address=18,
        bitmask=1 << 7,
        icon="mdi:alert-circle-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    ModbusBinarySensorDescription(
        key="alarm_bit_set_clock",
        translation_key="alarm_bit_set_clock",
        address=18,
        bitmask=1 << 8,
        icon="mdi:clock-alert-outline",
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
    async_add_entities(
        Modbus1EcoDesignBinarySensor(coordinator=coordinator, entry=entry, description=description)
        for description in BINARY_SENSOR_TYPES
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
        if self.entity_description.bitmask is not None:
            return bool(raw & self.entity_description.bitmask)
        return bool(raw)
