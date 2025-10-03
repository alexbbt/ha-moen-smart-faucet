"""Button platform for Moen Smart Water integration."""

from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import MoenDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Button descriptions
START_WATER_BUTTON = ButtonEntityDescription(
    key="start_water",
    name="Start Water",
    icon="mdi:play",
)

STOP_WATER_BUTTON = ButtonEntityDescription(
    key="stop_water",
    name="Stop Water",
    icon="mdi:stop",
)

COLDEST_BUTTON = ButtonEntityDescription(
    key="coldest",
    name="Coldest",
    icon="mdi:snowflake",
)

WARM_BUTTON = ButtonEntityDescription(
    key="warm",
    name="Warm",
    icon="mdi:thermometer-lines",
)

HOTTEST_BUTTON = ButtonEntityDescription(
    key="hottest",
    name="Hottest",
    icon="mdi:fire",
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Moen Smart Water button entities."""
    coordinator: MoenDataUpdateCoordinator = hass.data["moen_smart_water"][
        config_entry.entry_id
    ]

    # Get devices and create entities for each
    devices = coordinator.get_all_devices()
    _LOGGER.info(
        "Setting up button entities. Found %d devices: %s",
        len(devices),
        list(devices.keys()),
    )

    entities = []
    for device_id, device in devices.items():
        device_name = device.get("name", f"Moen Smart Water {device_id}")
        _LOGGER.info(
            "Creating button entities for device %s: %s", device_id, device_name
        )

        entities.extend(
            [
                MoenButton(coordinator, device_id, device_name, START_WATER_BUTTON),
                MoenButton(coordinator, device_id, device_name, STOP_WATER_BUTTON),
                MoenButton(coordinator, device_id, device_name, COLDEST_BUTTON),
                MoenButton(coordinator, device_id, device_name, WARM_BUTTON),
                MoenButton(coordinator, device_id, device_name, HOTTEST_BUTTON),
            ]
        )

    _LOGGER.info("Adding %d button entities", len(entities))
    async_add_entities(entities)


class MoenButton(CoordinatorEntity, ButtonEntity):
    """Generic Moen button entity using ButtonEntityDescription."""

    def __init__(
        self,
        coordinator: MoenDataUpdateCoordinator,
        device_id: str,
        device_name: str,
        description: ButtonEntityDescription,
    ) -> None:
        """Initialize the button entity."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_name = device_name
        self.entity_description = description
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{device_id}_{description.key}"

        # Device information
        self._attr_device_info = DeviceInfo(
            identifiers={("moen_smart_water", device_id)},
            name=device_name,
            manufacturer="Moen",
            model="Smart Faucet",
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        key = self.entity_description.key

        try:
            if key == "start_water":
                await self.hass.async_add_executor_job(
                    self.coordinator.api.start_water_flow,
                    self._device_id,
                    "coldest",  # Default to coldest temperature
                    100,  # Default to full flow rate
                )
                _LOGGER.info("Started water flow for device %s", self._device_id)

            elif key == "stop_water":
                await self.hass.async_add_executor_job(
                    self.coordinator.api.stop_water_flow, self._device_id
                )
                _LOGGER.info("Stopped water flow for device %s", self._device_id)

            elif key == "coldest":
                await self.hass.async_add_executor_job(
                    self.coordinator.api.set_coldest,
                    self._device_id,
                    100,  # Full flow rate
                )
                _LOGGER.info("Set coldest temperature for device %s", self._device_id)

            elif key == "warm":
                await self.hass.async_add_executor_job(
                    self.coordinator.api.set_warm,
                    self._device_id,
                    100,  # Full flow rate
                )
                _LOGGER.info("Set warm temperature for device %s", self._device_id)

            elif key == "hottest":
                await self.hass.async_add_executor_job(
                    self.coordinator.api.set_hottest,
                    self._device_id,
                    100,  # Full flow rate
                )
                _LOGGER.info("Set hottest temperature for device %s", self._device_id)

        except Exception as err:
            _LOGGER.error(
                "Failed to execute %s action for device %s: %s",
                key,
                self._device_id,
                err,
            )
