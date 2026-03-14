"""Number platform for Modbus 1EcoDesign Heatpump."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import Modbus1EcoDesignEntity
from .modbus import REGISTER_TYPE_HOLDING


@dataclass(frozen=True, kw_only=True)
class ModbusNumberDescription(NumberEntityDescription):
    """Description for writable numeric holding registers."""

    address: int
    register_type: str = REGISTER_TYPE_HOLDING
    scale: float = 1.0
    offset: float = 0.0


NUMBER_TYPES: tuple[ModbusNumberDescription, ...] = (
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
    async_add_entities(
        Modbus1EcoDesignNumber(coordinator=coordinator, entry=entry, description=description)
        for description in NUMBER_TYPES
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
