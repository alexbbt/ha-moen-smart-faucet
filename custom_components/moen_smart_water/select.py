"""Select platform for Moen Smart Water integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
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
    """Set up Moen Smart Water select entities."""
    coordinator: MoenDataUpdateCoordinator = hass.data["moen_smart_water"][config_entry.entry_id]

    # Get devices and create entities for each
    devices = coordinator.get_all_devices()

    entities = []
    for device_id, device in devices.items():
        device_name = device.get("name", f"Moen Smart Water {device_id}")
        entities.append(MoenTemperatureSelect(coordinator, device_id, device_name))

    async_add_entities(entities)


class MoenTemperatureSelect(CoordinatorEntity, SelectEntity):
    """Select entity for Moen Smart Water temperature presets."""

    def __init__(
        self,
        coordinator: MoenDataUpdateCoordinator,
        device_id: str,
        device_name: str
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_name = device_name
        self._attr_unique_id = f"{device_id}_temperature_preset"
        self._attr_name = "Temperature Preset"
        self._attr_has_entity_name = True

        # Device information
        self._attr_device_info = DeviceInfo(
            identifiers={("moen_smart_water", device_id)},
            name=device_name,
            manufacturer="Moen",
            model="Smart Faucet",
        )

        # Available options
        self._attr_options = [
            "coldest",
            "cold",
            "warm",
            "hot",
            "hottest",
            "custom"
        ]
        self._attr_current_option = "coldest"

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {("moen_smart_water", self._device_id)},
            "name": self._device_name,
            "manufacturer": "Moen",
            "model": "Smart Faucet",
        }

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        shadow = self.coordinator.get_device_shadow(self._device_id)
        if shadow:
            state = shadow.get("state", {}).get("reported", {})

            # Determine current temperature preset based on temperature value
            temperature = state.get("temperature", 20.0)
            if temperature <= 10:
                self._attr_current_option = "coldest"
            elif temperature <= 25:
                self._attr_current_option = "cold"
            elif temperature <= 40:
                self._attr_current_option = "warm"
            elif temperature <= 60:
                self._attr_current_option = "hot"
            elif temperature > 60:
                self._attr_current_option = "hottest"
            else:
                self._attr_current_option = "custom"

        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        try:
            # Map options to API calls
            if option == "coldest":
                await self.hass.async_add_executor_job(
                    self.coordinator.api.set_coldest,
                    self._device_id
                )
            elif option == "hottest":
                await self.hass.async_add_executor_job(
                    self.coordinator.api.set_hottest,
                    self._device_id
                )
            elif option == "warm":
                await self.hass.async_add_executor_job(
                    self.coordinator.api.set_warm,
                    self._device_id
                )
            elif option == "cold":
                # Set to a cold temperature (15°C)
                await self.hass.async_add_executor_job(
                    self.coordinator.api.set_specific_temperature,
                    self._device_id,
                    15.0
                )
            elif option == "hot":
                # Set to a hot temperature (50°C)
                await self.hass.async_add_executor_job(
                    self.coordinator.api.set_specific_temperature,
                    self._device_id,
                    50.0
                )
            elif option == "custom":
                # For custom, we'll let the user set specific temperature via number entity
                _LOGGER.info("Custom temperature selected - use temperature number entity to set specific value")

            self._attr_current_option = option
            _LOGGER.info("Set temperature preset to %s for device %s", option, self._device_id)
        except Exception as err:
            _LOGGER.error("Failed to set temperature preset for device %s: %s", self._device_id, err)
