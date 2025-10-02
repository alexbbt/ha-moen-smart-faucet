"""Tests for the Moen services module."""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from custom_components.moen_smart_water.services import async_setup_services
from custom_components.moen_smart_water.coordinator import MoenDataUpdateCoordinator


class TestMoenServices:
    """Test cases for Moen services."""

    @pytest.mark.asyncio
    async def test_async_setup_services(self, hass: HomeAssistant):
        """Test service setup."""
        with patch("custom_components.moen_smart_water.services.hass.services.async_register") as mock_register:
            await async_setup_services(hass)

            # Should register 6 services
            assert mock_register.call_count == 6

    @pytest.mark.asyncio
    async def test_dispense_water_service_success(self, hass: HomeAssistant, sample_device_data: dict):
        """Test successful water dispensing service."""
        # Setup mock coordinator
        mock_coordinator = MagicMock(spec=MoenDataUpdateCoordinator)
        mock_coordinator.get_all_devices.return_value = {"device_123": sample_device_data}
        mock_coordinator.api.start_water_flow = MagicMock(return_value=True)

        hass.data = {"moen_smart_water": {"test_entry": mock_coordinator}}

        # Setup service
        await async_setup_services(hass)

        # Create service call
        call = ServiceCall(
            "moen_smart_water",
            "dispense_water",
            {"device_id": "device_123", "volume_ml": 250, "timeout": 120}
        )

        # Get the service function
        service_func = hass.services.async_services()["moen_smart_water"]["dispense_water"]

        # Call service
        await service_func(call)

        # Verify API was called
        mock_coordinator.api.start_water_flow.assert_called_once_with("device_123", "coldest", 100)

    @pytest.mark.asyncio
    async def test_dispense_water_service_device_not_found(self, hass: HomeAssistant):
        """Test water dispensing service with device not found."""
        # Setup mock coordinator
        mock_coordinator = MagicMock(spec=MoenDataUpdateCoordinator)
        mock_coordinator.get_all_devices.return_value = {}

        hass.data = {"moen_smart_water": {"test_entry": mock_coordinator}}

        # Setup service
        await async_setup_services(hass)

        # Create service call
        call = ServiceCall(
            "moen_smart_water",
            "dispense_water",
            {"device_id": "nonexistent_device"}
        )

        # Get the service function
        service_func = hass.services.async_services()["moen_smart_water"]["dispense_water"]

        # Call service (should not raise exception)
        await service_func(call)

    @pytest.mark.asyncio
    async def test_stop_dispensing_service_success(self, hass: HomeAssistant, sample_device_data: dict):
        """Test successful stop dispensing service."""
        # Setup mock coordinator
        mock_coordinator = MagicMock(spec=MoenDataUpdateCoordinator)
        mock_coordinator.get_all_devices.return_value = {"device_123": sample_device_data}
        mock_coordinator.api.stop_water_flow = MagicMock(return_value=True)

        hass.data = {"moen_smart_water": {"test_entry": mock_coordinator}}

        # Setup service
        await async_setup_services(hass)

        # Create service call
        call = ServiceCall(
            "moen_smart_water",
            "stop_dispensing",
            {"device_id": "device_123"}
        )

        # Get the service function
        service_func = hass.services.async_services()["moen_smart_water"]["stop_dispensing"]

        # Call service
        await service_func(call)

        # Verify API was called
        mock_coordinator.api.stop_water_flow.assert_called_once_with("device_123")

    @pytest.mark.asyncio
    async def test_get_device_status_service_success(self, hass: HomeAssistant, sample_device_data: dict):
        """Test successful get device status service."""
        # Setup mock coordinator
        mock_coordinator = MagicMock(spec=MoenDataUpdateCoordinator)
        mock_coordinator.get_all_devices.return_value = {"device_123": sample_device_data}
        mock_coordinator.get_device_shadow.return_value = sample_device_data["shadow"]

        hass.data = {"moen_smart_water": {"test_entry": mock_coordinator}}

        # Setup service
        await async_setup_services(hass)

        # Create service call
        call = ServiceCall(
            "moen_smart_water",
            "get_device_status",
            {"device_id": "device_123"}
        )

        # Get the service function
        service_func = hass.services.async_services()["moen_smart_water"]["get_device_status"]

        # Call service
        await service_func(call)

        # Verify coordinator method was called
        mock_coordinator.get_device_shadow.assert_called_once_with("device_123")

    @pytest.mark.asyncio
    async def test_get_user_profile_service_success(self, hass: HomeAssistant):
        """Test successful get user profile service."""
        # Setup mock coordinator
        mock_coordinator = MagicMock(spec=MoenDataUpdateCoordinator)
        mock_coordinator.api.get_user_profile = MagicMock(return_value={"user_id": "test_user"})

        hass.data = {"moen_smart_water": {"test_entry": mock_coordinator}}

        # Setup service
        await async_setup_services(hass)

        # Create service call
        call = ServiceCall("moen_smart_water", "get_user_profile", {})

        # Get the service function
        service_func = hass.services.async_services()["moen_smart_water"]["get_user_profile"]

        # Call service
        await service_func(call)

        # Verify API was called
        mock_coordinator.api.get_user_profile.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_temperature_service_success(self, hass: HomeAssistant, sample_device_data: dict):
        """Test successful set temperature service."""
        # Setup mock coordinator
        mock_coordinator = MagicMock(spec=MoenDataUpdateCoordinator)
        mock_coordinator.get_all_devices.return_value = {"device_123": sample_device_data}
        mock_coordinator.api.set_specific_temperature = MagicMock(return_value=True)

        hass.data = {"moen_smart_water": {"test_entry": mock_coordinator}}

        # Setup service
        await async_setup_services(hass)

        # Create service call
        call = ServiceCall(
            "moen_smart_water",
            "set_temperature",
            {"device_id": "device_123", "temperature": 30.0, "flow_rate": 75}
        )

        # Get the service function
        service_func = hass.services.async_services()["moen_smart_water"]["set_temperature"]

        # Call service
        await service_func(call)

        # Verify API was called
        mock_coordinator.api.set_specific_temperature.assert_called_once_with("device_123", 30.0, 75)

    @pytest.mark.asyncio
    async def test_set_flow_rate_service_success(self, hass: HomeAssistant, sample_device_data: dict):
        """Test successful set flow rate service."""
        # Setup mock coordinator
        mock_coordinator = MagicMock(spec=MoenDataUpdateCoordinator)
        mock_coordinator.get_all_devices.return_value = {"device_123": sample_device_data}
        mock_coordinator.api.set_flow_rate = MagicMock(return_value=True)

        hass.data = {"moen_smart_water": {"test_entry": mock_coordinator}}

        # Setup service
        await async_setup_services(hass)

        # Create service call
        call = ServiceCall(
            "moen_smart_water",
            "set_flow_rate",
            {"device_id": "device_123", "flow_rate": 80}
        )

        # Get the service function
        service_func = hass.services.async_services()["moen_smart_water"]["set_flow_rate"]

        # Call service
        await service_func(call)

        # Verify API was called
        mock_coordinator.api.set_flow_rate.assert_called_once_with("device_123", 80)
