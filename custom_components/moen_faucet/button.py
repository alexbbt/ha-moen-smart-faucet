"""Button platform for Moen Faucet integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import MoenClient

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Moen Faucet button entities."""
    client: MoenClient = hass.data["moen_faucet"][config_entry.entry_id]

    # Get devices and create entities for each
    devices = await hass.async_add_executor_job(client.get_devices)

    entities = []
    for device in devices:
        device_id = device.get("id", device.get("device_id"))
        device_name = device.get("name", f"Moen Faucet {device_id}")

        entities.extend([
            MoenStartDispenseButton(client, device_id, device_name),
            MoenStopDispenseButton(client, device_id, device_name),
            MoenPreset1Button(client, device_id, device_name, 250),
            MoenPreset2Button(client, device_id, device_name, 500),
            MoenPreset3Button(client, device_id, device_name, 750),
        ])

    async_add_entities(entities)


class MoenButtonBase(ButtonEntity):
    """Base class for Moen button entities."""

    def __init__(self, client: MoenClient, device_id: str, device_name: str) -> None:
        """Initialize the button."""
        self._client = client
        self._device_id = device_id
        self._device_name = device_name
        self._attr_has_entity_name = True

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {("moen_faucet", self._device_id)},
            "name": self._device_name,
            "manufacturer": "Moen",
            "model": "Smart Faucet",
        }


class MoenStartDispenseButton(MoenButtonBase):
    """Button to start dispensing water."""

    def __init__(self, client: MoenClient, device_id: str, device_name: str) -> None:
        """Initialize the start dispense button."""
        super().__init__(client, device_id, device_name)
        self._attr_unique_id = f"{device_id}_start_dispense"
        self._attr_name = "Start Dispense"

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.hass.async_add_executor_job(
                self._client.start_dispense, self._device_id
            )
            _LOGGER.info("Started dispensing on device %s", self._device_id)
        except Exception as err:
            _LOGGER.error("Failed to start dispensing on device %s: %s", self._device_id, err)


class MoenStopDispenseButton(MoenButtonBase):
    """Button to stop dispensing water."""

    def __init__(self, client: MoenClient, device_id: str, device_name: str) -> None:
        """Initialize the stop dispense button."""
        super().__init__(client, device_id, device_name)
        self._attr_unique_id = f"{device_id}_stop_dispense"
        self._attr_name = "Stop Dispense"

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.hass.async_add_executor_job(
                self._client.stop_dispense, self._device_id
            )
            _LOGGER.info("Stopped dispensing on device %s", self._device_id)
        except Exception as err:
            _LOGGER.error("Failed to stop dispensing on device %s: %s", self._device_id, err)


class MoenPresetButton(MoenButtonBase):
    """Button for preset dispense volumes."""

    def __init__(
        self,
        client: MoenClient,
        device_id: str,
        device_name: str,
        volume_ml: int,
        preset_number: int
    ) -> None:
        """Initialize the preset button."""
        super().__init__(client, device_id, device_name)
        self._volume_ml = volume_ml
        self._preset_number = preset_number
        self._attr_unique_id = f"{device_id}_preset_{preset_number}"
        self._attr_name = f"Preset {preset_number} ({volume_ml}ml)"

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.hass.async_add_executor_job(
                self._client.dispense_preset, self._device_id, self._volume_ml
            )
            _LOGGER.info(
                "Dispensed preset %d (%dml) on device %s",
                self._preset_number, self._volume_ml, self._device_id
            )
        except Exception as err:
            _LOGGER.error(
                "Failed to dispense preset %d on device %s: %s",
                self._preset_number, self._device_id, err
            )


class MoenPreset1Button(MoenPresetButton):
    """Button for preset 1 (250ml)."""
    def __init__(self, client: MoenClient, device_id: str, device_name: str) -> None:
        super().__init__(client, device_id, device_name, 250, 1)


class MoenPreset2Button(MoenPresetButton):
    """Button for preset 2 (500ml)."""
    def __init__(self, client: MoenClient, device_id: str, device_name: str) -> None:
        super().__init__(client, device_id, device_name, 500, 2)


class MoenPreset3Button(MoenPresetButton):
    """Button for preset 3 (750ml)."""
    def __init__(self, client: MoenClient, device_id: str, device_name: str) -> None:
        super().__init__(client, device_id, device_name, 750, 3)
