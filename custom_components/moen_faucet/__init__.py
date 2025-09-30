"""Moen Smart Faucet integration for Home Assistant."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .client import MoenClient
from .services import async_setup_services

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Moen Faucet from a config entry."""
    hass.data.setdefault("moen_faucet", {})

    # Initialize the client
    client = MoenClient(
        client_id=entry.data["client_id"],
        username=entry.data["username"],
        password=entry.data["password"],
    )

    # Test the connection and get user profile
    try:
        await hass.async_add_executor_job(client.login)
        user_profile = await hass.async_add_executor_job(client.get_user_profile)
        _LOGGER.info("Successfully connected to Moen API for user: %s", user_profile.get("email", "unknown"))
        
        # Store user profile in the client for later use
        client._user_profile = user_profile
    except Exception as err:
        _LOGGER.error("Failed to connect to Moen API: %s", err)
        return False

    # Store the client in hass data
    hass.data["moen_faucet"][entry.entry_id] = client

    # Forward the setup to the platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Set up services
    await async_setup_services(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data["moen_faucet"].pop(entry.entry_id)

    return unload_ok
