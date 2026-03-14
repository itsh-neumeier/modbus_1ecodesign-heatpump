"""Low-level Modbus client helpers."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from pymodbus.client import AsyncModbusTcpClient

_LOGGER = logging.getLogger(__name__)

REGISTER_TYPE_INPUT = "input"
REGISTER_TYPE_HOLDING = "holding"


class ModbusConnectionError(Exception):
    """Raised when Modbus connection cannot be established."""


class ModbusReadError(Exception):
    """Raised when Modbus read fails."""


class ModbusWriteError(Exception):
    """Raised when Modbus write fails."""


@dataclass(slots=True, frozen=True)
class RegisterBlock:
    """A contiguous register range."""

    register_type: str
    start: int
    count: int


class Modbus1EcoDesignClient:
    """Async Modbus TCP client with connection reuse."""

    def __init__(self, host: str, port: int, slave: int, timeout: int) -> None:
        self._host = host
        self._port = port
        self._slave = slave
        self._timeout = timeout
        self._client: AsyncModbusTcpClient | None = None
        self._lock = asyncio.Lock()

    async def async_close(self) -> None:
        """Close client connection."""
        async with self._lock:
            if self._client is not None:
                self._client.close()
                self._client = None

    async def async_read_register_blocks(
        self, blocks: list[RegisterBlock]
    ) -> dict[str, dict[int, int]]:
        """Read a list of contiguous register blocks."""
        async with self._lock:
            client = await self._async_get_client()
            snapshot: dict[str, dict[int, int]] = {
                REGISTER_TYPE_INPUT: {},
                REGISTER_TYPE_HOLDING: {},
            }

            for block in blocks:
                if block.register_type == REGISTER_TYPE_INPUT:
                    response = await client.read_input_registers(
                        address=block.start,
                        count=block.count,
                        slave=self._slave,
                    )
                else:
                    response = await client.read_holding_registers(
                        address=block.start,
                        count=block.count,
                        slave=self._slave,
                    )

                if response.isError():
                    raise ModbusReadError(str(response))

                registers = getattr(response, "registers", None)
                if not isinstance(registers, list):
                    raise ModbusReadError("Response did not contain a registers list")

                target = snapshot[block.register_type]
                for idx, value in enumerate(registers):
                    target[block.start + idx] = int(value)

            return snapshot

    async def async_write_holding_register(self, address: int, value: int) -> None:
        """Write one holding register."""
        async with self._lock:
            client = await self._async_get_client()
            response = await client.write_register(
                address=address,
                value=value,
                slave=self._slave,
            )
            if response.isError():
                raise ModbusWriteError(str(response))

    async def _async_get_client(self) -> AsyncModbusTcpClient:
        """Return a connected AsyncModbusTcpClient."""
        if self._client is None:
            self._client = AsyncModbusTcpClient(
                host=self._host,
                port=self._port,
                timeout=self._timeout,
            )

        if not self._client.connected:
            connected = await self._client.connect()
            if not connected:
                raise ModbusConnectionError(
                    f"Could not connect to {self._host}:{self._port} (slave={self._slave})"
                )
            _LOGGER.debug("Connected to Modbus endpoint %s:%s", self._host, self._port)

        return self._client


async def async_validate_connection(host: str, port: int, slave: int, timeout: int) -> None:
    """Validate endpoint by reading one known register."""
    client = Modbus1EcoDesignClient(host=host, port=port, slave=slave, timeout=timeout)
    try:
        snapshot = await client.async_read_register_blocks(
            [RegisterBlock(register_type=REGISTER_TYPE_INPUT, start=7, count=1)]
        )
        if 7 not in snapshot[REGISTER_TYPE_INPUT]:
            raise ModbusReadError("Validation register was not returned by endpoint")
    finally:
        await client.async_close()

