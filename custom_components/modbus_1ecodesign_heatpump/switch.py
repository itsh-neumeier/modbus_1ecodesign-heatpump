"""Switch platform for Modbus 1EcoDesign Heatpump."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import Modbus1EcoDesignEntity
from .modbus import REGISTER_TYPE_HOLDING


@dataclass(frozen=True, kw_only=True)
class ModbusSwitchDescription(SwitchEntityDescription):
    """Description for writable switch-like holding registers."""

    address: int
    on_value: int = 1
    off_value: int = 0
    register_type: str = REGISTER_TYPE_HOLDING


SWITCH_TYPES: tuple[ModbusSwitchDescription, ...] = (
    ModbusSwitchDescription(
        key="timer_enabled",
        name="Timer Enabled",
        address=7,
        icon="mdi:timer-outline",
        entity_category=EntityCategory.CONFIG,
    ),
    ModbusSwitchDescription(
        key="boost_enabled",
        name="Boost Enabled",
        address=22,
        icon="mdi:rocket-launch-outline",
    ),
    ModbusSwitchDescription(
        key="anode_enabled",
        name="Anode Enabled",
        address=27,
        icon="mdi:lightning-bolt-outline",
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities(
        Modbus1EcoDesignSwitch(coordinator=coordinator, entry=entry, description=description)
        for description in SWITCH_TYPES
    )


class Modbus1EcoDesignSwitch(Modbus1EcoDesignEntity, SwitchEntity):
    """Switch mapped to writable holding register."""

    entity_description: ModbusSwitchDescription

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        description: ModbusSwitchDescription,
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
        return raw == self.entity_description.on_value

    async def async_turn_on(self, **kwargs) -> None:  # noqa: ANN003
        await self.coordinator.async_write_holding_register(
            address=self.entity_description.address,
            value=self.entity_description.on_value,
        )

    async def async_turn_off(self, **kwargs) -> None:  # noqa: ANN003
        await self.coordinator.async_write_holding_register(
            address=self.entity_description.address,
            value=self.entity_description.off_value,
        )
