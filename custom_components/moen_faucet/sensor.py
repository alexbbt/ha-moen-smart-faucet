"""Sensor platform for Moen Faucet integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import MoenAPI

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Moen Faucet sensor entities."""
    api: MoenAPI = hass.data["moen_faucet"][config_entry.entry_id]

    # Get devices and create entities for each
    devices = await hass.async_add_executor_job(api.get_cached_devices)

    entities = []
    for device in devices:
        device_id = device.get("clientId", device.get("id", device.get("device_id")))
        device_name = device.get("name", f"Moen Faucet {device_id}")

        entities.extend([
            MoenFaucetStateSensor(api, device_id, device_name),
            MoenLastDispenseVolumeSensor(api, device_id, device_name),
            MoenCloudConnectedSensor(api, device_id, device_name),
            MoenTemperatureSensor(api, device_id, device_name),
            MoenFlowRateSensor(api, device_id, device_name),
        ])

    async_add_entities(entities)


class MoenSensorBase(SensorEntity):
    """Base class for Moen sensor entities."""

    def __init__(self, api: MoenAPI, device_id: str, device_name: str) -> None:
        """Initialize the sensor."""
        self._api = api
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

    def __init__(self, api: MoenAPI, device_id: str, device_name: str) -> None:
        """Initialize the faucet state sensor."""
        super().__init__(api, device_id, device_name)
        self._attr_unique_id = f"{device_id}_faucet_state"
        self._attr_name = "Faucet State"
        self._attr_native_value = "unknown"

    async def async_update(self) -> None:
        """Update the sensor state."""
        try:
            shadow = await self.hass.async_add_executor_job(
                self._api.get_device_shadow, self._device_id
            )
            # Extract state from shadow data
            state = shadow.get("state", {}).get("reported", {})
            if state.get("command") == "run":
                self._attr_native_value = "running"
            elif state.get("command") == "stop":
                self._attr_native_value = "stopped"
            else:
                self._attr_native_value = "idle"
        except Exception as err:
            _LOGGER.error("Failed to update faucet state for device %s: %s", self._device_id, err)
            self._attr_native_value = "error"


class MoenLastDispenseVolumeSensor(MoenSensorBase):
    """Sensor for last dispense volume."""

    def __init__(self, api: MoenAPI, device_id: str, device_name: str) -> None:
        """Initialize the last dispense volume sensor."""
        super().__init__(api, device_id, device_name)
        self._attr_unique_id = f"{device_id}_last_dispense_volume"
        self._attr_name = "Last Dispense Volume"
        self._attr_native_unit_of_measurement = "ml"
        self._attr_native_value = 0

    async def async_update(self) -> None:
        """Update the sensor state."""
        try:
            shadow = await self.hass.async_add_executor_job(
                self._api.get_device_shadow, self._device_id
            )
            # Extract last dispense volume from shadow data
            state = shadow.get("state", {}).get("reported", {})
            self._attr_native_value = state.get("lastDispenseVolume", 0)
        except Exception as err:
            _LOGGER.error("Failed to update last dispense volume for device %s: %s", self._device_id, err)


class MoenCloudConnectedSensor(MoenSensorBase):
    """Sensor for cloud connection status."""

    def __init__(self, api: MoenAPI, device_id: str, device_name: str) -> None:
        """Initialize the cloud connected sensor."""
        super().__init__(api, device_id, device_name)
        self._attr_unique_id = f"{device_id}_cloud_connected"
        self._attr_name = "Cloud Connected"
        self._attr_native_value = "unknown"

    async def async_update(self) -> None:
        """Update the sensor state."""
        try:
            # Test connection by getting device shadow
            await self.hass.async_add_executor_job(
                self._api.get_device_shadow, self._device_id
            )
            self._attr_native_value = "connected"
        except Exception as err:
            _LOGGER.error("Failed to check cloud connection for device %s: %s", self._device_id, err)
            self._attr_native_value = "disconnected"


class MoenTemperatureSensor(MoenSensorBase):
    """Sensor for current water temperature."""

    def __init__(self, api: MoenAPI, device_id: str, device_name: str) -> None:
        """Initialize the temperature sensor."""
        super().__init__(api, device_id, device_name)
        self._attr_unique_id = f"{device_id}_temperature"
        self._attr_name = "Temperature"
        self._attr_native_unit_of_measurement = "°C"
        self._attr_native_value = 0

    async def async_update(self) -> None:
        """Update the sensor state."""
        try:
            shadow = await self.hass.async_add_executor_job(
                self._api.get_device_shadow, self._device_id
            )
            # Extract temperature from shadow data
            state = shadow.get("state", {}).get("reported", {})
            self._attr_native_value = state.get("temperature", 0)
        except Exception as err:
            _LOGGER.error("Failed to update temperature for device %s: %s", self._device_id, err)


class MoenFlowRateSensor(MoenSensorBase):
    """Sensor for current flow rate."""

    def __init__(self, api: MoenAPI, device_id: str, device_name: str) -> None:
        """Initialize the flow rate sensor."""
        super().__init__(api, device_id, device_name)
        self._attr_unique_id = f"{device_id}_flow_rate"
        self._attr_name = "Flow Rate"
        self._attr_native_unit_of_measurement = "%"
        self._attr_native_value = 0

    async def async_update(self) -> None:
        """Update the sensor state."""
        try:
            shadow = await self.hass.async_add_executor_job(
                self._api.get_device_shadow, self._device_id
            )
            # Extract flow rate from shadow data
            state = shadow.get("state", {}).get("reported", {})
            self._attr_native_value = state.get("flowRate", 0)
        except Exception as err:
            _LOGGER.error("Failed to update flow rate for device %s: %s", self._device_id, err)
