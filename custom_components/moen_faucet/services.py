"""Services for Moen Faucet integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .api import MoenAPI

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

SET_TEMPERATURE_SERVICE_SCHEMA = vol.Schema({
    vol.Required("device_id"): cv.string,
    vol.Required("temperature"): vol.All(float, vol.Range(min=0, max=100)),
    vol.Optional("flow_rate", default=100): vol.All(int, vol.Range(min=0, max=100)),
})

SET_FLOW_RATE_SERVICE_SCHEMA = vol.Schema({
    vol.Required("device_id"): cv.string,
    vol.Required("flow_rate"): vol.All(int, vol.Range(min=0, max=100)),
})


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up the services for Moen Faucet integration."""

    async def dispense_water(call: ServiceCall) -> None:
        """Service to dispense water from the faucet."""
        device_id = call.data["device_id"]
        volume_ml = call.data["volume_ml"]
        timeout = call.data["timeout"]

        # Find the API client for this device
        api = None
        for entry_id, entry_api in hass.data.get("moen_faucet", {}).items():
            if isinstance(entry_api, MoenAPI):
                devices = await hass.async_add_executor_job(entry_api.get_cached_devices)
                if any(device.get("clientId", device.get("id", device.get("device_id"))) == device_id for device in devices):
                    api = entry_api
                    break

        if not api:
            _LOGGER.error("Device %s not found in any configured Moen Faucet integration", device_id)
            return

        try:
            await hass.async_add_executor_job(
                api.start_water_flow, device_id, "coldest", 100
            )
            _LOGGER.info("Started dispensing from device %s", device_id)
        except Exception as err:
            _LOGGER.error("Failed to dispense water from device %s: %s", device_id, err)

    async def stop_dispensing(call: ServiceCall) -> None:
        """Service to stop dispensing water from the faucet."""
        device_id = call.data["device_id"]

        # Find the API client for this device
        api = None
        for entry_id, entry_api in hass.data.get("moen_faucet", {}).items():
            if isinstance(entry_api, MoenAPI):
                devices = await hass.async_add_executor_job(entry_api.get_cached_devices)
                if any(device.get("clientId", device.get("id", device.get("device_id"))) == device_id for device in devices):
                    api = entry_api
                    break

        if not api:
            _LOGGER.error("Device %s not found in any configured Moen Faucet integration", device_id)
            return

        try:
            await hass.async_add_executor_job(api.stop_water_flow, device_id)
            _LOGGER.info("Stopped dispensing from device %s", device_id)
        except Exception as err:
            _LOGGER.error("Failed to stop dispensing from device %s: %s", device_id, err)

    async def get_device_status(call: ServiceCall) -> None:
        """Service to get device status."""
        device_id = call.data["device_id"]

        # Find the API client for this device
        api = None
        for entry_id, entry_api in hass.data.get("moen_faucet", {}).items():
            if isinstance(entry_api, MoenAPI):
                devices = await hass.async_add_executor_job(entry_api.get_cached_devices)
                if any(device.get("clientId", device.get("id", device.get("device_id"))) == device_id for device in devices):
                    api = entry_api
                    break

        if not api:
            _LOGGER.error("Device %s not found in any configured Moen Faucet integration", device_id)
            return

        try:
            shadow = await hass.async_add_executor_job(api.get_device_shadow, device_id)
            _LOGGER.info("Device %s shadow: %s", device_id, shadow)
        except Exception as err:
            _LOGGER.error("Failed to get status for device %s: %s", device_id, err)

    async def get_user_profile(call: ServiceCall) -> None:
        """Service to get user profile."""
        # Find any API client (they all have the same user profile)
        api = None
        for entry_id, entry_api in hass.data.get("moen_faucet", {}).items():
            if isinstance(entry_api, MoenAPI):
                api = entry_api
                break

        if not api:
            _LOGGER.error("No Moen Faucet integration found")
            return

        try:
            profile = await hass.async_add_executor_job(api.get_user_profile)
            _LOGGER.info("User profile: %s", profile)
        except Exception as err:
            _LOGGER.error("Failed to get user profile: %s", err)

    async def set_temperature(call: ServiceCall) -> None:
        """Service to set water temperature."""
        device_id = call.data["device_id"]
        temperature = call.data["temperature"]
        flow_rate = call.data["flow_rate"]

        # Find the API client for this device
        api = None
        for entry_id, entry_api in hass.data.get("moen_faucet", {}).items():
            if isinstance(entry_api, MoenAPI):
                devices = await hass.async_add_executor_job(entry_api.get_cached_devices)
                if any(device.get("clientId", device.get("id", device.get("device_id"))) == device_id for device in devices):
                    api = entry_api
                    break

        if not api:
            _LOGGER.error("Device %s not found in any configured Moen Faucet integration", device_id)
            return

        try:
            await hass.async_add_executor_job(
                api.set_specific_temperature, device_id, temperature, flow_rate
            )
            _LOGGER.info("Set temperature to %.1f°C for device %s", temperature, device_id)
        except Exception as err:
            _LOGGER.error("Failed to set temperature for device %s: %s", device_id, err)

    async def set_flow_rate(call: ServiceCall) -> None:
        """Service to set flow rate."""
        device_id = call.data["device_id"]
        flow_rate = call.data["flow_rate"]

        # Find the API client for this device
        api = None
        for entry_id, entry_api in hass.data.get("moen_faucet", {}).items():
            if isinstance(entry_api, MoenAPI):
                devices = await hass.async_add_executor_job(entry_api.get_cached_devices)
                if any(device.get("clientId", device.get("id", device.get("device_id"))) == device_id for device in devices):
                    api = entry_api
                    break

        if not api:
            _LOGGER.error("Device %s not found in any configured Moen Faucet integration", device_id)
            return

        try:
            await hass.async_add_executor_job(api.set_flow_rate, device_id, flow_rate)
            _LOGGER.info("Set flow rate to %d%% for device %s", flow_rate, device_id)
        except Exception as err:
            _LOGGER.error("Failed to set flow rate for device %s: %s", device_id, err)

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

    hass.services.async_register(
        "moen_faucet",
        "set_temperature",
        set_temperature,
        schema=SET_TEMPERATURE_SERVICE_SCHEMA,
    )

    hass.services.async_register(
        "moen_faucet",
        "set_flow_rate",
        set_flow_rate,
        schema=SET_FLOW_RATE_SERVICE_SCHEMA,
    )
