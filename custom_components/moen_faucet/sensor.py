"""Sensor platform for Moen Faucet integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
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
    """Set up Moen Faucet sensor entities."""
    coordinator: MoenDataUpdateCoordinator = hass.data["moen_faucet"][config_entry.entry_id]

    # Get devices and create entities for each
    devices = coordinator.get_all_devices()
    _LOGGER.info("Setting up sensor entities. Found %d devices: %s", len(devices), list(devices.keys()))

    entities = []
    for device_id, device in devices.items():
        device_name = device.get("name", f"Moen Faucet {device_id}")
        _LOGGER.info("Creating sensor entities for device %s: %s", device_id, device_name)

        entities.extend([
            MoenFaucetStateSensor(coordinator, device_id, device_name),
            MoenLastDispenseVolumeSensor(coordinator, device_id, device_name),
            MoenCloudConnectedSensor(coordinator, device_id, device_name),
            MoenTemperatureSensor(coordinator, device_id, device_name),
            MoenFlowRateSensor(coordinator, device_id, device_name),
            # Debug sensors
            MoenDeviceShadowSensor(coordinator, device_id, device_name),
            MoenApiStatusSensor(coordinator, device_id, device_name),
            MoenLastUpdateSensor(coordinator, device_id, device_name),
        ])

    _LOGGER.info("Adding %d sensor entities", len(entities))
    async_add_entities(entities)


class MoenSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for Moen sensor entities."""

    def __init__(self, coordinator: MoenDataUpdateCoordinator, device_id: str, device_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_name = device_name
        self._attr_has_entity_name = True

        # Device information
        self._attr_device_info = DeviceInfo(
            identifiers={("moen_faucet", self._device_id)},
            name=self._device_name,
            manufacturer="Moen",
            model="Smart Faucet",
        )


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
        self._attr_native_value = 20.0

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        shadow = self.coordinator.get_device_shadow(self._device_id)
        if shadow:
            # Extract temperature from shadow data
            state = shadow.get("state", {}).get("reported", {})
            self._attr_native_value = state.get("temperature", 20.0)
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


class MoenDeviceShadowSensor(MoenSensorBase):
    """Debug sensor for device shadow data."""

    def __init__(self, coordinator: MoenDataUpdateCoordinator, device_id: str, device_name: str) -> None:
        """Initialize the device shadow sensor."""
        super().__init__(coordinator, device_id, device_name)
        self._attr_unique_id = f"{device_id}_device_shadow"
        self._attr_name = "Device Shadow"
        self._attr_native_value = "unknown"

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        shadow = self.coordinator.get_device_shadow(self._device_id)
        if shadow:
            # Show a summary of the shadow data
            state = shadow.get("state", {}).get("reported", {})
            command = state.get("command", "unknown")
            temperature = state.get("temperature", 0)
            flow_rate = state.get("flowRate", 0)
            self._attr_native_value = f"cmd:{command} temp:{temperature} flow:{flow_rate}"
        else:
            self._attr_native_value = "no_data"
        self.async_write_ha_state()


class MoenApiStatusSensor(MoenSensorBase):
    """Debug sensor for API status."""

    def __init__(self, coordinator: MoenDataUpdateCoordinator, device_id: str, device_name: str) -> None:
        """Initialize the API status sensor."""
        super().__init__(coordinator, device_id, device_name)
        self._attr_unique_id = f"{device_id}_api_status"
        self._attr_name = "API Status"
        self._attr_native_value = "unknown"

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        # Check if coordinator has data
        if self.coordinator.data:
            devices = self.coordinator.data.get("devices", {})
            device_shadows = self.coordinator.data.get("device_shadows", {})
            
            if self._device_id in devices and self._device_id in device_shadows:
                self._attr_native_value = "connected"
            elif self._device_id in devices:
                self._attr_native_value = "device_found_no_shadow"
            else:
                self._attr_native_value = "device_not_found"
        else:
            self._attr_native_value = "no_data"
        self.async_write_ha_state()


class MoenLastUpdateSensor(MoenSensorBase):
    """Debug sensor for last update time."""

    def __init__(self, coordinator: MoenDataUpdateCoordinator, device_id: str, device_name: str) -> None:
        """Initialize the last update sensor."""
        super().__init__(coordinator, device_id, device_name)
        self._attr_unique_id = f"{device_id}_last_update"
        self._attr_name = "Last Update"
        self._attr_native_value = "never"

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.last_update_success:
            self._attr_native_value = self.coordinator.last_update_time.isoformat()
        else:
            self._attr_native_value = "failed"
        self.async_write_ha_state()
