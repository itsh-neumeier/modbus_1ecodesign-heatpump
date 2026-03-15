"""Modbus 1EcoDesign Heatpump integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_TIMEOUT
from homeassistant.core import HomeAssistant

from .const import (
    CONF_DEVICE_PROFILE,
    CONF_SLAVE,
    DEFAULT_DEVICE_PROFILE,
    DEFAULT_TIMEOUT,
    DOMAIN,
    PLATFORMS,
)
from .device_profile import get_device_profile

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Modbus 1EcoDesign Heatpump from config entry."""
    # Import lazily so config flow can still load even if requirements are not ready yet.
    from .coordinator import Modbus1EcoDesignUpdateCoordinator
    from .modbus import Modbus1EcoDesignClient

    client = Modbus1EcoDesignClient(
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        slave=entry.data[CONF_SLAVE],
        timeout=entry.options.get(CONF_TIMEOUT, entry.data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)),
    )

    coordinator = Modbus1EcoDesignUpdateCoordinator(
        hass=hass,
        entry=entry,
        client=client,
        profile=get_device_profile(
            str(
                entry.options.get(
                    CONF_DEVICE_PROFILE,
                    entry.data.get(CONF_DEVICE_PROFILE, DEFAULT_DEVICE_PROFILE),
                )
            )
        ),
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "client": client,
        "coordinator": coordinator,
        "profile": coordinator.profile,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if not unloaded:
        return False

    entry_data = hass.data[DOMAIN].pop(entry.entry_id)
    await entry_data["client"].async_close()
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old config entry versions."""
    if config_entry.version > 3:
        _LOGGER.error(
            "Cannot migrate entry %s from future version %s",
            config_entry.entry_id,
            config_entry.version,
        )
        return False

    if config_entry.version < 3:
        data = dict(config_entry.data)
        options = dict(config_entry.options)
        profile = str(data.get(CONF_DEVICE_PROFILE, DEFAULT_DEVICE_PROFILE))
        data.setdefault(CONF_DEVICE_PROFILE, profile)
        options.setdefault(CONF_DEVICE_PROFILE, profile)
        hass.config_entries.async_update_entry(
            config_entry,
            data=data,
            options=options,
            version=3,
        )
        _LOGGER.info("Migrated %s to version 3", config_entry.entry_id)

    return True
