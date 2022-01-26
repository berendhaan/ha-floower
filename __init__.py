"""The Floower integration."""
from __future__ import annotations
from datetime import timedelta

from voluptuous.validators import Number
from .FloowerDataCoordinator import (
    FloowerDataUpdateCoordinator,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, MIN_UPDATE_INTERVAL, NAME

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[str] = ["sensor", "light"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Floower from a config entry."""
    api_key = entry.data["apiKey"]

    websession = async_get_clientsession(hass)
    update_interval = timedelta(seconds=MIN_UPDATE_INTERVAL)

    coordinator = FloowerDataUpdateCoordinator(
        hass, websession, api_key, update_interval=update_interval
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # 9k_Dv3T_LS
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
