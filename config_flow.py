"""Config flow for Floower integration."""
from __future__ import annotations

import logging
from http import HTTPStatus
from typing import Any
from aiohttp.client import ClientSession

import voluptuous as vol
import requests
import aiohttp
import asyncio


from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, FLOOWER_ENDPOINT

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("apiKey"): str,
        vol.Required("name"): str,
    }
)

class FloowerHub:
    def __init__(self, hass: HomeAssistant, session: ClientSession) -> None:
        self.hass = hass
        self.session = session

    async def authenticate(self, apiKey: str) -> bool:
        url = f"{FLOOWER_ENDPOINT}?apiKey={apiKey}"
        resp = await self.session.get(url)
        return resp.status == HTTPStatus.OK


async def validate_input(
    hass: HomeAssistant, session: ClientSession, data: dict[str, Any]
) -> dict[str, Any]:

    hub = FloowerHub(hass, session)

    if not await hub.authenticate(data["apiKey"]):
        raise InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": data["name"], "apiKey": data["apiKey"]}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Floower."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        websession = async_get_clientsession(self.hass)
        errors = {}

        try:
            info = await validate_input(self.hass, websession, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            await self.async_set_unique_id(info["apiKey"])
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
