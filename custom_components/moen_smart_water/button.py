"""Button platform for Moen Smart Water integration."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import MoenDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Moen Smart Water button entities."""
    coordinator: MoenDataUpdateCoordinator = hass.data["moen_smart_water"][config_entry.entry_id]

    # Get devices and create entities for each
    devices = coordinator.get_all_devices()
    _LOGGER.info("Setting up button entities. Found %d devices: %s", len(devices), list(devices.keys()))

    entities = []
    for device_id, device in devices.items():
        device_name = device.get("name", f"Moen Smart Water {device_id}")
        _LOGGER.info("Creating button entities for device %s: %s", device_id, device_name)

        entities.extend([
            MoenStartWaterButton(coordinator, device_id, device_name),
            MoenStopWaterButton(coordinator, device_id, device_name),
            MoenColdestButton(coordinator, device_id, device_name),
            MoenWarmButton(coordinator, device_id, device_name),
            MoenHottestButton(coordinator, device_id, device_name),
        ])

    _LOGGER.info("Adding %d button entities", len(entities))
    async_add_entities(entities)


class MoenButtonBase(CoordinatorEntity, ButtonEntity):
    """Base class for Moen button entities."""

    def __init__(
        self,
        coordinator: MoenDataUpdateCoordinator,
        device_id: str,
        device_name: str,
        button_name: str,
        unique_id_suffix: str,
    ) -> None:
        """Initialize the button entity."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_name = device_name
        self._attr_unique_id = f"{device_id}_{unique_id_suffix}"
        self._attr_name = button_name
        self._attr_has_entity_name = True

        # Device information
        self._attr_device_info = DeviceInfo(
            identifiers={("moen_smart_water", device_id)},
            name=device_name,
            manufacturer="Moen",
            model="Smart Faucet",
        )


class MoenStartWaterButton(MoenButtonBase):
    """Button to start water flow."""

    def __init__(
        self,
        coordinator: MoenDataUpdateCoordinator,
        device_id: str,
        device_name: str,
    ) -> None:
        """Initialize the start water button."""
        super().__init__(
            coordinator, device_id, device_name, "Start Water", "start_water"
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.hass.async_add_executor_job(
                self.coordinator.api.start_water_flow,
                self._device_id,
                "coldest",  # Default to coldest temperature
                100  # Default to full flow rate
            )
            _LOGGER.info("Started water flow for device %s", self._device_id)
        except Exception as err:
            _LOGGER.error("Failed to start water flow for device %s: %s", self._device_id, err)


class MoenStopWaterButton(MoenButtonBase):
    """Button to stop water flow."""

    def __init__(
        self,
        coordinator: MoenDataUpdateCoordinator,
        device_id: str,
        device_name: str,
    ) -> None:
        """Initialize the stop water button."""
        super().__init__(
            coordinator, device_id, device_name, "Stop Water", "stop_water"
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.hass.async_add_executor_job(
                self.coordinator.api.stop_water_flow,
                self._device_id
            )
            _LOGGER.info("Stopped water flow for device %s", self._device_id)
        except Exception as err:
            _LOGGER.error("Failed to stop water flow for device %s: %s", self._device_id, err)


class MoenColdestButton(MoenButtonBase):
    """Button to set water to coldest temperature."""

    def __init__(
        self,
        coordinator: MoenDataUpdateCoordinator,
        device_id: str,
        device_name: str,
    ) -> None:
        """Initialize the coldest button."""
        super().__init__(
            coordinator, device_id, device_name, "Coldest", "coldest"
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.hass.async_add_executor_job(
                self.coordinator.api.set_coldest,
                self._device_id,
                100  # Full flow rate
            )
            _LOGGER.info("Set coldest temperature for device %s", self._device_id)
        except Exception as err:
            _LOGGER.error("Failed to set coldest temperature for device %s: %s", self._device_id, err)


class MoenWarmButton(MoenButtonBase):
    """Button to set water to warm temperature."""

    def __init__(
        self,
        coordinator: MoenDataUpdateCoordinator,
        device_id: str,
        device_name: str,
    ) -> None:
        """Initialize the warm button."""
        super().__init__(
            coordinator, device_id, device_name, "Warm", "warm"
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.hass.async_add_executor_job(
                self.coordinator.api.set_warm,
                self._device_id,
                100  # Full flow rate
            )
            _LOGGER.info("Set warm temperature for device %s", self._device_id)
        except Exception as err:
            _LOGGER.error("Failed to set warm temperature for device %s: %s", self._device_id, err)


class MoenHottestButton(MoenButtonBase):
    """Button to set water to hottest temperature."""

    def __init__(
        self,
        coordinator: MoenDataUpdateCoordinator,
        device_id: str,
        device_name: str,
    ) -> None:
        """Initialize the hottest button."""
        super().__init__(
            coordinator, device_id, device_name, "Hottest", "hottest"
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.hass.async_add_executor_job(
                self.coordinator.api.set_hottest,
                self._device_id,
                100  # Full flow rate
            )
            _LOGGER.info("Set hottest temperature for device %s", self._device_id)
        except Exception as err:
            _LOGGER.error("Failed to set hottest temperature for device %s: %s", self._device_id, err)
