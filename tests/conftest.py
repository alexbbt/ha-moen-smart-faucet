"""Pytest configuration and fixtures for Moen Smart Water integration tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.moen_smart_water.api import MoenAPI
from custom_components.moen_smart_water.coordinator import MoenDataUpdateCoordinator


@pytest.fixture
async def hass() -> HomeAssistant:
    """Return a Home Assistant instance for testing."""
    hass_instance = HomeAssistant("")
    await hass_instance.async_start()
    yield hass_instance
    await hass_instance.async_stop()


@pytest.fixture
def config_entry() -> ConfigEntry:
    """Return a mock config entry for testing."""
    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test_entry_id"
    entry.data = {
        "username": "test@example.com",
        "password": "test_password",
    }
    return entry


@pytest.fixture
def mock_api() -> MagicMock:
    """Return a mock MoenAPI instance for testing."""
    api = MagicMock(spec=MoenAPI)
    api.authenticate = AsyncMock(return_value=True)
    api.get_user_profile = MagicMock(return_value={"user_id": "test_user"})
    api.get_devices = MagicMock(return_value=[])
    return api


@pytest.fixture
async def coordinator(
    hass: HomeAssistant, config_entry: ConfigEntry, mock_api: MagicMock
) -> MoenDataUpdateCoordinator:
    """Return a MoenDataUpdateCoordinator instance for testing."""
    with patch(
        "custom_components.moen_smart_water.coordinator.MoenAPI", return_value=mock_api
    ):
        coordinator = MoenDataUpdateCoordinator(hass, config_entry)
        return coordinator


@pytest.fixture
def sample_device_data() -> dict:
    """Return sample device data for testing."""
    return {
        "device_id": "test_device_123",
        "name": "Test Faucet",
        "model": "Moen Smart Faucet",
        "status": "online",
        "shadow": {
            "state": {
                "desired": {
                    "temperature": 25.0,
                    "flow_rate": 50,
                    "water_flowing": False,
                },
                "reported": {
                    "temperature": 25.0,
                    "flow_rate": 50,
                    "water_flowing": False,
                },
            }
        },
    }
