"""Tests for the Moen coordinator module."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from custom_components.moen_smart_water.coordinator import MoenDataUpdateCoordinator


class TestMoenDataUpdateCoordinator:
    """Test cases for MoenDataUpdateCoordinator class."""

    def test_init(self, hass: HomeAssistant, config_entry: ConfigEntry):
        """Test coordinator initialization."""
        with patch("custom_components.moen_smart_water.coordinator.MoenAPI") as mock_api_class:
            coordinator = MoenDataUpdateCoordinator(hass, config_entry)

            assert coordinator.hass == hass
            assert coordinator.config_entry == config_entry
            assert coordinator.api is not None
            mock_api_class.assert_called_once_with(
                "test@example.com",
                "test_password",
                "test_client_id",
                "test_client_secret"
            )

    @pytest.mark.asyncio
    async def test_async_setup_success(self, coordinator: MoenDataUpdateCoordinator):
        """Test successful coordinator setup."""
        coordinator.api.authenticate = AsyncMock(return_value=True)
        coordinator.api.get_devices = MagicMock(return_value=[
            {"device_id": "device_123", "name": "Test Faucet"}
        ])

        result = await coordinator.async_setup()

        assert result is True
        coordinator.api.authenticate.assert_called_once()
        coordinator.api.get_devices.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_setup_auth_failure(self, coordinator: MoenDataUpdateCoordinator):
        """Test coordinator setup with authentication failure."""
        coordinator.api.authenticate = AsyncMock(return_value=False)

        result = await coordinator.async_setup()

        assert result is False
        coordinator.api.authenticate.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_update_data_success(self, coordinator: MoenDataUpdateCoordinator, sample_device_data: dict):
        """Test successful data update."""
        coordinator.api.get_devices = MagicMock(return_value=[sample_device_data])
        coordinator.api.get_device_shadow = MagicMock(return_value=sample_device_data["shadow"])

        result = await coordinator._async_update_data()

        assert "device_123" in result
        assert result["device_123"]["name"] == "Test Faucet"
        assert result["device_123"]["shadow"]["state"]["desired"]["temperature"] == 25.0

    @pytest.mark.asyncio
    async def test_async_update_data_no_devices(self, coordinator: MoenDataUpdateCoordinator):
        """Test data update with no devices."""
        coordinator.api.get_devices = MagicMock(return_value=[])

        result = await coordinator._async_update_data()

        assert result == {}

    @pytest.mark.asyncio
    async def test_async_update_data_exception(self, coordinator: MoenDataUpdateCoordinator):
        """Test data update with exception."""
        coordinator.api.get_devices = MagicMock(side_effect=Exception("API Error"))

        result = await coordinator._async_update_data()

        assert result == {}

    def test_get_all_devices(self, coordinator: MoenDataUpdateCoordinator, sample_device_data: dict):
        """Test getting all devices."""
        coordinator.data = {"device_123": sample_device_data}

        devices = coordinator.get_all_devices()

        assert "device_123" in devices
        assert devices["device_123"]["name"] == "Test Faucet"

    def test_get_all_devices_empty(self, coordinator: MoenDataUpdateCoordinator):
        """Test getting all devices when data is empty."""
        coordinator.data = {}

        devices = coordinator.get_all_devices()

        assert devices == {}

    def test_get_device_shadow(self, coordinator: MoenDataUpdateCoordinator, sample_device_data: dict):
        """Test getting device shadow."""
        coordinator.data = {"device_123": sample_device_data}

        shadow = coordinator.get_device_shadow("device_123")

        assert shadow["state"]["desired"]["temperature"] == 25.0
        assert shadow["state"]["reported"]["flow_rate"] == 50

    def test_get_device_shadow_not_found(self, coordinator: MoenDataUpdateCoordinator):
        """Test getting device shadow for non-existent device."""
        coordinator.data = {}

        shadow = coordinator.get_device_shadow("nonexistent_device")

        assert shadow is None

    def test_get_device_shadow_none_data(self, coordinator: MoenDataUpdateCoordinator):
        """Test getting device shadow when data is None."""
        coordinator.data = None

        shadow = coordinator.get_device_shadow("device_123")

        assert shadow is None
