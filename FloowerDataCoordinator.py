from __future__ import annotations

from datetime import timedelta
import logging
from aiohttp.client import ClientSession


import async_timeout
import homeassistant
from .FloowerApi import FloowerApi

from homeassistant.components.light import LightEntity
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    COLOR_B,
    COLOR_G,
    COLOR_R,
    DOMAIN,
    ID,
    NAME,
    FIRMWAREVERSION,
    BATTERYLEVEL,
    PETALSLEVEL,
)

_LOGGER = logging.getLogger(__name__)


class FloowerDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(
        self,
        hass: homeassistant,
        session: ClientSession,
        api_key: str,
        update_interval: timedelta,
    ) -> None:
        self.floower_api = FloowerApi(api_key, session)
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)

    @property
    def api(self) -> FloowerApi:
        return self.floower_api

    async def _async_update_data(self) -> dict[str, str | float | int]:
        """Update data via library."""
        data: dict[str, str | float | int] = {}
        resp = await self.floower_api.poll_data()

        data[ID] = resp["id"]
        data[NAME] = resp["name"]
        data[FIRMWAREVERSION] = resp["firmwareVersion"]
        data[BATTERYLEVEL] = resp["status"]["batteryLevel"]
        data[PETALSLEVEL] = resp["state"]["petalsLevel"]
        data[COLOR_R] = resp["state"]["red"]
        data[COLOR_G] = resp["state"]["green"]
        data[COLOR_B] = resp["state"]["blue"]
        return data
