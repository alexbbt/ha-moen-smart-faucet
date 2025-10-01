"""Sensor platform for Moen Faucet integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import MoenDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Moen Faucet sensor entities."""
    coordinator: MoenDataUpdateCoordinator = hass.data["moen_faucet"][config_entry.entry_id]

    # Get devices and create entities for each
    devices = coordinator.get_all_devices()

    entities = []
    for device_id, device in devices.items():
        device_name = device.get("name", f"Moen Faucet {device_id}")

        entities.extend([
            MoenFaucetStateSensor(coordinator, device_id, device_name),
            MoenLastDispenseVolumeSensor(coordinator, device_id, device_name),
            MoenCloudConnectedSensor(coordinator, device_id, device_name),
            MoenTemperatureSensor(coordinator, device_id, device_name),
            MoenFlowRateSensor(coordinator, device_id, device_name),
        ])

    async_add_entities(entities)


class MoenSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for Moen sensor entities."""

    def __init__(self, coordinator: MoenDataUpdateCoordinator, device_id: str, device_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
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


class MoenFaucetStateSensor(MoenSensorBase):
    """Sensor for faucet state."""

    def __init__(self, coordinator: MoenDataUpdateCoordinator, device_id: str, device_name: str) -> None:
        """Initialize the faucet state sensor."""
        super().__init__(coordinator, device_id, device_name)
        self._attr_unique_id = f"{device_id}_faucet_state"
        self._attr_name = "Faucet State"
        self._attr_native_value = "unknown"

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        shadow = self.coordinator.get_device_shadow(self._device_id)
        if shadow:
            # Extract state from shadow data
            state = shadow.get("state", {}).get("reported", {})
            if state.get("command") == "run":
                self._attr_native_value = "running"
            elif state.get("command") == "stop":
                self._attr_native_value = "stopped"
            else:
                self._attr_native_value = "idle"
        else:
            self._attr_native_value = "unknown"
        self.async_write_ha_state()


class MoenLastDispenseVolumeSensor(MoenSensorBase):
    """Sensor for last dispense volume."""

    def __init__(self, coordinator: MoenDataUpdateCoordinator, device_id: str, device_name: str) -> None:
        """Initialize the last dispense volume sensor."""
        super().__init__(coordinator, device_id, device_name)
        self._attr_unique_id = f"{device_id}_last_dispense_volume"
        self._attr_name = "Last Dispense Volume"
        self._attr_native_unit_of_measurement = "ml"
        self._attr_native_value = 0

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        shadow = self.coordinator.get_device_shadow(self._device_id)
        if shadow:
            # Extract last dispense volume from shadow data
            state = shadow.get("state", {}).get("reported", {})
            self._attr_native_value = state.get("lastDispenseVolume", 0)
        self.async_write_ha_state()


class MoenCloudConnectedSensor(MoenSensorBase):
    """Sensor for cloud connection status."""

    def __init__(self, coordinator: MoenDataUpdateCoordinator, device_id: str, device_name: str) -> None:
        """Initialize the cloud connected sensor."""
        super().__init__(coordinator, device_id, device_name)
        self._attr_unique_id = f"{device_id}_cloud_connected"
        self._attr_name = "Cloud Connected"
        self._attr_native_value = "unknown"

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        shadow = self.coordinator.get_device_shadow(self._device_id)
        if shadow:
            self._attr_native_value = "connected"
        else:
            self._attr_native_value = "disconnected"
        self.async_write_ha_state()


class MoenTemperatureSensor(MoenSensorBase):
    """Sensor for current water temperature."""

    def __init__(self, coordinator: MoenDataUpdateCoordinator, device_id: str, device_name: str) -> None:
        """Initialize the temperature sensor."""
        super().__init__(coordinator, device_id, device_name)
        self._attr_unique_id = f"{device_id}_temperature"
        self._attr_name = "Temperature"
        self._attr_native_unit_of_measurement = "°C"
        self._attr_native_value = 0

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        shadow = self.coordinator.get_device_shadow(self._device_id)
        if shadow:
            # Extract temperature from shadow data
            state = shadow.get("state", {}).get("reported", {})
            self._attr_native_value = state.get("temperature", 0)
        self.async_write_ha_state()


class MoenFlowRateSensor(MoenSensorBase):
    """Sensor for current flow rate."""

    def __init__(self, coordinator: MoenDataUpdateCoordinator, device_id: str, device_name: str) -> None:
        """Initialize the flow rate sensor."""
        super().__init__(coordinator, device_id, device_name)
        self._attr_unique_id = f"{device_id}_flow_rate"
        self._attr_name = "Flow Rate"
        self._attr_native_unit_of_measurement = "%"
        self._attr_native_value = 0

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        shadow = self.coordinator.get_device_shadow(self._device_id)
        if shadow:
            # Extract flow rate from shadow data
            state = shadow.get("state", {}).get("reported", {})
            self._attr_native_value = state.get("flowRate", 0)
        self.async_write_ha_state()
