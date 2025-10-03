"""Valve platform for Moen Smart Water integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.valve import ValveEntity, ValveEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import MoenDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Moen Smart Water valve entities."""
    coordinator: MoenDataUpdateCoordinator = hass.data["moen_smart_water"][
        config_entry.entry_id
    ]

    # Get devices and create entities for each
    devices = coordinator.get_all_devices()
    _LOGGER.info(
        "Setting up valve entities. Found %d devices: %s",
        len(devices),
        list(devices.keys()),
    )

    entities = []
    for device_id, device in devices.items():
        device_name = device.get("name", f"Moen Smart Water {device_id}")
        _LOGGER.info("Creating valve entity for device %s: %s", device_id, device_name)
        entities.append(MoenFaucetValve(coordinator, device_id, device_name))

    _LOGGER.info("Adding %d valve entities", len(entities))
    async_add_entities(entities)


class MoenFaucetValve(CoordinatorEntity, ValveEntity):
    """Valve entity for Moen Smart Water water control."""

    def __init__(
        self, coordinator: MoenDataUpdateCoordinator, device_id: str, device_name: str
    ) -> None:
        """Initialize the valve entity."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_name = device_name
        self._attr_unique_id = f"{device_id}_valve"
        self._attr_name = "Water Control"
        self._attr_has_entity_name = True

        # Valve features
        self._attr_supported_features = (
            ValveEntityFeature.OPEN | ValveEntityFeature.CLOSE
        )

        # Valve state
        self._attr_is_closed = True
        self._attr_is_opening = False
        self._attr_is_closing = False
        self._attr_valve_position = 0  # 0-100 for flow rate
        self._attr_reports_position = True  # Required for valve entities

        # Device class for better UI representation
        self._attr_device_class = "water"

        # Track previous state for stopped detection
        self._previous_is_closed = True

        # Additional attributes for temperature and status
        self._attr_temperature = 20.0
        self._attr_preset_mode = "coldest"
        self._attr_extra_state_attributes = {}

        # Device information
        self._attr_device_info = DeviceInfo(
            identifiers={("moen_smart_water", device_id)},
            name=device_name,
            manufacturer="Moen",
            model="Smart Faucet",
        )

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        shadow = self.coordinator.get_device_shadow(self._device_id)
        if shadow:
            state = shadow.get("state", {}).get("reported", {})

            # Update valve state based on command
            command = state.get("command", "stop")
            if command == "run":
                # Valve is running - check if it was previously closed to determine opening state
                if self._previous_is_closed:
                    self._attr_is_opening = True
                    self._attr_is_closing = False
                else:
                    self._attr_is_opening = False
                    self._attr_is_closing = False
                self._attr_is_closed = False
            elif command == "stop":
                # Valve stopped - check if it was previously opening/closing to determine stopped state
                if self._attr_is_opening or self._attr_is_closing:
                    # Valve was in motion and now stopped - this is "stopped" state
                    # In Home Assistant, "stopped" means neither fully open nor fully closed
                    self._attr_is_closed = False
                    self._attr_is_opening = False
                    self._attr_is_closing = False
                else:
                    # Valve was idle and now stopped - this is "closed" state
                    self._attr_is_closed = True
                    self._attr_is_opening = False
                    self._attr_is_closing = False

            # Update previous state for next comparison
            self._previous_is_closed = self._attr_is_closed

            # Update valve position (flow rate)
            self._attr_valve_position = state.get("flowRate", 0)

            # Update temperature
            self._attr_temperature = state.get("temperature", 20.0)

            # Update extra state attributes
            self._attr_extra_state_attributes.update(
                {
                    "last_dispense_volume": state.get("lastDispenseVolume", 0),
                    "command": command,
                    "flow_rate": self._attr_valve_position,
                    "temperature": self._attr_temperature,
                }
            )

        self.async_write_ha_state()

    async def async_open_valve(self, **kwargs: Any) -> None:
        """Open the valve (start water flow)."""
        try:
            # Set opening state before API call
            self._attr_is_opening = True
            self._attr_is_closing = False
            self._attr_is_closed = False
            self.async_write_ha_state()

            await self.hass.async_add_executor_job(
                self.coordinator.api.start_water_flow,
                self._device_id,
                self._attr_preset_mode,
                int(self._attr_valve_position),
            )

            # After successful API call, valve is now open
            self._attr_is_opening = False
            self._attr_is_closed = False
            self._previous_is_closed = False
            _LOGGER.info("Opened valve for device %s", self._device_id)
        except Exception as err:
            # Reset state on error
            self._attr_is_opening = False
            self._attr_is_closed = True
            _LOGGER.error(
                "Failed to open valve for device %s: %s", self._device_id, err
            )

    async def async_close_valve(self, **kwargs: Any) -> None:
        """Close the valve (stop water flow)."""
        try:
            # Set closing state before API call
            self._attr_is_closing = True
            self._attr_is_opening = False
            self._attr_is_closed = False
            self.async_write_ha_state()

            await self.hass.async_add_executor_job(
                self.coordinator.api.stop_water_flow, self._device_id
            )

            # After successful API call, valve is now closed
            self._attr_is_closing = False
            self._attr_is_closed = True
            self._previous_is_closed = True
            _LOGGER.info("Closed valve for device %s", self._device_id)
        except Exception as err:
            # Reset state on error
            self._attr_is_closing = False
            self._attr_is_closed = True
            _LOGGER.error(
                "Failed to close valve for device %s: %s", self._device_id, err
            )

    async def async_stop_valve(self, **kwargs: Any) -> None:
        """Stop the valve (same as close for faucet)."""
        await self.async_close_valve(**kwargs)

    async def async_toggle(self) -> None:
        """Toggle the valve open/closed."""
        if self._attr_is_closed:
            await self.async_open_valve()
        else:
            await self.async_close_valve()

    async def async_set_valve_position(self, position: float) -> None:
        """Set the valve position (flow rate 0-100)."""
        try:
            # Update flow rate
            await self.hass.async_add_executor_job(
                self.coordinator.api.set_flow_rate, self._device_id, int(position)
            )
            self._attr_valve_position = position
            _LOGGER.info(
                "Set valve position to %d%% for device %s",
                int(position),
                self._device_id,
            )
        except Exception as err:
            _LOGGER.error(
                "Failed to set valve position for device %s: %s", self._device_id, err
            )

    async def async_set_temperature(self, temperature: float) -> None:
        """Set the water temperature."""
        try:
            await self.hass.async_add_executor_job(
                self.coordinator.api.set_specific_temperature,
                self._device_id,
                temperature,
                int(self._attr_valve_position),
            )
            self._attr_temperature = temperature
            _LOGGER.info(
                "Set temperature to %.1f°C for device %s", temperature, self._device_id
            )
        except Exception as err:
            _LOGGER.error(
                "Failed to set temperature for device %s: %s", self._device_id, err
            )

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the temperature preset mode."""
        try:
            # Map preset modes to API calls
            if preset_mode == "coldest":
                await self.hass.async_add_executor_job(
                    self.coordinator.api.set_coldest,
                    self._device_id,
                    int(self._attr_valve_position),
                )
            elif preset_mode == "hottest":
                await self.hass.async_add_executor_job(
                    self.coordinator.api.set_hottest,
                    self._device_id,
                    int(self._attr_valve_position),
                )
            elif preset_mode == "warm":
                await self.hass.async_add_executor_job(
                    self.coordinator.api.set_warm,
                    self._device_id,
                    int(self._attr_valve_position),
                )

            self._attr_preset_mode = preset_mode
            _LOGGER.info(
                "Set preset mode to %s for device %s", preset_mode, self._device_id
            )
        except Exception as err:
            _LOGGER.error(
                "Failed to set preset mode for device %s: %s", self._device_id, err
            )

    @property
    def preset_modes(self) -> list[str]:
        """Return the available preset modes."""
        return ["coldest", "cold", "warm", "hot", "hottest"]

    @property
    def current_option(self) -> str:
        """Return the current preset mode."""
        return self._attr_preset_mode
