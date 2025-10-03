"""DateTime platform for Moen Smart Water integration."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from homeassistant.components.datetime import DateTimeEntity, DateTimeEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import MoenDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


DATETIME_DESCRIPTIONS: list[DateTimeEntityDescription] = [
    DateTimeEntityDescription(
        key="last_update",
        name="Last Update",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:update",
    ),
    DateTimeEntityDescription(
        key="last_connect",
        name="Last Connect",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:clock-outline",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Moen Smart Water datetime entities from a config entry."""
    coordinator: MoenDataUpdateCoordinator = hass.data["moen_smart_water"][
        config_entry.entry_id
    ]

    entities = []

    devices = coordinator.get_all_devices()
    for device_id, device in devices.items():
        device_name = device.get("nickname", f"Moen Device {device_id}")

        for description in DATETIME_DESCRIPTIONS:
            entities.append(
                MoenDateTime(
                    coordinator,
                    device_id,
                    device_name,
                    description,
                )
            )

    _LOGGER.info("Adding %d datetime entities", len(entities))
    async_add_entities(entities)


class MoenDateTime(CoordinatorEntity, DateTimeEntity):
    """Moen datetime entity for timestamps."""

    def __init__(
        self,
        coordinator: MoenDataUpdateCoordinator,
        device_id: str,
        device_name: str,
        description: DateTimeEntityDescription,
    ) -> None:
        """Initialize the datetime entity."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_name = device_name
        self.entity_description = description
        self._attr_unique_id = f"{device_id}_{description.key}"
        self._attr_has_entity_name = True

        # Set initial value
        self._attr_native_value = None

        # Make datetime entities read-only (diagnostic entities)
        self._attr_entity_registry_visible_default = True
        self._attr_entity_registry_enabled_default = True

        # Device info
        self._attr_device_info = DeviceInfo(
            identifiers={("moen_smart_water", device_id)},
            name=device_name,
            manufacturer="Moen",
            model="Smart Faucet",
        )

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        shadow = self.coordinator.get_device_shadow(self._device_id)
        details = self.coordinator.get_device_details(self._device_id)

        if not shadow:
            self._attr_native_value = None
            self.async_write_ha_state()
            return

        if self.entity_description.key == "last_connect":
            if details:
                last_connect = details.get("lastConnect")
                if last_connect:
                    if isinstance(last_connect, str):
                        # Parse ISO string
                        try:
                            dt = datetime.fromisoformat(
                                last_connect.replace("Z", "+00:00")
                            )
                            self._attr_native_value = dt
                        except (ValueError, TypeError):
                            self._attr_native_value = None
                    else:
                        # Convert timestamp to datetime
                        try:
                            dt = datetime.fromtimestamp(last_connect / 1000)
                            # Assume UTC if no timezone info
                            if dt.tzinfo is None:
                                dt = dt.replace(tzinfo=timezone.utc)  # noqa: UP017
                            self._attr_native_value = dt
                        except (ValueError, TypeError):
                            self._attr_native_value = None
                else:
                    self._attr_native_value = None
            else:
                self._attr_native_value = None

        elif self.entity_description.key == "last_update":
            if self.coordinator.last_update_success:
                # Use current time as last update time
                self._attr_native_value = datetime.now(timezone.utc)  # noqa: UP017
            else:
                self._attr_native_value = None

        self.async_write_ha_state()

    async def async_set_value(self, value: datetime) -> None:
        """Set the datetime value - not supported for read-only diagnostic entities."""
        raise NotImplementedError("Datetime entities are read-only diagnostic entities")
