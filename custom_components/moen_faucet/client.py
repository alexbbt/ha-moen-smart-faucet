"""Client for Moen Smart Faucet API."""
from __future__ import annotations

import logging
import time
from typing import Any

import requests

_LOGGER = logging.getLogger(__name__)

# API endpoints - these will need to be updated with actual values from network capture
# Primary endpoint from network capture
API_BASE = "https://exo9f857n8.execute-api.us-east-2.amazonaws.com/prod"

# Alternative endpoints that might work
ALTERNATIVE_ENDPOINTS = [
    "https://exo9f857n8.execute-api.us-east-2.amazonaws.com",
    "https://api.moen.com",
    "https://api.ubymoen.com",
]


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
        payload = {
            "client_id": self.client_id,
            "username": self.username,
            "password": self.password,
        }
        
        login_url = f"{base_url}/auth/login"
        _LOGGER.debug("Attempting login to %s with client_id: %s", login_url, self.client_id)
        
        response = self.session.post(login_url, json=payload, timeout=30)
        
        # Log response details for debugging
        _LOGGER.debug("Login response status: %s", response.status_code)
        _LOGGER.debug("Login response headers: %s", dict(response.headers))
        
        if response.status_code == 403:
            _LOGGER.warning("403 Forbidden for endpoint: %s", login_url)
            return None
            
        response.raise_for_status()
        data = response.json()
        
        self.token = data["access_token"]
        # Set expiry with 60 second buffer
        self.expiry = time.time() + data.get("expires_in", 3600) - 60
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        
        _LOGGER.info("Successfully logged in to Moen API at %s", base_url)
        return data

    def login(self) -> dict[str, Any]:
        """Login to the Moen API and get access token."""
        # Try primary endpoint first
        try:
            return self._try_login_endpoint(API_BASE)
        except requests.exceptions.RequestException as err:
            _LOGGER.warning("Primary endpoint failed: %s", err)
            
        # Try alternative endpoints
        for endpoint in ALTERNATIVE_ENDPOINTS:
            try:
                _LOGGER.info("Trying alternative endpoint: %s", endpoint)
                result = self._try_login_endpoint(endpoint)
                if result:
                    return result
            except requests.exceptions.RequestException as err:
                _LOGGER.warning("Alternative endpoint %s failed: %s", endpoint, err)
                continue
        
        # If all endpoints fail, raise the original error
        _LOGGER.error("All API endpoints failed. This usually means:")
        _LOGGER.error("1. The API endpoints are incorrect")
        _LOGGER.error("2. The client_id is not valid")
        _LOGGER.error("3. The API structure has changed")
        _LOGGER.error("4. Your credentials are incorrect")
        _LOGGER.error("Current client_id: %s", self.client_id)
        _LOGGER.error("Tried endpoints: %s", [API_BASE] + ALTERNATIVE_ENDPOINTS)
        
        raise requests.exceptions.RequestException("All API endpoints failed")

    def ensure_auth(self) -> None:
        """Ensure we have a valid authentication token."""
        if not self.token or time.time() > self.expiry:
            _LOGGER.info("Token expired or missing, re-authenticating")
            self.login()

    def list_devices(self) -> list[dict[str, Any]]:
        """Get list of devices from the API."""
        self.ensure_auth()

        try:
            response = self.session.get(f"{API_BASE}/devices", timeout=30)
            response.raise_for_status()
            devices = response.json()

            # Cache devices for later use
            self._devices = devices
            _LOGGER.info("Retrieved %d devices from Moen API", len(devices))
            return devices

        except requests.exceptions.RequestException as err:
            _LOGGER.error("Failed to get devices from Moen API: %s", err)
            raise

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
