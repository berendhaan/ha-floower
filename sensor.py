from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any, cast
from . import (
    FloowerDataUpdateCoordinator,
)

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo

from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ID, NAME, FIRMWAREVERSION, BATTERYLEVEL, PETALSLEVEL

_LOGGER = logging.getLogger(__name__)


@dataclass
class FloowersSensorEntityDescription(SensorEntityDescription):
    """Class describing Airly sensor entities."""

    value: Callable = round


SENSOR_TYPES: tuple[FloowersSensorEntityDescription, ...] = (
    FloowersSensorEntityDescription(
        key=BATTERYLEVEL,
        device_class=SensorDeviceClass.BATTERY,
        name=BATTERYLEVEL,
        native_unit_of_measurement="%",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:

    coordinator = hass.data[DOMAIN][entry.entry_id]

        # floower_id = 
        # self.firmware_version = 
        # self._attr_name = f"{name} {description.name}"
        # self._attr_unique_id = f"{description.key}{floower_id}".lower()
        # self.entity_description = description

    device_info = DeviceInfo(
        identifiers={(DOMAIN, coordinator.data["id"])},
        manufacturer="Floower",
        name="Floower lampje",
        sw_version=coordinator.data[FIRMWAREVERSION],
    )

    sensors = []
    for description in SENSOR_TYPES:
        # When we use the nearest method, we are not sure which sensors are available
        _LOGGER.info("Getting key" + description.key)
        if coordinator.data.get(description.key) != None:
            _LOGGER.info("Adding " + description.key)
            sensors.append(FloowerSensor(coordinator, device_info, description))

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(sensors)


class FloowerSensor(CoordinatorEntity, SensorEntity):
    """Define an Airly sensor."""

    coordinator: FloowerDataUpdateCoordinator
    entity_description: FloowersSensorEntityDescription

    def __init__(
        self,
        coordinator: FloowerDataUpdateCoordinator,
        device_info: DeviceInfo,
        description: FloowersSensorEntityDescription
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_device_info = device_info
        self.entity_description = description

    @property
    def device_info(self) -> DeviceInfo | None:
        return self.device_info

    @property
    def native_value(self) -> StateType:
        """Return the state."""
        state = self.coordinator.data[self.entity_description.key]
        return cast(StateType, self.entity_description.value(state))
