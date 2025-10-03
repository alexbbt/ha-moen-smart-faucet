"""Moen Smart Water integration for Home Assistant."""

from __future__ import annotations

import logging
import time
from typing import Any

__version__ = "0.8.18"

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .api import MoenAPI
from .coordinator import MoenDataUpdateCoordinator
from .services import async_setup_services

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.BUTTON,
    Platform.DATETIME,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SELECT,
    Platform.VALVE,
]


async def _store_tokens(
    hass: HomeAssistant, entry: ConfigEntry, tokens: dict[str, Any]
) -> None:
    """Store tokens in the config entry."""
    # Update the config entry with new tokens
    new_data = {**entry.data, "tokens": tokens}
    hass.config_entries.async_update_entry(entry, data=new_data)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Moen Smart Water from a config entry."""
    hass.data.setdefault("moen_smart_water", {})

    # Get stored tokens from config entry
    stored_tokens = entry.data.get("tokens")

    # Initialize the API client with stored tokens
    api = MoenAPI(
        username=entry.data["username"],
        password=entry.data["password"],
        tokens=stored_tokens,
    )

    # Test the connection and get user profile
    try:
        # Only login if we don't have valid tokens
        if not api.access_token or time.time() > api.token_expiry:
            await hass.async_add_executor_job(api.login)
            # Store the new tokens
            await _store_tokens(hass, entry, api.get_tokens())

        user_profile = await hass.async_add_executor_job(api.get_user_profile)
        _LOGGER.info(
            "Successfully connected to Moen API for user: %s",
            user_profile.get("email", "unknown"),
        )
    except Exception as err:
        _LOGGER.error("Failed to connect to Moen API: %s", err)
        return False

    # Create coordinator for data updates
    coordinator = MoenDataUpdateCoordinator(hass, api, entry)

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Store the coordinator in hass data
    hass.data["moen_smart_water"][entry.entry_id] = coordinator

    # Forward the setup to the platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Set up services
    await async_setup_services(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data["moen_smart_water"].pop(entry.entry_id)

    return unload_ok
