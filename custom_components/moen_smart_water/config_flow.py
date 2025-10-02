"""Config flow for Moen Smart Water integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_entry_oauth2_flow

from .api import CLIENT_ID, MoenAPI
from .oauth2_impl import MoenOAuth2Implementation

_LOGGER = logging.getLogger(__name__)


class MoenSmartWaterConfigFlow(config_entry_oauth2_flow.AbstractOAuth2FlowHandler):
    """Handle a config flow for Moen Smart Water."""

    DOMAIN = "moen_smart_water"

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return _LOGGER

    @property
    def extra_authorize_data(self) -> dict[str, Any]:
        """Extra data that needs to be appended to the authorize url."""
        return {
            "scope": "openid profile email",
            "response_type": "code",
        }

    async def async_oauth_create_entry(self, data: dict[str, Any]) -> FlowResult:
        """Create an entry for the flow, or update existing entry."""
        # Get user profile to create a meaningful title
        try:
            api = MoenAPI.from_token(data["token"])
            user_profile = await self.hass.async_add_executor_job(api.get_user_profile)

            # Try to get devices to see if we can find any
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
                data=data,
            )
        except Exception as err:
            _LOGGER.error("Failed to validate Moen API connection: %s", err)
            return self.async_abort(reason="cannot_connect")

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if not self.flow_impl:
            return self.async_abort(reason="missing_configuration")
        return await self.async_step_pick_implementation()

    async def async_step_pick_implementation(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the step to pick implementation."""
        if user_input is not None:
            await self.async_set_external_data(
                {"implementation": user_input["implementation"]}
            )
            return await self.async_step_auth()

        implementations = await self.async_get_implementations()
        if not implementations:
            return self.async_abort(reason="missing_configuration")

        return self.async_show_form(
            step_id="pick_implementation",
            data_schema=vol.Schema(
                {
                    vol.Required("implementation"): vol.In(
                        {impl.domain: impl.name for impl in implementations}
                    )
                }
            ),
        )

    async def async_get_implementations(
        self,
    ) -> list[config_entry_oauth2_flow.LocalOAuth2Implementation]:
        """Return list of OAuth2 implementations."""
        return [
            MoenOAuth2Implementation(
                self.hass,
                "moen_smart_water",
                CLIENT_ID,
                "",  # Client secret will be provided by application_credentials
            )
        ]
