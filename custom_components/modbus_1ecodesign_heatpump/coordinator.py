"""DataUpdateCoordinator for Modbus 1EcoDesign Heatpump."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

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
        profile: dict[str, Any],
    ) -> None:
        self._entry = entry
        self._client = client
        self.profile = profile
        self._read_blocks = _read_blocks_from_profile(profile)
        self.gateway_online = False
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
        self.gateway_online = await self._async_probe_gateway_tcp()
        if not self.gateway_online:
            raise UpdateFailed(
                f"Gateway {self._client.host}:{self._client.port} is not reachable over TCP"
            )
        try:
            return await self._client.async_read_register_blocks(self._read_blocks)
        except (ModbusConnectionError, ModbusReadError) as err:
            self.gateway_online = False
            raise UpdateFailed(str(err)) from err

    async def async_write_holding_register(self, address: int, value: int) -> None:
        try:
            await self._client.async_write_holding_register(address=address, value=value)
        except ModbusWriteError as err:
            raise UpdateFailed(str(err)) from err
        await self.async_request_refresh()

    async def async_write_holding_registers(self, values: dict[int, int]) -> None:
        """Write multiple holding registers and refresh once."""
        try:
            await self._client.async_write_holding_registers(values=values)
        except ModbusWriteError as err:
            raise UpdateFailed(str(err)) from err
        await self.async_request_refresh()

    async def _async_probe_gateway_tcp(self) -> bool:
        """Check whether Modbus TCP gateway endpoint is reachable."""
        writer = None
        timeout = max(1, int(self._client.timeout))
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(self._client.host, self._client.port),
                timeout=timeout,
            )
        except (TimeoutError, OSError):
            return False
        finally:
            if writer is not None:
                writer.close()
                await writer.wait_closed()
        return True


def _read_blocks_from_profile(profile: dict[str, Any]) -> list[RegisterBlock]:
    """Use profile read blocks if valid, otherwise fallback to defaults."""
    configured = profile.get("read_blocks", [])
    if not isinstance(configured, list):
        return DEFAULT_READ_BLOCKS

    blocks: list[RegisterBlock] = []
    for item in configured:
        if not isinstance(item, dict):
            continue
        register_type = str(item.get("register_type", "")).strip().lower()
        if register_type not in (REGISTER_TYPE_INPUT, REGISTER_TYPE_HOLDING):
            continue
        try:
            start = int(item.get("start"))
            count = int(item.get("count"))
        except (TypeError, ValueError):
            continue
        if start < 0 or count <= 0:
            continue
        blocks.append(RegisterBlock(register_type=register_type, start=start, count=count))

    return blocks or DEFAULT_READ_BLOCKS
