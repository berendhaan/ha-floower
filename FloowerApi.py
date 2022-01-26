import math
import logging
import json

from aiohttp.client import ClientSession
from aiohttp.client_reqrep import ClientResponse

from .const import FLOOWER_ENDPOINT

_LOGGER = logging.getLogger(__name__)


class FloowerApi:
    def __init__(self, api_key: str, session: ClientSession) -> None:
        self.api_key = api_key
        self.session = session
        self.api_uri = f"{FLOOWER_ENDPOINT}?apiKey={self.api_key}"

    async def poll_data(self) -> any:
        resp = await self.session.get(self.api_uri)
        return await resp.json()

    async def turn_off(self) -> bool:
        response = await self.__async_update_state(0, 0, 0, 0)
        return response.status == 204

    async def turn_on(self, r, g, b) -> bool:
        resp = await self.__async_update_state(55, r, g, b)
        return resp.status == 204

    async def __async_update_state(
        self, petals_level: int, r: int, g: int, b: int
    ) -> ClientResponse:
        message = {
            "petalsLevel": clamp(petals_level, 0, 100),
            "red": clamp(r, 0, 255),
            "green": clamp(g, 0, 255),
            "blue": clamp(b, 0, 255),
            "apiKey": self.api_key,
        }

        json_body = json.dumps(message)

        _LOGGER.debug(json_body)
        return await self.session.put(
            FLOOWER_ENDPOINT,
            data=json_body,
            headers={"content-type": "application/json"},
        )


def clamp(num, min_value, max_value):
    return max(min(num, max_value), min_value)
