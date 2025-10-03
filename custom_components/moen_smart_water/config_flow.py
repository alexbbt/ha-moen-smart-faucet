"""Config flow for Moen Smart Water integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .api import MoenAPI

_LOGGER = logging.getLogger(__name__)


class MoenSmartWaterConfigFlow(config_entries.ConfigFlow):
    """Handle a config flow for Moen Smart Water."""

    VERSION = 1

    @property
    def domain(self) -> str:
        """Return the domain."""
        return "moen_smart_water"

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required("username"): str,
                        vol.Required("password"): str,
                    }
                ),
            )

        # Check if already configured
        await self.async_set_unique_id(user_input["username"])
        self._abort_if_unique_id_configured()

        # Test the connection
        try:
            api = MoenAPI(
                username=user_input["username"],
                password=user_input["password"],
            )

            # Test login
            await self.hass.async_add_executor_job(api.login)
            user_profile = await self.hass.async_add_executor_job(api.get_user_profile)

            # Try to get devices
            try:
                devices = await self.hass.async_add_executor_job(api.list_devices)
                device_count = len(devices) if devices else 0
                _LOGGER.info("Found %d devices", device_count)
            except Exception as device_err:
                _LOGGER.warning(
                    "Could not retrieve devices, but authentication works: %s",
                    device_err,
                )
                devices = []
                device_count = 0

            title = f"Moen Smart Water ({user_profile.get('firstName', 'User')} - {device_count} devices)"

            return self.async_create_entry(
                title=title,
                data=user_input,
            )
        except Exception as err:
            _LOGGER.error("Failed to validate Moen API connection: %s", err)
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required("username"): str,
                        vol.Required("password"): str,
                    }
                ),
                errors={"base": "cannot_connect"},
            )
