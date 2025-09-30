"""Client for Moen Smart Faucet API."""
from __future__ import annotations

import logging
import time
from typing import Any

import requests

_LOGGER = logging.getLogger(__name__)

# API endpoints - updated with correct values from network capture
# Correct API host and path from working curl command
API_HOST = "4j1gkf0vji.execute-api.us-east-2.amazonaws.com"
API_BASE = f"https://{API_HOST}/prod/v1"


class MoenClient:
    """Client for communicating with Moen Smart Faucet API."""

    def __init__(self, client_id: str, username: str, password: str) -> None:
        """Initialize the Moen client."""
        self.client_id = client_id
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.token: str | None = None
        self.expiry = 0.0
        self._devices: list[dict[str, Any]] | None = None

    def _try_login_endpoint(self, base_url: str) -> dict[str, Any]:
        """Try to login to a specific endpoint."""
        # Create JSON payload as shown in the working curl command
        json_payload = {
            "client_id": self.client_id,
            "username": self.username,
            "password": self.password,
        }

        # Use the correct OAuth2 token endpoint
        login_url = f"{base_url}/oauth2/token"
        _LOGGER.debug("Attempting login to %s with client_id: %s", login_url, self.client_id)

        # Set headers to match the working curl command exactly
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "User-Agent": "Smartwater-iOS-prod-3.39.0",
            "priority": "u=3",
        }

        try:
            # Send JSON directly as the body
            import json

            # Create the JSON payload string exactly like the curl command
            json_string = json.dumps(json_payload)
            _LOGGER.debug("JSON payload: %s", json_string)

            response = self.session.post(
                login_url,
                data=json_string,
                headers=headers,
                timeout=30
            )

            # Log response details for debugging
            _LOGGER.debug("Login response status: %s", response.status_code)
            _LOGGER.debug("Login response headers: %s", dict(response.headers))

            if response.status_code == 200:
                data = response.json()

                # Check if response contains token with access_token
                if "token" in data and "access_token" in data["token"]:
                    token_data = data["token"]
                    self.token = token_data["access_token"]
                    # Set expiry with 60 second buffer
                    self.expiry = time.time() + token_data.get("expires_in", 3600) - 60
                    self.session.headers.update({"Authorization": f"Bearer {self.token}"})

                    _LOGGER.info("Successfully logged in to Moen API at %s", login_url)
                    return data
                else:
                    _LOGGER.error("No access_token in response from %s. Response data: %s", login_url, data)
                    return None
            else:
                _LOGGER.error(
                    "Login failed with status %s for endpoint: %s. Response: %s. "
                    "Request headers: %s. Request body: %s",
                    response.status_code, login_url, response.text,
                    dict(response.request.headers), response.request.body
                )
                return None

        except requests.exceptions.RequestException as err:
            _LOGGER.error("Request failed for %s: %s", login_url, err)
            return None

    def login(self) -> dict[str, Any]:
        """Login to the Moen API and get access token."""
        _LOGGER.info("Starting login process with client_id: %s", self.client_id)

        # Use the correct API endpoint
        result = self._try_login_endpoint(API_BASE)
        if result:
            return result

        # If login fails, raise an error with technical details
        _LOGGER.error(
            "Login failed - API endpoint: %s, Client ID: %s, Username: %s. "
            "This suggests the request format still doesn't match the working curl command. "
            "Check debug logs above for exact payload being sent.",
            f"{API_BASE}/oauth2/token", self.client_id, self.username
        )

        raise requests.exceptions.RequestException("Login failed")

    def ensure_auth(self) -> None:
        """Ensure we have a valid authentication token."""
        if not self.token or time.time() > self.expiry:
            _LOGGER.info("Token expired or missing, re-authenticating")
            self.login()

    def get_user_profile(self) -> dict[str, Any]:
        """Get user profile information."""
        self.ensure_auth()

        if not self.token:
            _LOGGER.error("No valid authentication token available")
            raise requests.exceptions.RequestException("No valid authentication token")

        try:
            profile_url = f"{API_BASE}/users/me"
            _LOGGER.debug("Getting user profile from %s", profile_url)

            response = self.session.get(profile_url, timeout=30)
            response.raise_for_status()

            profile = response.json()
            _LOGGER.info("Retrieved user profile for %s", profile.get("email", "unknown"))
            _LOGGER.debug("User profile data: %s", profile)
            return profile

        except requests.exceptions.RequestException as err:
            _LOGGER.error("Failed to get user profile: %s", err)
            raise

    def list_devices(self) -> list[dict[str, Any]]:
        """Get list of devices from the API."""
        self.ensure_auth()
        
        # Check if we have a valid token
        if not self.token:
            _LOGGER.error("No valid authentication token available")
            raise requests.exceptions.RequestException("No valid authentication token")
        
        # First try to get user profile to see if we can find account-specific endpoints
        try:
            profile = self.get_user_profile()
            account_id = profile.get("account", {}).get("id")
            if account_id:
                _LOGGER.info("Found account ID: %s", account_id)
        except Exception as err:
            _LOGGER.debug("Could not get user profile: %s", err)
            account_id = None
        
        # Try different device paths based on the API pattern
        device_paths = [
            "/devices",
            "/users/me/devices", 
            "/api/devices",
            "/v1/devices",
            "/prod/devices",
            "/accounts/devices",
            "/user/devices",
            "/my/devices",
            "/device/list",
            "/devices/list",
            "/api/v1/devices",
            "/v1/api/devices",
        ]
        
        # Add account-specific paths if we have an account ID
        if account_id:
            device_paths.extend([
                f"/accounts/{account_id}/devices",
                f"/account/{account_id}/devices",
                f"/users/{account_id}/devices",
            ])

        for path in device_paths:
            try:
                devices_url = f"{API_BASE}{path}"
                _LOGGER.debug("Attempting to get devices from %s with token: %s...", devices_url, self.token[:10])

                response = self.session.get(devices_url, timeout=30)

                if response.status_code == 403:
                    _LOGGER.warning("403 Forbidden for devices endpoint: %s", devices_url)
                    _LOGGER.warning("This suggests the authentication token is invalid or expired")
                    continue
                elif response.status_code == 401:
                    _LOGGER.warning("401 Unauthorized for devices endpoint: %s", devices_url)
                    _LOGGER.warning("Authentication token is invalid, trying to re-authenticate")
                    # Try to re-authenticate
                    try:
                        self.login()
                        response = self.session.get(devices_url, timeout=30)
                        if response.status_code == 200:
                            devices = response.json()
                            self._devices = devices
                            _LOGGER.info("Retrieved %d devices from Moen API at %s after re-authentication", len(devices), devices_url)
                            return devices
                    except Exception as reauth_err:
                        _LOGGER.error("Re-authentication failed: %s", reauth_err)
                        continue
                elif response.status_code == 404:
                    _LOGGER.debug("404 Not Found for devices endpoint: %s", devices_url)
                    continue
                elif response.status_code == 200:
                    devices = response.json()

                    # Cache devices for later use
                    self._devices = devices
                    _LOGGER.info("Retrieved %d devices from Moen API at %s", len(devices), devices_url)
                    return devices
                else:
                    _LOGGER.debug("Unexpected status code %s for devices endpoint: %s", response.status_code, devices_url)
                    response.raise_for_status()

            except requests.exceptions.RequestException as err:
                _LOGGER.debug("Request failed for devices endpoint %s: %s", devices_url, err)
                continue

        # If all paths fail, raise an error
        _LOGGER.error("All device endpoints failed - this usually means authentication is not working")
        raise requests.exceptions.RequestException("All device endpoints failed - check authentication")

    def get_device_status(self, device_id: str) -> dict[str, Any]:
        """Get status of a specific device."""
        self.ensure_auth()

        try:
            response = self.session.get(f"{API_BASE}/devices/{device_id}/status", timeout=30)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as err:
            _LOGGER.error("Failed to get device status for %s: %s", device_id, err)
            raise

    def send_command(self, device_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Send a command to a specific device."""
        self.ensure_auth()

        try:
            response = self.session.post(
                f"{API_BASE}/devices/{device_id}/commands",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            _LOGGER.info("Command sent to device %s: %s", device_id, payload)
            return result

        except requests.exceptions.RequestException as err:
            _LOGGER.error("Failed to send command to device %s: %s", device_id, err)
            raise

    def start_dispense(self, device_id: str, volume_ml: int = 250, timeout: int = 120) -> dict[str, Any]:
        """Start dispensing water from the faucet."""
        payload = {
            "commandSrc": "app",
            "action": "dispense",
            "volume_ml": volume_ml,
            "dispenseActiveTimeout": timeout,
        }
        return self.send_command(device_id, payload)

    def stop_dispense(self, device_id: str) -> dict[str, Any]:
        """Stop dispensing water from the faucet."""
        payload = {
            "commandSrc": "app",
            "action": "stop",
        }
        return self.send_command(device_id, payload)

    def dispense_preset(self, device_id: str, preset_volume: int) -> dict[str, Any]:
        """Dispense a preset volume of water."""
        return self.start_dispense(device_id, preset_volume)

    def get_devices(self) -> list[dict[str, Any]]:
        """Get cached devices or fetch from API."""
        if self._devices is None:
            self.list_devices()
        return self._devices or []
