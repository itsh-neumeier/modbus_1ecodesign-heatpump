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

    @property
    def host(self) -> str:
        """Configured Modbus host."""
        return self._host

    @property
    def port(self) -> int:
        """Configured Modbus port."""
        return self._port

    @property
    def timeout(self) -> int:
        """Configured timeout in seconds."""
        return self._timeout

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
                    response = await self._async_read_input_registers(
                        client=client,
                        address=block.start,
                        count=block.count,
                    )
                else:
                    response = await self._async_read_holding_registers(
                        client=client,
                        address=block.start,
                        count=block.count,
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
            response = await self._async_write_register(
                client=client,
                address=address,
                value=value,
            )
            if response.isError():
                raise ModbusWriteError(str(response))

    async def async_write_holding_registers(self, values: dict[int, int]) -> None:
        """Write multiple holding registers in one client session."""
        async with self._lock:
            client = await self._async_get_client()
            for address, value in values.items():
                response = await self._async_write_register(
                    client=client,
                    address=address,
                    value=value,
                )
                if response.isError():
                    raise ModbusWriteError(str(response))

    async def _async_read_input_registers(
        self,
        client: AsyncModbusTcpClient,
        address: int,
        count: int,
    ):
        """Read input registers across pymodbus API variants."""
        try:
            return await client.read_input_registers(
                address=address,
                count=count,
                device_id=self._slave,
            )
        except TypeError:
            return await client.read_input_registers(
                address=address,
                count=count,
                slave=self._slave,
            )

    async def _async_read_holding_registers(
        self,
        client: AsyncModbusTcpClient,
        address: int,
        count: int,
    ):
        """Read holding registers across pymodbus API variants."""
        try:
            return await client.read_holding_registers(
                address=address,
                count=count,
                device_id=self._slave,
            )
        except TypeError:
            return await client.read_holding_registers(
                address=address,
                count=count,
                slave=self._slave,
            )

    async def _async_write_register(
        self,
        client: AsyncModbusTcpClient,
        address: int,
        value: int,
    ):
        """Write a register across pymodbus API variants."""
        try:
            return await client.write_register(
                address=address,
                value=value,
                device_id=self._slave,
            )
        except TypeError:
            return await client.write_register(
                address=address,
                value=value,
                slave=self._slave,
            )

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
