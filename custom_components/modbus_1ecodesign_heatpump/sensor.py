"""Sensor platform for Modbus 1EcoDesign Heatpump."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import Modbus1EcoDesignEntity
from .modbus import REGISTER_TYPE_INPUT


@dataclass(frozen=True, kw_only=True)
class ModbusSensorDescription(SensorEntityDescription):
    """Description for a Modbus numeric sensor."""

    address: int
    register_type: str = REGISTER_TYPE_INPUT
    scale: float = 1.0
    offset: float = 0.0


SENSOR_TYPES: tuple[ModbusSensorDescription, ...] = (
    ModbusSensorDescription(
        key="t1_evaporator_temperature",
        name="T1 Evaporator Temperature",
        address=7,
        scale=0.1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    ModbusSensorDescription(
        key="t2_tank_temperature",
        name="T2 Tank Temperature",
        address=8,
        scale=0.1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    ModbusSensorDescription(
        key="remaining_holiday_days",
        name="Remaining Holiday Days",
        address=17,
        icon="mdi:calendar-clock",
    ),
    ModbusSensorDescription(
        key="status_bits",
        name="Status Bits",
        address=16,
        icon="mdi:information-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ModbusSensorDescription(
        key="unit_alarm_bits",
        name="Unit Alarm Bits",
        address=18,
        icon="mdi:alarm-light-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ModbusSensorDescription(
        key="firmware_version",
        name="Firmware Version",
        address=119,
        scale=0.1,
        icon="mdi:chip",
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=1,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities(
        Modbus1EcoDesignSensor(coordinator=coordinator, entry=entry, description=description)
        for description in SENSOR_TYPES
    )


class Modbus1EcoDesignSensor(Modbus1EcoDesignEntity, SensorEntity):
    """Numeric sensor from one Modbus register."""

    entity_description: ModbusSensorDescription

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        description: ModbusSensorDescription,
    ) -> None:
        super().__init__(coordinator=coordinator, entry=entry, key=description.key)
        self.entity_description = description

    @property
    def native_value(self) -> float | int | None:
        raw = self._read_register(
            register_type=self.entity_description.register_type,
            address=self.entity_description.address,
        )
        if raw is None:
            return None

        value = (raw * self.entity_description.scale) + self.entity_description.offset
        if self.entity_description.scale != 1.0:
            return round(value, self.entity_description.suggested_display_precision or 1)
        return int(value)

