"""Application credentials for Moen Smart Water integration."""

from __future__ import annotations

from homeassistant.components.application_credentials import AuthorizationServer
from homeassistant.core import HomeAssistant

# OAuth endpoints from the Moen API documentation
OAUTH_BASE = "https://4j1gkf0vji.execute-api.us-east-2.amazonaws.com/prod/v1"


async def async_get_authorization_server(hass: HomeAssistant) -> AuthorizationServer:
    """Return authorization server."""
    return AuthorizationServer(
        authorize_url=f"{OAUTH_BASE}/oauth2/authorize",
        token_url=f"{OAUTH_BASE}/oauth2/token",
    )
