"""Time platform for Modbus 1EcoDesign Heatpump."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import time as dt_time
from typing import Any

from homeassistant.components.time import TimeEntity, TimeEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .device_profile import get_entity_override, get_timer_config, is_entity_excluded
from .entity import Modbus1EcoDesignEntity
from .modbus import REGISTER_TYPE_HOLDING


@dataclass(frozen=True, kw_only=True)
class ModbusTimeDescription(TimeEntityDescription):
    """Description for timer time register pair."""

    hour_address: int
    minute_address: int
    register_type: str = REGISTER_TYPE_HOLDING


BASE_TIME_TYPES: tuple[ModbusTimeDescription, ...] = (
    ModbusTimeDescription(
        key="timer_start",
        translation_key="timer_start",
        icon="mdi:clock-start",
        hour_address=8,
        minute_address=9,
        entity_category=EntityCategory.CONFIG,
    ),
    ModbusTimeDescription(
        key="timer_stop",
        translation_key="timer_stop",
        icon="mdi:clock-end",
        hour_address=10,
        minute_address=11,
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    profile = hass.data[DOMAIN][entry.entry_id]["profile"]
    time_types = _build_time_types(profile)
    if not time_types:
        return
    async_add_entities(
        Modbus1EcoDesignTime(coordinator=coordinator, entry=entry, description=description)
        for description in time_types
    )


class Modbus1EcoDesignTime(Modbus1EcoDesignEntity, TimeEntity):
    """Time entity mapped to hour+minute holding registers."""

    entity_description: ModbusTimeDescription

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        description: ModbusTimeDescription,
    ) -> None:
        super().__init__(coordinator=coordinator, entry=entry, key=description.key)
        self.entity_description = description

    @property
    def native_value(self) -> dt_time | None:
        hour = self._read_register(
            register_type=self.entity_description.register_type,
            address=self.entity_description.hour_address,
        )
        minute = self._read_register(
            register_type=self.entity_description.register_type,
            address=self.entity_description.minute_address,
        )
        if hour is None or minute is None:
            return None
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            return None
        return dt_time(hour=hour, minute=minute)

    async def async_set_value(self, value: dt_time) -> None:
        if not (0 <= value.hour <= 23 and 0 <= value.minute <= 59):
            raise ValueError("Timer value out of range")
        await self.coordinator.async_write_holding_registers(
            {
                self.entity_description.hour_address: int(value.hour),
                self.entity_description.minute_address: int(value.minute),
            }
        )


def _build_time_types(profile: dict[str, Any]) -> tuple[ModbusTimeDescription, ...]:
    timer = get_timer_config(profile)
    if not timer["supported"]:
        return ()

    start_hour = timer["start_hour_register"]
    start_minute = timer["start_minute_register"]
    stop_hour = timer["stop_hour_register"]
    stop_minute = timer["stop_minute_register"]
    if None in (start_hour, start_minute, stop_hour, stop_minute):
        return ()

    register_map = {
        "timer_start": {"hour_address": start_hour, "minute_address": start_minute},
        "timer_stop": {"hour_address": stop_hour, "minute_address": stop_minute},
    }

    result: list[ModbusTimeDescription] = []
    for description in BASE_TIME_TYPES:
        if is_entity_excluded(profile, "time", description.key):
            continue
        merged_override = {
            **register_map.get(description.key, {}),
            **get_entity_override(profile, "time", description.key),
        }
        result.append(_apply_time_override(description, merged_override))
    return tuple(result)


def _apply_time_override(
    description: ModbusTimeDescription,
    override: dict[str, Any],
) -> ModbusTimeDescription:
    if not override:
        return description
    allowed = {
        "translation_key",
        "icon",
        "hour_address",
        "minute_address",
        "register_type",
        "entity_registry_enabled_default",
    }
    update_data: dict[str, Any] = {key: value for key, value in override.items() if key in allowed}
    if "hour_address" in update_data:
        update_data["hour_address"] = int(update_data["hour_address"])
    if "minute_address" in update_data:
        update_data["minute_address"] = int(update_data["minute_address"])
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
