"""Sensor platform for Moen Faucet integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import MoenClient

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Moen Faucet sensor entities."""
    client: MoenClient = hass.data["moen_faucet"][config_entry.entry_id]

    # Get devices and create entities for each
    devices = await hass.async_add_executor_job(client.get_devices)

    entities = []
    for device in devices:
        device_id = device.get("id", device.get("device_id"))
        device_name = device.get("name", f"Moen Faucet {device_id}")

        entities.extend([
            MoenFaucetStateSensor(client, device_id, device_name),
            MoenLastDispenseVolumeSensor(client, device_id, device_name),
            MoenCloudConnectedSensor(client, device_id, device_name),
        ])

    async_add_entities(entities)


class MoenSensorBase(SensorEntity):
    """Base class for Moen sensor entities."""

    def __init__(self, client: MoenClient, device_id: str, device_name: str) -> None:
        """Initialize the sensor."""
        self._client = client
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

    def __init__(self, client: MoenClient, device_id: str, device_name: str) -> None:
        """Initialize the faucet state sensor."""
        super().__init__(client, device_id, device_name)
        self._attr_unique_id = f"{device_id}_faucet_state"
        self._attr_name = "Faucet State"
        self._attr_native_value = "unknown"

    async def async_update(self) -> None:
        """Update the sensor state."""
        try:
            status = await self.hass.async_add_executor_job(
                self._client.get_device_status, self._device_id
            )
            # Extract state from status - this will need to be updated based on actual API response
            self._attr_native_value = status.get("state", "unknown")
        except Exception as err:
            _LOGGER.error("Failed to update faucet state for device %s: %s", self._device_id, err)
            self._attr_native_value = "error"


class MoenLastDispenseVolumeSensor(MoenSensorBase):
    """Sensor for last dispense volume."""

    def __init__(self, client: MoenClient, device_id: str, device_name: str) -> None:
        """Initialize the last dispense volume sensor."""
        super().__init__(client, device_id, device_name)
        self._attr_unique_id = f"{device_id}_last_dispense_volume"
        self._attr_name = "Last Dispense Volume"
        self._attr_native_unit_of_measurement = "ml"
        self._attr_native_value = 0

    async def async_update(self) -> None:
        """Update the sensor state."""
        try:
            status = await self.hass.async_add_executor_job(
                self._client.get_device_status, self._device_id
            )
            # Extract last dispense volume from status - this will need to be updated based on actual API response
            self._attr_native_value = status.get("last_dispense_volume", 0)
        except Exception as err:
            _LOGGER.error("Failed to update last dispense volume for device %s: %s", self._device_id, err)


class MoenCloudConnectedSensor(MoenSensorBase):
    """Sensor for cloud connection status."""

    def __init__(self, client: MoenClient, device_id: str, device_name: str) -> None:
        """Initialize the cloud connected sensor."""
        super().__init__(client, device_id, device_name)
        self._attr_unique_id = f"{device_id}_cloud_connected"
        self._attr_name = "Cloud Connected"
        self._attr_native_value = "unknown"

    async def async_update(self) -> None:
        """Update the sensor state."""
        try:
            # Test connection by getting device status
            await self.hass.async_add_executor_job(
                self._client.get_device_status, self._device_id
            )
            self._attr_native_value = "connected"
        except Exception as err:
            _LOGGER.error("Failed to check cloud connection for device %s: %s", self._device_id, err)
            self._attr_native_value = "disconnected"
