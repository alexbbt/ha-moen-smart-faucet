"""Tests for API structure and initialization."""

from __future__ import annotations

from custom_components.moen_smart_water.api import MoenAPI


class TestAPIStructure:
    """Test cases for API structure and initialization."""

    def test_api_init(self):
        """Test API initialization."""
        api = MoenAPI("test_client_id", "test@example.com", "password")

        assert api.username == "test@example.com"
        assert api.password == "password"
        assert api.client_id == "test_client_id"
        assert api.access_token is None
        assert api.refresh_token is None

    def test_api_session_headers(self):
        """Test API session headers are set correctly."""
        api = MoenAPI("test_client_id", "test@example.com", "password")

        assert "User-Agent" in api.session.headers
        assert api.session.headers["User-Agent"] == "Smartwater-iOS-prod-3.39.0"

    def test_api_cached_data_initialization(self):
        """Test API cached data is initialized correctly."""
        api = MoenAPI("test_client_id", "test@example.com", "password")

        assert api._user_profile is None
        assert api._locations is None
        assert api._devices is None
        assert api._temperature_definitions is None

    def test_api_methods_exist(self):
        """Test that API methods exist."""
        api = MoenAPI("test_client_id", "test@example.com", "password")

        # Check that key methods exist
        assert hasattr(api, "login")
        assert hasattr(api, "get_user_profile")
        assert hasattr(api, "list_devices")
        assert hasattr(api, "get_device_shadow")
        assert hasattr(api, "start_water_flow")
        assert hasattr(api, "stop_water_flow")
        assert hasattr(api, "set_specific_temperature")
        assert hasattr(api, "set_flow_rate")
