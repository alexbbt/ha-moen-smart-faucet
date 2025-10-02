"""OAuth2 implementation for Moen Smart Water integration."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow


class MoenOAuth2Implementation(config_entry_oauth2_flow.LocalOAuth2Implementation):
    """OAuth2 implementation for Moen Smart Water."""

    def __init__(
        self, hass: HomeAssistant, domain: str, client_id: str, client_secret: str
    ):
        """Initialize OAuth2 implementation."""
        super().__init__(
            hass,
            domain,
            client_id,
            client_secret,
            "https://4j1gkf0vji.execute-api.us-east-2.amazonaws.com/prod/v1/oauth2/authorize",
            "https://4j1gkf0vji.execute-api.us-east-2.amazonaws.com/prod/v1/oauth2/token",
        )

    async def async_resolve_external_data(self, external_data: dict) -> dict:
        """Resolve external data to tokens."""
        # The external data should already contain the tokens from the OAuth2 flow
        return external_data
