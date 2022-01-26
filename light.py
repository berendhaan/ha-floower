"""Platform for light integration."""
from __future__ import annotations

import logging

from . import (
    FloowerDataUpdateCoordinator,
)

import voluptuous as vol
from . import FloowerApi, FloowerDataCoordinator
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    COLOR_MODE_RGB,
    PLATFORM_SCHEMA,
    LightEntity,
)
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from .const import COLOR_B, COLOR_G, COLOR_R, DOMAIN, FIRMWAREVERSION

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_USERNAME, default="admin"): cv.string,
        vol.Optional(CONF_PASSWORD): cv.string,
    }
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:

    coordinator = hass.data[DOMAIN][entry.entry_id]
    device = DeviceInfo(
        identifiers={(DOMAIN, coordinator.data["id"])},
        manufacturer="Floower",
        name="Floower lampje",
        sw_version=coordinator.data[FIRMWAREVERSION],
    )
    async_add_entities([FloowerLamp(coordinator, entry, device)])


class FloowerLamp(LightEntity):
    def __init__(self, coordinator: FloowerDataUpdateCoordinator, entry: ConfigEntry, device: DeviceInfo) -> None:
        # super().__init__(device, entry)
        """Initialize an AwesomeLight."""
        floower_id = coordinator.data["id"]
        self.firmware_version = coordinator.data[FIRMWAREVERSION]
        #self._attr_name = f"{name} {description.name}"
        self._attr_unique_id = f"{floower_id}".lower()
        # self.entity_description = description
        # self.device_info = device
        self.coordinator = coordinator
        self._name = "Foower"
        self._state = None
        self._brightness = None
        

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(self.unique_id)},
            manufacturer="Floower",
            name="Floower lampje",
            sw_version=self.firmware_version,
        )

    @property
    def supported_color_modes(self) -> set[str] | None:
        return {COLOR_MODE_RGB}

    @property
    def color_mode(self):
        return COLOR_MODE_RGB

    @property
    def rgb_color(self) -> tuple:
        """Return the color property."""
        blue = self.coordinator.data[COLOR_B]
        green = self.coordinator.data[COLOR_G]
        red = self.coordinator.data[COLOR_R]

        return (red, green, blue)

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Return the brightness of the light.
        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state

    async def async_turn_off(self) -> None:
        off = await self.coordinator.api.turn_off()
        self._state = False

    async def async_turn_on(self, **kwargs) -> None:
        _LOGGER.info(kwargs)
        if ATTR_RGB_COLOR in kwargs:
            self.attr_rgb = kwargs[ATTR_RGB_COLOR]
        else:
            self.attr_rgb = (255, 255, 255)
            
        on = await self.coordinator.api.turn_on(self.attr_rgb[0], self.attr_rgb[1], self.attr_rgb[2])
        self._state = True

    async def async_update_ha_state(self, force_refresh: bool = False) -> None:
        return await super().async_update_ha_state(force_refresh=force_refresh)

    def update(self) -> None:
        """Fetch new state data for this light.
        This is the only method that should fetch new data for Home Assistant.
        """
        # self._light.update()
        # self._state = self._light.is_on()
        # self._brightness = self._light.brightness
