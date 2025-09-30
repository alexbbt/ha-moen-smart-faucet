"""Services for Moen Faucet integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .client import MoenClient

_LOGGER = logging.getLogger(__name__)

# Service schemas
DISPENSE_SERVICE_SCHEMA = vol.Schema({
    vol.Required("device_id"): cv.string,
    vol.Optional("volume_ml", default=250): vol.All(int, vol.Range(min=50, max=2000)),
    vol.Optional("timeout", default=120): vol.All(int, vol.Range(min=10, max=300)),
})

STOP_DISPENSE_SERVICE_SCHEMA = vol.Schema({
    vol.Required("device_id"): cv.string,
})

GET_STATUS_SERVICE_SCHEMA = vol.Schema({
    vol.Required("device_id"): cv.string,
})

GET_USER_PROFILE_SERVICE_SCHEMA = vol.Schema({})


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up the services for Moen Faucet integration."""

    async def dispense_water(call: ServiceCall) -> None:
        """Service to dispense water from the faucet."""
        device_id = call.data["device_id"]
        volume_ml = call.data["volume_ml"]
        timeout = call.data["timeout"]

        # Find the client for this device
        client = None
        for entry_id, entry_client in hass.data.get("moen_faucet", {}).items():
            if isinstance(entry_client, MoenClient):
                devices = await hass.async_add_executor_job(entry_client.get_devices)
                if any(device.get("id", device.get("device_id")) == device_id for device in devices):
                    client = entry_client
                    break

        if not client:
            _LOGGER.error("Device %s not found in any configured Moen Faucet integration", device_id)
            return

        try:
            await hass.async_add_executor_job(
                client.start_dispense, device_id, volume_ml, timeout
            )
            _LOGGER.info("Started dispensing %dml from device %s", volume_ml, device_id)
        except Exception as err:
            _LOGGER.error("Failed to dispense water from device %s: %s", device_id, err)

    async def stop_dispensing(call: ServiceCall) -> None:
        """Service to stop dispensing water from the faucet."""
        device_id = call.data["device_id"]

        # Find the client for this device
        client = None
        for entry_id, entry_client in hass.data.get("moen_faucet", {}).items():
            if isinstance(entry_client, MoenClient):
                devices = await hass.async_add_executor_job(entry_client.get_devices)
                if any(device.get("id", device.get("device_id")) == device_id for device in devices):
                    client = entry_client
                    break

        if not client:
            _LOGGER.error("Device %s not found in any configured Moen Faucet integration", device_id)
            return

        try:
            await hass.async_add_executor_job(client.stop_dispense, device_id)
            _LOGGER.info("Stopped dispensing from device %s", device_id)
        except Exception as err:
            _LOGGER.error("Failed to stop dispensing from device %s: %s", device_id, err)

    async def get_device_status(call: ServiceCall) -> None:
        """Service to get device status."""
        device_id = call.data["device_id"]

        # Find the client for this device
        client = None
        for entry_id, entry_client in hass.data.get("moen_faucet", {}).items():
            if isinstance(entry_client, MoenClient):
                devices = await hass.async_add_executor_job(entry_client.get_devices)
                if any(device.get("id", device.get("device_id")) == device_id for device in devices):
                    client = entry_client
                    break

        if not client:
            _LOGGER.error("Device %s not found in any configured Moen Faucet integration", device_id)
            return

        try:
            status = await hass.async_add_executor_job(client.get_device_status, device_id)
            _LOGGER.info("Device %s status: %s", device_id, status)
        except Exception as err:
            _LOGGER.error("Failed to get status for device %s: %s", device_id, err)

    async def get_user_profile(call: ServiceCall) -> None:
        """Service to get user profile."""
        # Find any client (they all have the same user profile)
        client = None
        for entry_id, entry_client in hass.data.get("moen_faucet", {}).items():
            if isinstance(entry_client, MoenClient):
                client = entry_client
                break

        if not client:
            _LOGGER.error("No Moen Faucet integration found")
            return

        try:
            profile = await hass.async_add_executor_job(client.get_user_profile)
            _LOGGER.info("User profile: %s", profile)
        except Exception as err:
            _LOGGER.error("Failed to get user profile: %s", err)

    # Register services
    hass.services.async_register(
        "moen_faucet",
        "dispense_water",
        dispense_water,
        schema=DISPENSE_SERVICE_SCHEMA,
    )

    hass.services.async_register(
        "moen_faucet",
        "stop_dispensing",
        stop_dispensing,
        schema=STOP_DISPENSE_SERVICE_SCHEMA,
    )

    hass.services.async_register(
        "moen_faucet",
        "get_device_status",
        get_device_status,
        schema=GET_STATUS_SERVICE_SCHEMA,
    )

    hass.services.async_register(
        "moen_faucet",
        "get_user_profile",
        get_user_profile,
        schema=GET_USER_PROFILE_SERVICE_SCHEMA,
    )
