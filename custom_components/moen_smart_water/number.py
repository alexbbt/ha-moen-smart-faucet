"""Number platform for Moen Smart Water integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
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
    """Set up Moen Smart Water number entities."""
    coordinator: MoenDataUpdateCoordinator = hass.data["moen_smart_water"][config_entry.entry_id]

    # Get devices and create entities for each
    devices = coordinator.get_all_devices()
    _LOGGER.info("Setting up number entities. Found %d devices: %s", len(devices), list(devices.keys()))

    entities = []
    for device_id, device in devices.items():
        device_name = device.get("name", f"Moen Smart Water {device_id}")
        _LOGGER.info("Creating number entities for device %s: %s", device_id, device_name)

        entities.extend([
            MoenTemperatureNumber(coordinator, device_id, device_name),
            MoenFlowRateNumber(coordinator, device_id, device_name),
        ])

    _LOGGER.info("Adding %d number entities", len(entities))
    async_add_entities(entities)


class MoenNumberBase(CoordinatorEntity, NumberEntity):
    """Base class for Moen number entities."""

    def __init__(
        self,
        coordinator: MoenDataUpdateCoordinator,
        device_id: str,
        device_name: str,
        number_name: str,
        unique_id_suffix: str,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_name = device_name
        self._attr_unique_id = f"{device_id}_{unique_id_suffix}"
        self._attr_name = number_name
        self._attr_has_entity_name = True
        self._attr_mode = NumberMode.AUTO

        # Device information
        self._attr_device_info = DeviceInfo(
            identifiers={("moen_smart_water", device_id)},
            name=device_name,
            manufacturer="Moen",
            model="Smart Faucet",
        )

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        shadow = self.coordinator.get_device_shadow(self._device_id)
        if shadow:
            state = shadow.get("state", {}).get("reported", {})
            self._update_from_state(state)
        self.async_write_ha_state()

    def _update_from_state(self, state: dict[str, Any]) -> None:
        """Update entity state from device shadow data."""
        # Override in subclasses
        pass


class MoenTemperatureNumber(MoenNumberBase):
    """Number entity for water temperature."""

    def __init__(
        self,
        coordinator: MoenDataUpdateCoordinator,
        device_id: str,
        device_name: str,
    ) -> None:
        """Initialize the temperature number entity."""
        super().__init__(
            coordinator, device_id, device_name, "Temperature", "temperature"
        )
        self._attr_native_min_value = 0.0
        self._attr_native_max_value = 100.0
        self._attr_native_step = 1.0
        self._attr_native_unit_of_measurement = "°C"
        self._attr_native_value = 20.0

    def _update_from_state(self, state: dict[str, Any]) -> None:
        """Update temperature from device state."""
        self._attr_native_value = state.get("temperature", 20.0)

    async def async_set_native_value(self, value: float) -> None:
        """Set the temperature value."""
        try:
            await self.hass.async_add_executor_job(
                self.coordinator.api.set_specific_temperature,
                self._device_id,
                value
            )
            self._attr_native_value = value
            _LOGGER.info("Set temperature to %.1f°C for device %s", value, self._device_id)
        except Exception as err:
            _LOGGER.error("Failed to set temperature for device %s: %s", self._device_id, err)


class MoenFlowRateNumber(MoenNumberBase):
    """Number entity for flow rate."""

    def __init__(
        self,
        coordinator: MoenDataUpdateCoordinator,
        device_id: str,
        device_name: str,
    ) -> None:
        """Initialize the flow rate number entity."""
        super().__init__(
            coordinator, device_id, device_name, "Flow Rate", "flow_rate"
        )
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = "%"
        self._attr_native_value = 0

    def _update_from_state(self, state: dict[str, Any]) -> None:
        """Update flow rate from device state."""
        self._attr_native_value = state.get("flowRate", 0)

    async def async_set_native_value(self, value: float) -> None:
        """Set the flow rate value."""
        try:
            await self.hass.async_add_executor_job(
                self.coordinator.api.set_flow_rate,
                self._device_id,
                int(value)
            )
            self._attr_native_value = int(value)
            _LOGGER.info("Set flow rate to %d%% for device %s", int(value), self._device_id)
        except Exception as err:
            _LOGGER.error("Failed to set flow rate for device %s: %s", self._device_id, err)
