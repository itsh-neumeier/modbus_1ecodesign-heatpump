"""Constants for the Modbus 1EcoDesign Heatpump integration."""

from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "modbus_1ecodesign_heatpump"
DEFAULT_NAME = "1EcoDesign Heatpump"
MANUFACTURER = "1EcoDesign"
MODEL = "ED300KWL / VC200"

CONF_SLAVE = "slave"

DEFAULT_PORT = 502
DEFAULT_SLAVE = 3
DEFAULT_SCAN_INTERVAL = 15
MIN_SCAN_INTERVAL = 5
DEFAULT_TIMEOUT = 3

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SWITCH,
]

