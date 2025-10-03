"""Config flow for Moen Smart Water integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .api import MoenAPI

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    api = MoenAPI(
        username=data[CONF_USERNAME],
        password=data[CONF_PASSWORD],
    )

    try:
        # Test the connection
        await hass.async_add_executor_job(api.login)

        # Test the /users/me endpoint to verify authentication works
        user_profile = await hass.async_add_executor_job(api.get_user_profile)
        _LOGGER.info(
            "Successfully authenticated and retrieved user profile: %s",
            user_profile.get("email", "unknown"),
        )

        # Try to get devices to see if we can find any
        try:
            devices = await hass.async_add_executor_job(api.list_devices)
            device_count = len(devices) if devices else 0
            _LOGGER.info("Found %d devices", device_count)
        except Exception as device_err:
            _LOGGER.warning(
                "Could not retrieve devices, but authentication works: %s", device_err
            )
            devices = []
            device_count = 0

        return {
            "title": f"Moen Smart Water ({user_profile.get('firstName', 'User')} - {device_count} devices)",
            "user_profile": user_profile,
            "device_count": device_count,
            "tokens": api.get_tokens(),
        }

    except Exception as err:
        _LOGGER.error("Failed to validate Moen API connection: %s", err)
        if "401" in str(err) or "unauthorized" in str(err).lower():
            raise InvalidAuth("Invalid credentials") from err
        raise CannotConnect(f"Failed to connect to Moen API: {err}") from err


class ConfigFlow(config_entries.ConfigFlow, domain="moen_smart_water"):
    """Handle a config flow for Moen Smart Water."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Include tokens in the config entry data
                config_data = {**user_input, "tokens": info["tokens"]}
                return self.async_create_entry(title=info["title"], data=config_data)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_import(self, import_info: dict[str, Any]) -> FlowResult:
        """Handle import from configuration.yaml."""
        return await self.async_step_user(import_info)
