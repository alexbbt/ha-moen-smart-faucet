"""Button platform for Moen Faucet integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import MoenDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Moen Faucet button entities."""
    coordinator: MoenDataUpdateCoordinator = hass.data["moen_faucet"][config_entry.entry_id]

    # Get devices and create entities for each
    devices = coordinator.get_all_devices()

    entities = []
    for device_id, device in devices.items():
        device_name = device.get("name", f"Moen Faucet {device_id}")

        entities.extend([
            MoenStartDispenseButton(coordinator, device_id, device_name),
            MoenStopDispenseButton(coordinator, device_id, device_name),
            MoenColdestButton(coordinator, device_id, device_name),
            MoenHottestButton(coordinator, device_id, device_name),
            MoenWarmButton(coordinator, device_id, device_name),
        ])

    async_add_entities(entities)


class MoenButtonBase(ButtonEntity):
    """Base class for Moen button entities."""

    def __init__(self, coordinator: MoenDataUpdateCoordinator, device_id: str, device_name: str) -> None:
        """Initialize the button."""
        self._coordinator = coordinator
        self._device_id = device_id
        self._device_name = device_name
        self._attr_has_entity_name = True

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {("moen_faucet", self._device_id)},
            "name": self._device_name,
            "manufacturer": "Moen",
            "model": "Smart Faucet",
        }


class MoenStartDispenseButton(MoenButtonBase):
    """Button to start dispensing water."""

    def __init__(self, coordinator: MoenDataUpdateCoordinator, device_id: str, device_name: str) -> None:
        """Initialize the start dispense button."""
        super().__init__(coordinator, device_id, device_name)
        self._attr_unique_id = f"{device_id}_start_dispense"
        self._attr_name = "Start Dispense"

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.hass.async_add_executor_job(
                self._coordinator.api.start_water_flow, self._device_id
            )
            _LOGGER.info("Started dispensing on device %s", self._device_id)
        except Exception as err:
            _LOGGER.error("Failed to start dispensing on device %s: %s", self._device_id, err)


class MoenStopDispenseButton(MoenButtonBase):
    """Button to stop dispensing water."""

    def __init__(self, coordinator: MoenDataUpdateCoordinator, device_id: str, device_name: str) -> None:
        """Initialize the stop dispense button."""
        super().__init__(coordinator, device_id, device_name)
        self._attr_unique_id = f"{device_id}_stop_dispense"
        self._attr_name = "Stop Dispense"

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.hass.async_add_executor_job(
                self._coordinator.api.stop_water_flow, self._device_id
            )
            _LOGGER.info("Stopped dispensing on device %s", self._device_id)
        except Exception as err:
            _LOGGER.error("Failed to stop dispensing on device %s: %s", self._device_id, err)


class MoenColdestButton(MoenButtonBase):
    """Button to set water to coldest temperature."""

    def __init__(self, coordinator: MoenDataUpdateCoordinator, device_id: str, device_name: str) -> None:
        """Initialize the coldest button."""
        super().__init__(coordinator, device_id, device_name)
        self._attr_unique_id = f"{device_id}_coldest"
        self._attr_name = "Coldest"

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.hass.async_add_executor_job(
                self._coordinator.api.set_coldest, self._device_id
            )
            _LOGGER.info("Set coldest temperature on device %s", self._device_id)
        except Exception as err:
            _LOGGER.error("Failed to set coldest temperature on device %s: %s", self._device_id, err)


class MoenHottestButton(MoenButtonBase):
    """Button to set water to hottest temperature."""

    def __init__(self, coordinator: MoenDataUpdateCoordinator, device_id: str, device_name: str) -> None:
        """Initialize the hottest button."""
        super().__init__(coordinator, device_id, device_name)
        self._attr_unique_id = f"{device_id}_hottest"
        self._attr_name = "Hottest"

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.hass.async_add_executor_job(
                self._coordinator.api.set_hottest, self._device_id
            )
            _LOGGER.info("Set hottest temperature on device %s", self._device_id)
        except Exception as err:
            _LOGGER.error("Failed to set hottest temperature on device %s: %s", self._device_id, err)


class MoenWarmButton(MoenButtonBase):
    """Button to set water to warm temperature."""

    def __init__(self, coordinator: MoenDataUpdateCoordinator, device_id: str, device_name: str) -> None:
        """Initialize the warm button."""
        super().__init__(coordinator, device_id, device_name)
        self._attr_unique_id = f"{device_id}_warm"
        self._attr_name = "Warm"

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.hass.async_add_executor_job(
                self._coordinator.api.set_warm, self._device_id
            )
            _LOGGER.info("Set warm temperature on device %s", self._device_id)
        except Exception as err:
            _LOGGER.error("Failed to set warm temperature on device %s: %s", self._device_id, err)
