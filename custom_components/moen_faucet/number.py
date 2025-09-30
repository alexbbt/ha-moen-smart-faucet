"""Number platform for Moen Faucet integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity
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
    """Set up Moen Faucet number entities."""
    client: MoenClient = hass.data["moen_faucet"][config_entry.entry_id]

    # Get devices and create entities for each
    devices = await hass.async_add_executor_job(client.get_devices)

    entities = []
    for device in devices:
        device_id = device.get("id", device.get("device_id"))
        device_name = device.get("name", f"Moen Faucet {device_id}")

        entities.append(MoenTargetVolumeNumber(client, device_id, device_name))

    async_add_entities(entities)


class MoenNumberBase(NumberEntity):
    """Base class for Moen number entities."""

    def __init__(self, client: MoenClient, device_id: str, device_name: str) -> None:
        """Initialize the number entity."""
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


class MoenTargetVolumeNumber(MoenNumberBase):
    """Number entity for target dispense volume."""

    def __init__(self, client: MoenClient, device_id: str, device_name: str) -> None:
        """Initialize the target volume number entity."""
        super().__init__(client, device_id, device_name)
        self._attr_unique_id = f"{device_id}_target_volume"
        self._attr_name = "Target Volume"
        self._attr_native_min_value = 50
        self._attr_native_max_value = 2000
        self._attr_native_step = 50
        self._attr_native_unit_of_measurement = "ml"
        self._attr_native_value = 250  # Default value

    async def async_set_native_value(self, value: float) -> None:
        """Set the target volume."""
        volume_ml = int(value)
        self._attr_native_value = volume_ml
        _LOGGER.info("Set target volume to %dml for device %s", volume_ml, self._device_id)
