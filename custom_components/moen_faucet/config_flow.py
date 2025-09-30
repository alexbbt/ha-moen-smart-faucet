"""Config flow for Moen Faucet integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .client import MoenClient

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("client_id", default="moen_mobile_app"): str,
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
    client = MoenClient(
        client_id=data["client_id"],
        username=data[CONF_USERNAME],
        password=data[CONF_PASSWORD],
    )

    try:
        # Test the connection
        await hass.async_add_executor_job(client.login)

        # Get devices to verify the connection works
        devices = await hass.async_add_executor_job(client.list_devices)

        if not devices:
            raise InvalidAuth("No devices found for this account")

        return {"title": f"Moen Faucet ({len(devices)} devices)"}

    except Exception as err:
        _LOGGER.error("Failed to validate Moen API connection: %s", err)
        if "401" in str(err) or "unauthorized" in str(err).lower():
            raise InvalidAuth("Invalid credentials") from err
        raise CannotConnect(f"Failed to connect to Moen API: {err}") from err


class ConfigFlow(config_entries.ConfigFlow, domain="moen_faucet"):
    """Handle a config flow for Moen Faucet."""

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
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_import(self, import_info: dict[str, Any]) -> FlowResult:
        """Handle import from configuration.yaml."""
        return await self.async_step_user(import_info)
