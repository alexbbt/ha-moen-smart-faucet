"""Valve platform for Moen Smart Water integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.valve import (
    ValveEntity,
    ValveEntityDescription,
    ValveEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import MoenDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


VALVE_DESCRIPTIONS: list[ValveEntityDescription] = [
    ValveEntityDescription(
        key="water_control",
        name="Water Control",
        device_class="water",
    ),
]


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

        for description in VALVE_DESCRIPTIONS:
            entities.append(
                MoenFaucetValve(coordinator, device_id, device_name, description)
            )

    _LOGGER.info("Adding %d valve entities", len(entities))
    async_add_entities(entities)


class MoenFaucetValve(CoordinatorEntity, ValveEntity):
    """Valve entity for Moen Smart Water water control."""

    def __init__(
        self,
        coordinator: MoenDataUpdateCoordinator,
        device_id: str,
        device_name: str,
        description: ValveEntityDescription,
    ) -> None:
        """Initialize the valve entity."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_name = device_name
        self.entity_description = description
        self._attr_unique_id = f"{device_id}_{description.key}"
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

            # Simple state mapping: "run" = open, "stop" = closed
            if command == "run":
                self._attr_is_closed = False
                self._attr_is_opening = False
                self._attr_is_closing = False
            else:  # "stop" or any other command
                self._attr_is_closed = True
                self._attr_is_opening = False
                self._attr_is_closing = False

            # Update valve position (flow rate) - only when running
            if command == "run":
                self._attr_valve_position = state.get(
                    "flowRate", 50
                )  # Default to 50% if not specified
            else:
                self._attr_valve_position = 0

            # Update temperature
            self._attr_temperature = state.get("temperature", 20.0)

            # Update extra state attributes
            self._attr_extra_state_attributes.update(
                {
                    "last_dispense_volume": state.get(
                        "volume", 0
                    ),  # Use 'volume' field from API
                    "command": command,
                    "flow_rate": self._attr_valve_position,
                    "temperature": self._attr_temperature,
                    "faucet_state": "running" if command == "run" else "idle",
                }
            )

        self.async_write_ha_state()

    async def async_open_valve(self, **kwargs: Any) -> None:
        """Open the valve (start water flow)."""
        try:
            _LOGGER.info("Opening valve for device %s", self._device_id)

            # Call the API to start water flow
            await self.hass.async_add_executor_job(
                self.coordinator.api.start_water_flow,
                self._device_id,
                self._attr_preset_mode,
                int(self._attr_valve_position),
            )

            # Trigger coordinator update to refresh state
            await self.coordinator.async_request_refresh()
            _LOGGER.info("Successfully opened valve for device %s", self._device_id)

        except Exception as err:
            _LOGGER.error(
                "Failed to open valve for device %s: %s", self._device_id, err
            )
            raise

    async def async_close_valve(self, **kwargs: Any) -> None:
        """Close the valve (stop water flow)."""
        try:
            _LOGGER.info("Closing valve for device %s", self._device_id)

            # Call the API to stop water flow
            await self.hass.async_add_executor_job(
                self.coordinator.api.stop_water_flow, self._device_id
            )

            # Trigger coordinator update to refresh state
            await self.coordinator.async_request_refresh()
            _LOGGER.info("Successfully closed valve for device %s", self._device_id)

        except Exception as err:
            _LOGGER.error(
                "Failed to close valve for device %s: %s", self._device_id, err
            )
            raise

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
