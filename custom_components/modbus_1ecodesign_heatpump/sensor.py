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
    bit_flags: dict[int, str] | None = None


SENSOR_TYPES: tuple[ModbusSensorDescription, ...] = (
    ModbusSensorDescription(
        key="t1_evaporator_temperature",
        translation_key="t1_evaporator_temperature",
        address=7,
        scale=0.1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    ModbusSensorDescription(
        key="t2_tank_temperature",
        translation_key="t2_tank_temperature",
        address=8,
        scale=0.1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    ModbusSensorDescription(
        key="remaining_holiday_days",
        translation_key="remaining_holiday_days",
        address=17,
        icon="mdi:calendar-clock",
    ),
    ModbusSensorDescription(
        key="status_bits",
        translation_key="status_bits",
        address=16,
        icon="mdi:information-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        bit_flags={
            1: "Aus",
            2: "Betriebsbereit",
            4: "In Betrieb",
            8: "Legionellenmodus",
            32: "Legionellenmodus-Ende",
            64: "Abtau",
            128: "Abtau-Ende",
            256: "Stoerung",
            512: "Boost",
            1024: "WP Gesperrt",
            2048: "Ferien",
            4096: "SG-ENABLED",
            8192: "PV-WP",
            16384: "PV-EL",
            32768: "PV-WP+EL",
        },
    ),
    ModbusSensorDescription(
        key="unit_alarm_bits",
        translation_key="unit_alarm_bits",
        address=18,
        icon="mdi:alarm-light-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        bit_flags={
            1 << 0: "Speicherfuehler: Kurzschluss",
            1 << 1: "Speicherfuehler: Unterbrechung",
            1 << 2: "Verdampferfuehler: Kurzschluss",
            1 << 3: "Verdampferfuehler: Unterbrechung",
            1 << 4: "1ste Pressostat Meldung",
            1 << 5: "Pressostat Stoerung",
            1 << 6: "Anode kontrollieren",
            1 << 7: "Legio Temperatur nicht erreicht",
            1 << 8: "Uhrzeit einstellen!",
        },
    ),
    ModbusSensorDescription(
        key="firmware_version",
        translation_key="firmware_version",
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

    @property
    def extra_state_attributes(self) -> dict[str, list[str]] | None:
        if self.entity_description.bit_flags is None:
            return None
        raw = self._read_register(
            register_type=self.entity_description.register_type,
            address=self.entity_description.address,
        )
        if raw is None:
            return None
        active_flags = [
            label
            for mask, label in self.entity_description.bit_flags.items()
            if raw & mask
        ]
        return {"active_flags": active_flags}
