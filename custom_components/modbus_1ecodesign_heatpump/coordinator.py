"""DataUpdateCoordinator for Modbus 1EcoDesign Heatpump."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN
from .modbus import (
    REGISTER_TYPE_HOLDING,
    REGISTER_TYPE_INPUT,
    Modbus1EcoDesignClient,
    ModbusConnectionError,
    ModbusReadError,
    ModbusWriteError,
    RegisterBlock,
)

_LOGGER = logging.getLogger(__name__)

DEFAULT_READ_BLOCKS = [
    RegisterBlock(register_type=REGISTER_TYPE_INPUT, start=0, count=19),
    RegisterBlock(register_type=REGISTER_TYPE_INPUT, start=119, count=1),
    RegisterBlock(register_type=REGISTER_TYPE_HOLDING, start=4, count=30),
]


class Modbus1EcoDesignUpdateCoordinator(
    DataUpdateCoordinator[dict[str, dict[int, int]]]
):
    """Coordinator for grouped Modbus register reads."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: Modbus1EcoDesignClient,
    ) -> None:
        self._entry = entry
        self._client = client
        scan_interval = int(
            entry.options.get(
                CONF_SCAN_INTERVAL,
                entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            )
        )
        super().__init__(
            hass,
            logger=_LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict[str, dict[int, int]]:
        try:
            return await self._client.async_read_register_blocks(DEFAULT_READ_BLOCKS)
        except (ModbusConnectionError, ModbusReadError) as err:
            raise UpdateFailed(str(err)) from err

    async def async_write_holding_register(self, address: int, value: int) -> None:
        try:
            await self._client.async_write_holding_register(address=address, value=value)
        except ModbusWriteError as err:
            raise UpdateFailed(str(err)) from err
        await self.async_request_refresh()

