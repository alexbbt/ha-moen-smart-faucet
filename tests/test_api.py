"""Tests for the Moen API module."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import requests
from requests.exceptions import RequestException

from custom_components.moen_smart_water.api import MoenAPI


class TestMoenAPI:
    """Test cases for MoenAPI class."""

    def test_init(self):
        """Test API initialization."""
        api = MoenAPI("test@example.com", "password", "client_id", "client_secret")

        assert api.username == "test@example.com"
        assert api.password == "password"
        assert api.client_id == "client_id"
        assert api.client_secret == "client_secret"
        assert api.access_token is None
        assert api.refresh_token is None

    @patch("requests.post")
    def test_authenticate_success(self, mock_post):
        """Test successful authentication."""
        # Mock successful authentication response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600
        }
        mock_post.return_value = mock_response

        api = MoenAPI("test@example.com", "password", "client_id", "client_secret")
        result = api.authenticate()

        assert result is True
        assert api.access_token == "test_access_token"
        assert api.refresh_token == "test_refresh_token"
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_authenticate_failure(self, mock_post):
        """Test authentication failure."""
        # Mock failed authentication response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "invalid_credentials"}
        mock_post.return_value = mock_response

        api = MoenAPI("test@example.com", "password", "client_id", "client_secret")
        result = api.authenticate()

        assert result is False
        assert api.access_token is None
        assert api.refresh_token is None

    @patch("requests.post")
    def test_authenticate_request_exception(self, mock_post):
        """Test authentication with request exception."""
        mock_post.side_effect = RequestException("Network error")

        api = MoenAPI("test@example.com", "password", "client_id", "client_secret")
        result = api.authenticate()

        assert result is False

    @patch("requests.get")
    def test_get_user_profile_success(self, mock_get):
        """Test successful user profile retrieval."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "user_id": "test_user_123",
            "email": "test@example.com",
            "name": "Test User"
        }
        mock_get.return_value = mock_response

        api = MoenAPI("test@example.com", "password", "client_id", "client_secret")
        api.access_token = "test_access_token"

        result = api.get_user_profile()

        assert result == {
            "user_id": "test_user_123",
            "email": "test@example.com",
            "name": "Test User"
        }
        mock_get.assert_called_once()

    @patch("requests.get")
    def test_get_devices_success(self, mock_get):
        """Test successful devices retrieval."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "devices": [
                {
                    "device_id": "device_123",
                    "name": "Kitchen Faucet",
                    "model": "Moen Smart Faucet"
                }
            ]
        }
        mock_get.return_value = mock_response

        api = MoenAPI("test@example.com", "password", "client_id", "client_secret")
        api.access_token = "test_access_token"

        result = api.get_devices()

        assert len(result) == 1
        assert result[0]["device_id"] == "device_123"
        assert result[0]["name"] == "Kitchen Faucet"

    @patch("requests.get")
    def test_get_device_shadow_success(self, mock_get):
        """Test successful device shadow retrieval."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "state": {
                "desired": {"temperature": 25.0, "flow_rate": 50},
                "reported": {"temperature": 25.0, "flow_rate": 50}
            }
        }
        mock_get.return_value = mock_response

        api = MoenAPI("test@example.com", "password", "client_id", "client_secret")
        api.access_token = "test_access_token"

        result = api.get_device_shadow("device_123")

        assert result["state"]["desired"]["temperature"] == 25.0
        assert result["state"]["reported"]["flow_rate"] == 50

    @patch("requests.post")
    def test_start_water_flow_success(self, mock_post):
        """Test successful water flow start."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response

        api = MoenAPI("test@example.com", "password", "client_id", "client_secret")
        api.access_token = "test_access_token"

        result = api.start_water_flow("device_123", "coldest", 100)

        assert result is True
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_stop_water_flow_success(self, mock_post):
        """Test successful water flow stop."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response

        api = MoenAPI("test@example.com", "password", "client_id", "client_secret")
        api.access_token = "test_access_token"

        result = api.stop_water_flow("device_123")

        assert result is True
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_set_specific_temperature_success(self, mock_post):
        """Test successful temperature setting."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response

        api = MoenAPI("test@example.com", "password", "client_id", "client_secret")
        api.access_token = "test_access_token"

        result = api.set_specific_temperature("device_123", 30.0, 75)

        assert result is True
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_set_flow_rate_success(self, mock_post):
        """Test successful flow rate setting."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response

        api = MoenAPI("test@example.com", "password", "client_id", "client_secret")
        api.access_token = "test_access_token"

        result = api.set_flow_rate("device_123", 80)

        assert result is True
        mock_post.assert_called_once()
