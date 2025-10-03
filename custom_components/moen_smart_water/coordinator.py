"""Data update coordinator for Moen Smart Water integration."""

from __future__ import annotations

import logging
import time
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MoenAPI

_LOGGER = logging.getLogger(__name__)

# Polling interval - update every 30 seconds
SCAN_INTERVAL = timedelta(seconds=30)


class MoenDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching data from the Moen API."""

    def __init__(self, hass: HomeAssistant, api: MoenAPI, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.api = api
        self.entry = entry
        self._devices: dict[str, dict[str, Any]] = {}
        self._device_shadows: dict[str, dict[str, Any]] = {}
        self._device_details: dict[str, dict[str, Any]] = {}

        super().__init__(
            hass,
            _LOGGER,
            name="moen_smart_water",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            # Get fresh device list
            devices = await self.hass.async_add_executor_job(
                self.api.get_cached_devices
            )

            # Update device cache
            self._devices = {
                device.get("clientId", device.get("id", "")): device
                for device in devices
            }

            # Get device shadows for all devices (operational data)
            device_shadows = {}
            for device_id in self._devices.keys():
                try:
                    # Get device shadow
                    shadow = await self.hass.async_add_executor_job(
                        self.api.get_device_shadow, device_id
                    )
                    device_shadows[device_id] = shadow
                except Exception as err:
                    _LOGGER.warning(
                        "Failed to get shadow for device %s: %s", device_id, err
                    )
                    # Use empty shadow if we can't get it
                    device_shadows[device_id] = {}

            # Get device details only if we don't have them or they're stale (diagnostic data)
            current_time = time.time()
            if not hasattr(self, '_device_details') or not hasattr(self, '_details_last_update') or (current_time - self._details_last_update) > 300:  # 5 minutes
                device_details = {}
                for device_id in self._devices.keys():
                    try:
                        # Get device details with expanded attributes
                        details = await self.hass.async_add_executor_job(
                            self.api.get_device_details, device_id
                        )
                        device_details[device_id] = details
                    except Exception as err:
                        _LOGGER.warning(
                            "Failed to get device details for %s: %s", device_id, err
                        )
                        # Use empty details if we can't get it
                        device_details[device_id] = {}
                
                self._device_details = device_details
                self._details_last_update = current_time
            else:
                # Use cached device details
                device_details = getattr(self, '_device_details', {})

            self._device_shadows = device_shadows
            self._device_details = device_details

            # Store updated tokens if they were refreshed
            from . import _store_tokens

            await _store_tokens(self.hass, self.entry, self.api.get_tokens())

            return {
                "devices": self._devices,
                "device_shadows": self._device_shadows,
                "device_details": self._device_details,
            }

        except Exception as err:
            _LOGGER.error("Error communicating with Moen API: %s", err)
            raise UpdateFailed(f"Error communicating with Moen API: {err}") from err

    def get_device(self, device_id: str) -> dict[str, Any] | None:
        """Get device data by ID."""
        return self._devices.get(device_id)

    def get_device_shadow(self, device_id: str) -> dict[str, Any] | None:
        """Get device shadow data by ID."""
        return self._device_shadows.get(device_id)

    def get_all_devices(self) -> dict[str, dict[str, Any]]:
        """Get all devices."""
        return self._devices

    def get_all_device_shadows(self) -> dict[str, dict[str, Any]]:
        """Get all device shadows."""
        return self._device_shadows

    def get_device_details(self, device_id: str) -> dict[str, Any] | None:
        """Get device details with expanded attributes by ID."""
        return self._device_details.get(device_id)

    def get_all_device_details(self) -> dict[str, dict[str, Any]]:
        """Get all device details with expanded attributes."""
        return self._device_details
