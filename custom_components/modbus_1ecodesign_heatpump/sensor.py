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

STATUS_FLAG_LABELS = {
    "status_off": {"de": "Aus", "en": "Off"},
    "status_ready": {"de": "Betriebsbereit", "en": "Ready"},
    "status_running": {"de": "In Betrieb", "en": "Running"},
    "status_legionella_mode": {"de": "Legionellenmodus", "en": "Legionella mode"},
    "status_legionella_mode_end": {"de": "Legionellenmodus-Ende", "en": "Legionella mode end"},
    "status_defrost": {"de": "Abtau", "en": "Defrost"},
    "status_defrost_end": {"de": "Abtau-Ende", "en": "Defrost end"},
    "status_fault": {"de": "Stoerung", "en": "Fault"},
    "status_boost": {"de": "Boost", "en": "Boost"},
    "status_hp_locked": {"de": "WP Gesperrt", "en": "Heat pump locked"},
    "status_holiday": {"de": "Ferien", "en": "Holiday"},
    "status_sg_enabled": {"de": "SG-ENABLED", "en": "SG-ENABLED"},
    "status_pv_hp": {"de": "PV-WP", "en": "PV-HP"},
    "status_pv_el": {"de": "PV-EL", "en": "PV-EL"},
    "status_pv_hp_el": {"de": "PV-WP+EL", "en": "PV-HP+EL"},
}

ALARM_FLAG_LABELS = {
    "alarm_tank_sensor_short": {
        "de": "Speicherfuehler: Kurzschluss",
        "en": "Tank sensor: short circuit",
    },
    "alarm_tank_sensor_open": {
        "de": "Speicherfuehler: Unterbrechung",
        "en": "Tank sensor: open circuit",
    },
    "alarm_evaporator_sensor_short": {
        "de": "Verdampferfuehler: Kurzschluss",
        "en": "Evaporator sensor: short circuit",
    },
    "alarm_evaporator_sensor_open": {
        "de": "Verdampferfuehler: Unterbrechung",
        "en": "Evaporator sensor: open circuit",
    },
    "alarm_pressostat_first": {"de": "1ste Pressostat Meldung", "en": "1st pressostat warning"},
    "alarm_pressostat_fault": {"de": "Pressostat Stoerung", "en": "Pressostat fault"},
    "alarm_check_anode": {"de": "Anode kontrollieren", "en": "Check anode"},
    "alarm_legio_temp_not_reached": {
        "de": "Legio Temperatur nicht erreicht",
        "en": "Legionella temperature not reached",
    },
    "alarm_set_clock": {"de": "Uhrzeit einstellen!", "en": "Set clock!"},
}

NO_FLAGS_TEXT = {
    "de": "Keine",
    "en": "None",
}


@dataclass(frozen=True, kw_only=True)
class ModbusSensorDescription(SensorEntityDescription):
    """Description for a Modbus numeric sensor."""

    address: int
    register_type: str = REGISTER_TYPE_INPUT
    scale: float = 1.0
    offset: float = 0.0
    bit_flags: dict[int, str] | None = None
    bit_label_map: dict[str, dict[str, str]] | None = None


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
            1: "status_off",
            2: "status_ready",
            4: "status_running",
            8: "status_legionella_mode",
            32: "status_legionella_mode_end",
            64: "status_defrost",
            128: "status_defrost_end",
            256: "status_fault",
            512: "status_boost",
            1024: "status_hp_locked",
            2048: "status_holiday",
            4096: "status_sg_enabled",
            8192: "status_pv_hp",
            16384: "status_pv_el",
            32768: "status_pv_hp_el",
        },
        bit_label_map=STATUS_FLAG_LABELS,
    ),
    ModbusSensorDescription(
        key="unit_alarm_bits",
        translation_key="unit_alarm_bits",
        address=18,
        icon="mdi:alarm-light-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        bit_flags={
            1 << 0: "alarm_tank_sensor_short",
            1 << 1: "alarm_tank_sensor_open",
            1 << 2: "alarm_evaporator_sensor_short",
            1 << 3: "alarm_evaporator_sensor_open",
            1 << 4: "alarm_pressostat_first",
            1 << 5: "alarm_pressostat_fault",
            1 << 6: "alarm_check_anode",
            1 << 7: "alarm_legio_temp_not_reached",
            1 << 8: "alarm_set_clock",
        },
        bit_label_map=ALARM_FLAG_LABELS,
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
    def native_value(self) -> float | int | str | None:
        raw = self._read_register(
            register_type=self.entity_description.register_type,
            address=self.entity_description.address,
        )
        if raw is None:
            return None

        if self.entity_description.bit_flags is not None:
            active_flags = self._active_flags(raw)
            if not active_flags:
                return self._localized_no_flags_text()
            return ", ".join(active_flags)

        value = (raw * self.entity_description.scale) + self.entity_description.offset
        if self.entity_description.scale != 1.0:
            return round(value, self.entity_description.suggested_display_precision or 1)
        return int(value)

    @property
    def extra_state_attributes(self) -> dict[str, int | list[str]] | None:
        if self.entity_description.bit_flags is None:
            return None
        raw = self._read_register(
            register_type=self.entity_description.register_type,
            address=self.entity_description.address,
        )
        if raw is None:
            return None
        active_flags = self._active_flags(raw)
        return {
            "raw_value": raw,
            "active_flags": active_flags,
        }

    def _active_flags(self, raw: int) -> list[str]:
        bit_flags = self.entity_description.bit_flags or {}
        return [
            self._localize_flag(flag_key)
            for mask, flag_key in bit_flags.items()
            if raw & mask
        ]

    def _localize_flag(self, flag_key: str) -> str:
        labels = self.entity_description.bit_label_map or {}
        localized = labels.get(flag_key, {})
        language = self._language_code()
        return localized.get(language, localized.get("en", flag_key))

    def _localized_no_flags_text(self) -> str:
        language = self._language_code()
        return NO_FLAGS_TEXT.get(language, NO_FLAGS_TEXT["en"])

    def _language_code(self) -> str:
        language = (self.hass.config.language or "en").lower()
        return "de" if language.startswith("de") else "en"
