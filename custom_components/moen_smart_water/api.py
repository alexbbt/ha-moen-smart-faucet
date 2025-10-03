"""Moen Smart Water API client for all API operations."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

import requests

_LOGGER = logging.getLogger(__name__)

# API endpoints from the documentation
OAUTH_BASE = "https://4j1gkf0vji.execute-api.us-east-2.amazonaws.com/prod/v1"
API_BASE = "https://api.prod.iot.moen.com/v3"
INVOKER_BASE = "https://exo9f857n8.execute-api.us-east-2.amazonaws.com/prod/v1"

# Client ID for Moen Smart Water API (iOS app version 3.39.0)
CLIENT_ID = "6qn9pep31dglq6ed4fvlq6rp5t"

# User agent from the documentation
USER_AGENT = "Smartwater-iOS-prod-3.39.0"


class MoenAPI:
    """Comprehensive API client for Moen Smart Water operations."""

    def __init__(self, username: str, password: str, tokens: dict[str, Any] | None = None) -> None:
        """Initialize the Moen API client."""
        self.client_id = CLIENT_ID
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": USER_AGENT,
            }
        )

        # Authentication state
        self.access_token: str | None = None
        self.id_token: str | None = None
        self.refresh_token: str | None = None
        self.token_expiry = 0.0

        # Restore tokens if provided
        if tokens:
            self.access_token = tokens.get("access_token")
            self.id_token = tokens.get("id_token")
            self.refresh_token = tokens.get("refresh_token")
            self.token_expiry = tokens.get("token_expiry", 0.0)

            # Update session headers if we have a valid token
            if self.access_token and time.time() < self.token_expiry:
                self.session.headers.update(
                    {"Authorization": f"Bearer {self.access_token}"}
                )

        # Cached data
        self._user_profile: dict[str, Any] | None = None
        self._locations: list[dict[str, Any]] | None = None
        self._devices: list[dict[str, Any]] | None = None
        self._temperature_definitions: dict[str, Any] | None = None

    def _ensure_auth(self) -> None:
        """Ensure we have a valid authentication token."""
        if not self.access_token or time.time() > self.token_expiry:
            _LOGGER.info("Token expired or missing, attempting refresh")
            if self.refresh_token and not self._refresh_access_token():
                _LOGGER.info("Refresh failed, re-authenticating with username/password")
                self.login()

    def _refresh_access_token(self) -> bool:
        """Refresh the access token using the refresh token."""
        if not self.refresh_token:
            return False

        _LOGGER.info("Refreshing access token using refresh token")

        refresh_url = f"{OAUTH_BASE}/oauth2/token"

        # Create refresh token payload
        refresh_payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
        }

        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "User-Agent": USER_AGENT,
            "priority": "u=3",
        }

        try:
            import json

            json_string = json.dumps(refresh_payload)

            _LOGGER.debug("Refresh URL: %s", refresh_url)
            _LOGGER.debug("Refresh payload: %s", refresh_payload)

            response = self.session.post(
                refresh_url, data=json_string, headers=headers, timeout=30
            )

            _LOGGER.debug("Refresh response status: %s", response.status_code)
            response.raise_for_status()

            data = response.json()

            if "token" in data:
                token_data = data["token"]
                self.access_token = token_data.get("access_token")
                self.id_token = token_data.get("id_token")
                self.refresh_token = token_data.get("refresh_token", self.refresh_token)

                # Set expiry with 60 second buffer
                expires_in = token_data.get("expires_in", 3600)
                self.token_expiry = time.time() + expires_in - 60

                # Update session headers
                self.session.headers.update(
                    {"Authorization": f"Bearer {self.access_token}"}
                )

                _LOGGER.info("Successfully refreshed access token")
                return True
            else:
                _LOGGER.error("No token in refresh response: %s", data)
                return False

        except Exception as err:
            _LOGGER.error("Token refresh failed: %s", err)
            return False

    def login(self) -> dict[str, Any]:
        """Login to the Moen API and get access token."""
        _LOGGER.info("Starting login process for user: %s", self.username)

        login_url = f"{OAUTH_BASE}/oauth2/token"

        # Create JSON payload as shown in the documentation
        json_payload = {
            "client_id": self.client_id,
            "username": self.username,
            "password": self.password,
        }

        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "User-Agent": USER_AGENT,
            "priority": "u=3",
        }

        try:
            # Send JSON directly as request body (as shown in the API documentation)
            import json

            json_string = json.dumps(json_payload)

            _LOGGER.debug("Login URL: %s", login_url)
            _LOGGER.debug("Headers: %s", headers)
            _LOGGER.debug("JSON payload: %s", json_payload)
            _LOGGER.debug("JSON string: %s", json_string)

            response = self.session.post(
                login_url, data=json_string, headers=headers, timeout=30
            )

            _LOGGER.debug("Response status: %s", response.status_code)
            _LOGGER.debug("Response headers: %s", dict(response.headers))
            response.raise_for_status()

            data = response.json()

            if "token" in data:
                token_data = data["token"]
                self.access_token = token_data.get("access_token")
                self.id_token = token_data.get("id_token")
                self.refresh_token = token_data.get("refresh_token")

                # Set expiry with 60 second buffer
                expires_in = token_data.get("expires_in", 3600)
                self.token_expiry = time.time() + expires_in - 60

                # Update session headers
                self.session.headers.update(
                    {"Authorization": f"Bearer {self.access_token}"}
                )

                _LOGGER.info("Successfully authenticated with Moen API")
                return data
            else:
                _LOGGER.error("No token in response: %s", data)
                raise requests.exceptions.RequestException("No token in response")

        except requests.exceptions.RequestException as err:
            _LOGGER.error("Login failed: %s", err)
            raise

    def get_user_profile(self) -> dict[str, Any]:
        """Get user profile information."""
        self._ensure_auth()

        url = f"{OAUTH_BASE}/users/me"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            profile = response.json()
            self._user_profile = profile
            _LOGGER.info(
                "Retrieved user profile for %s", profile.get("email", "unknown")
            )
            return profile

        except requests.exceptions.RequestException as err:
            _LOGGER.error("Failed to get user profile: %s", err)
            raise

    def get_locations(self) -> list[dict[str, Any]]:
        """Get list of locations."""
        self._ensure_auth()

        url = f"{API_BASE}/locations"
        params = {"limit": 100}

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            locations = data.get("locations", [])
            self._locations = locations
            _LOGGER.info("Retrieved %d locations", len(locations))
            return locations

        except requests.exceptions.RequestException as err:
            _LOGGER.error("Failed to get locations: %s", err)
            raise

    def get_user_details_and_temperature_definitions(self) -> dict[str, Any]:
        """Get user details and temperature definitions."""
        self._ensure_auth()

        url = f"{INVOKER_BASE}/invoker"
        payload = {
            "body": {"locale": "en_US"},
            "escape": False,
            "fn": "smartwater-app-user-api-prod-get",
            "parse": False,
        }

        try:
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()
            if data.get("StatusCode") == 200:
                payload_data = json.loads(data["Payload"])
                body = payload_data.get("body", {})
                self._temperature_definitions = body.get("temperatureDefinitions", {})
                _LOGGER.info("Retrieved user details and temperature definitions")
                return body
            else:
                _LOGGER.error("Failed to get user details: %s", data)
                raise requests.exceptions.RequestException("Failed to get user details")

        except requests.exceptions.RequestException as err:
            _LOGGER.error("Failed to get user details: %s", err)
            raise

    def list_devices(self) -> list[dict[str, Any]]:
        """List all devices (filtering for VAK devices only)."""
        self._ensure_auth()

        url = f"{INVOKER_BASE}/invoker"
        payload = {
            "parse": False,
            "body": {"locale": "en_US"},
            "fn": "smartwater-app-device-api-prod-list",
            "escape": False,
        }

        try:
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()
            if data.get("StatusCode") == 200:
                payload_data = json.loads(data["Payload"])
                all_devices = payload_data.get("body", [])

                # Filter for VAK devices only (ignore FLO devices)
                vak_devices = [
                    device
                    for device in all_devices
                    if device.get("deviceType") == "VAK"
                ]
                self._devices = vak_devices
                _LOGGER.info(
                    "Retrieved %d VAK devices (filtered from %d total devices)",
                    len(vak_devices),
                    len(all_devices),
                )
                return vak_devices
            else:
                _LOGGER.error("Failed to list devices: %s", data)
                raise requests.exceptions.RequestException("Failed to list devices")

        except requests.exceptions.RequestException as err:
            _LOGGER.error("Failed to list devices: %s", err)
            raise

    def list_presets(self) -> list[dict[str, Any]]:
        """List presets for the device."""
        self._ensure_auth()

        url = f"{INVOKER_BASE}/invoker"
        payload = {
            "body": {"locale": "en_US"},
            "fn": "smartwater-app-preset-api-prod-list",
            "escape": False,
            "parse": False,
        }

        try:
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()
            if data.get("StatusCode") == 200:
                payload_data = json.loads(data["Payload"])
                presets = payload_data.get("body", [])
                _LOGGER.info("Retrieved %d presets", len(presets))
                return presets
            else:
                _LOGGER.error("Failed to list presets: %s", data)
                raise requests.exceptions.RequestException("Failed to list presets")

        except requests.exceptions.RequestException as err:
            _LOGGER.error("Failed to list presets: %s", err)
            raise

    def get_device_details(self, device_id: str, units: str = "imperial") -> dict[str, Any]:
        """Get detailed device information with all available attributes.

        Args:
            device_id: The device ID to get details for
            units: Units for measurements ("imperial" or "metric")
        """
        self._ensure_auth()

        url = f"{API_BASE}/device/{device_id}"
        params = {"expand": "addons", "units": units}

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            device_data = response.json()
            _LOGGER.info("Retrieved device details for %s", device_id)
            return device_data

        except requests.exceptions.RequestException as err:
            _LOGGER.error("Failed to get device details for %s: %s", device_id, err)
            raise

    def get_winterize_status(self, location_id: str) -> dict[str, Any]:
        """Get winterize status for a location."""
        self._ensure_auth()

        url = f"{API_BASE}/actions/routine/winterize"
        params = {"location": location_id}

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            winterize_data = response.json()
            _LOGGER.info("Retrieved winterize status for location %s", location_id)
            return winterize_data

        except requests.exceptions.RequestException as err:
            _LOGGER.error("Failed to get winterize status for %s: %s", location_id, err)
            raise

    def get_device_shadow(self, client_id: str) -> dict[str, Any]:
        """Get device shadow (current state and configuration)."""
        self._ensure_auth()

        url = f"{INVOKER_BASE}/invoker"
        payload = {
            "parse": False,
            "fn": "smartwater-app-shadow-api-prod-get",
            "escape": False,
            "body": {"clientId": client_id, "shadow": True, "locale": "en_US"},
        }

        try:
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()
            if data.get("StatusCode") == 200:
                payload_data = json.loads(data["Payload"])
                shadow_data = payload_data.get("body", {})
                _LOGGER.info("Retrieved device shadow for %s", client_id)
                return shadow_data
            else:
                _LOGGER.error("Failed to get device shadow: %s", data)
                raise requests.exceptions.RequestException(
                    "Failed to get device shadow"
                )

        except requests.exceptions.RequestException as err:
            _LOGGER.error("Failed to get device shadow for %s: %s", client_id, err)
            raise

    def get_daily_usage(
        self, client_id: str, timezone_offset: int = -7, query_date: int | None = None
    ) -> dict[str, Any]:
        """Get daily usage statistics."""
        self._ensure_auth()

        if query_date is None:
            query_date = int(time.time())

        url = f"{INVOKER_BASE}/invoker"
        payload = {
            "parse": False,
            "body": {
                "devices": [client_id],
                "timezoneOffset": timezone_offset,
                "depth": "DAILY",
                "locale": "en_US",
                "queryDate": query_date,
                "future": True,
            },
            "fn": "smartwater-app-usage-api-prod-get-v1",
            "escape": False,
        }

        try:
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()
            if data.get("StatusCode") == 200:
                payload_data = json.loads(data["Payload"])
                usage_data = payload_data.get("body", {})
                _LOGGER.info("Retrieved daily usage for %s", client_id)
                return usage_data
            else:
                _LOGGER.error("Failed to get daily usage: %s", data)
                raise requests.exceptions.RequestException("Failed to get daily usage")

        except requests.exceptions.RequestException as err:
            _LOGGER.error("Failed to get daily usage for %s: %s", client_id, err)
            raise

    def get_session_data(self, client_id: str, limit: int = 5) -> dict[str, Any]:
        """Get session data for a device."""
        self._ensure_auth()

        url = f"{INVOKER_BASE}/invoker"
        payload = {
            "body": {"limit": limit, "locale": "en_US", "clientId": client_id},
            "escape": False,
            "fn": "smartwater-app-session-api-prod-get-v1",
            "parse": False,
        }

        try:
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()
            if data.get("StatusCode") == 200:
                payload_data = json.loads(data["Payload"])
                session_data = payload_data.get("body", {})
                _LOGGER.info("Retrieved session data for %s", client_id)
                return session_data
            else:
                _LOGGER.error("Failed to get session data: %s", data)
                raise requests.exceptions.RequestException("Failed to get session data")

        except requests.exceptions.RequestException as err:
            _LOGGER.error("Failed to get session data for %s: %s", client_id, err)
            raise

    def update_device_shadow(
        self, client_id: str, payload_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update device shadow with new configuration."""
        self._ensure_auth()

        url = f"{INVOKER_BASE}/invoker"
        payload = {
            "parse": False,
            "fn": "smartwater-app-shadow-api-prod-update",
            "escape": False,
            "body": {"payload": payload_data, "locale": "en_US", "clientId": client_id},
        }

        try:
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()
            if data.get("StatusCode") == 200:
                payload_data = json.loads(data["Payload"])
                result = payload_data.get("body", {})
                _LOGGER.info("Updated device shadow for %s", client_id)
                return result
            else:
                _LOGGER.error("Failed to update device shadow: %s", data)
                raise requests.exceptions.RequestException(
                    "Failed to update device shadow"
                )

        except requests.exceptions.RequestException as err:
            _LOGGER.error("Failed to update device shadow for %s: %s", client_id, err)
            raise

    def start_water_flow(
        self, client_id: str, temperature: str | float = "coldest", flow_rate: int = 100
    ) -> dict[str, Any]:
        """Start water flow with specified temperature and flow rate."""
        payload_data = {
            "commandSrc": "app",
            "command": "run",
            "temperature": temperature,
            "flowRate": flow_rate,
        }
        return self.update_device_shadow(client_id, payload_data)

    def stop_water_flow(self, client_id: str) -> dict[str, Any]:
        """Stop water flow."""
        payload_data = {"commandSrc": "app", "command": "stop"}
        return self.update_device_shadow(client_id, payload_data)

    def set_temperature(
        self, client_id: str, temperature: str | float, flow_rate: int = 100
    ) -> dict[str, Any]:
        """Set specific temperature for water flow."""
        return self.start_water_flow(client_id, temperature, flow_rate)

    def set_coldest(self, client_id: str, flow_rate: int = 100) -> dict[str, Any]:
        """Set water to coldest temperature."""
        return self.start_water_flow(client_id, "coldest", flow_rate)

    def set_hottest(self, client_id: str, flow_rate: int = 100) -> dict[str, Any]:
        """Set water to hottest temperature."""
        return self.start_water_flow(client_id, "hottest", flow_rate)

    def set_warm(self, client_id: str, flow_rate: int = 100) -> dict[str, Any]:
        """Set water to warm temperature."""
        return self.start_water_flow(client_id, "warm", flow_rate)

    def set_specific_temperature(
        self, client_id: str, temperature_celsius: float, flow_rate: int = 100
    ) -> dict[str, Any]:
        """Set specific temperature in Celsius."""
        return self.start_water_flow(client_id, temperature_celsius, flow_rate)

    def update_device_settings(
        self, client_id: str, settings: dict[str, Any]
    ) -> dict[str, Any]:
        """Update various device settings."""
        payload_data = {"commandSrc": "app", **settings}
        return self.update_device_shadow(client_id, payload_data)

    def set_freeze_enable(self, client_id: str, enabled: bool) -> dict[str, Any]:
        """Enable or disable freeze protection."""
        return self.update_device_settings(client_id, {"freezeEnable": enabled})

    def set_timeouts(
        self,
        client_id: str,
        handle_timeout: int = 300,
        sensor_timeout: int = 300,
        voice_timeout: int = 300,
        dispense_activate_timeout: int = 120,
    ) -> dict[str, Any]:
        """Set various timeout values."""
        settings = {
            "handleTimeout": handle_timeout,
            "sensorTimeout": sensor_timeout,
            "voiceTimeout": voice_timeout,
            "dispenseActivateTimeout": dispense_activate_timeout,
        }
        return self.update_device_settings(client_id, settings)

    def set_flow_rate(self, client_id: str, flow_rate: int) -> dict[str, Any]:
        """Set default flow rate."""
        return self.update_device_settings(client_id, {"defaultFlowRate": flow_rate})

    # Convenience methods for getting cached data
    def get_cached_devices(self) -> list[dict[str, Any]]:
        """Get cached devices or fetch if not available."""
        if self._devices is None:
            self.list_devices()
        return self._devices or []

    def get_cached_locations(self) -> list[dict[str, Any]]:
        """Get cached locations or fetch if not available."""
        if self._locations is None:
            self.get_locations()
        return self._locations or []

    def get_cached_user_profile(self) -> dict[str, Any]:
        """Get cached user profile or fetch if not available."""
        if self._user_profile is None:
            self.get_user_profile()
        return self._user_profile or {}

    def get_cached_temperature_definitions(self) -> dict[str, Any]:
        """Get cached temperature definitions or fetch if not available."""
        if self._temperature_definitions is None:
            self.get_user_details_and_temperature_definitions()
        return self._temperature_definitions or {}

    def get_tokens(self) -> dict[str, Any]:
        """Get current authentication tokens."""
        return {
            "access_token": self.access_token,
            "id_token": self.id_token,
            "refresh_token": self.refresh_token,
            "token_expiry": self.token_expiry,
        }
