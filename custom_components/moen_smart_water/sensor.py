"""Sensor platform for Moen Smart Water integration."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import MoenDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Essential sensors
TEMPERATURE_SENSOR = SensorEntityDescription(
    key="temperature",
    name="Temperature",
    native_unit_of_measurement="°C",
    device_class=SensorDeviceClass.TEMPERATURE,
)

FLOW_RATE_SENSOR = SensorEntityDescription(
    key="flow_rate",
    name="Flow Rate",
    native_unit_of_measurement="%",
)

FAUCET_STATE_SENSOR = SensorEntityDescription(
    key="faucet_state",
    name="Faucet State",
)

LAST_DISPENSE_VOLUME_SENSOR = SensorEntityDescription(
    key="last_dispense_volume",
    name="Last Dispense Volume",
    native_unit_of_measurement="ml",
)

# Diagnostic sensors
API_STATUS_SENSOR = SensorEntityDescription(
    key="api_status",
    name="API Status",
    entity_category=EntityCategory.DIAGNOSTIC,
)

LAST_UPDATE_SENSOR = SensorEntityDescription(
    key="last_update",
    name="Last Update",
    entity_category=EntityCategory.DIAGNOSTIC,
)

WIFI_NETWORK_SENSOR = SensorEntityDescription(
    key="wifi_network",
    name="WiFi Network",
    entity_category=EntityCategory.DIAGNOSTIC,
)

WIFI_RSSI_SENSOR = SensorEntityDescription(
    key="wifi_rssi",
    name="WiFi Signal",
    native_unit_of_measurement="dBm",
    entity_category=EntityCategory.DIAGNOSTIC,
)

WIFI_CONNECTED_SENSOR = SensorEntityDescription(
    key="wifi_connected",
    name="WiFi Connected",
    entity_category=EntityCategory.DIAGNOSTIC,
)

BATTERY_SENSOR = SensorEntityDescription(
    key="battery_percentage",
    name="Battery",
    native_unit_of_measurement="%",
    device_class=SensorDeviceClass.BATTERY,
    entity_category=EntityCategory.DIAGNOSTIC,
)

POWER_SOURCE_SENSOR = SensorEntityDescription(
    key="power_source",
    name="Power Source",
    entity_category=EntityCategory.DIAGNOSTIC,
)

FIRMWARE_VERSION_SENSOR = SensorEntityDescription(
    key="firmware_version",
    name="Firmware Version",
    entity_category=EntityCategory.DIAGNOSTIC,
)

LAST_CONNECT_SENSOR = SensorEntityDescription(
    key="last_connect",
    name="Last Connect",
    entity_category=EntityCategory.DIAGNOSTIC,
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Moen Smart Water sensor entities."""
    coordinator: MoenDataUpdateCoordinator = hass.data["moen_smart_water"][
        config_entry.entry_id
    ]

    # Get devices and create entities for each
    devices = coordinator.get_all_devices()
    _LOGGER.info(
        "Setting up sensor entities. Found %d devices: %s",
        len(devices),
        list(devices.keys()),
    )

    entities = []
    for device_id, device in devices.items():
        device_name = device.get("name", f"Moen Smart Water {device_id}")
        _LOGGER.info(
            "Creating sensor entities for device %s: %s", device_id, device_name
        )

        # Essential sensors
        entities.extend(
            [
                MoenSensor(coordinator, device_id, device_name, FAUCET_STATE_SENSOR),
                MoenSensor(
                    coordinator, device_id, device_name, LAST_DISPENSE_VOLUME_SENSOR
                ),
                MoenSensor(coordinator, device_id, device_name, TEMPERATURE_SENSOR),
                MoenSensor(coordinator, device_id, device_name, FLOW_RATE_SENSOR),
            ]
        )

        # Diagnostic sensors
        entities.extend(
            [
                MoenSensor(coordinator, device_id, device_name, API_STATUS_SENSOR),
                MoenSensor(coordinator, device_id, device_name, LAST_UPDATE_SENSOR),
                MoenSensor(coordinator, device_id, device_name, WIFI_NETWORK_SENSOR),
                MoenSensor(coordinator, device_id, device_name, WIFI_RSSI_SENSOR),
                MoenSensor(coordinator, device_id, device_name, WIFI_CONNECTED_SENSOR),
                MoenSensor(coordinator, device_id, device_name, BATTERY_SENSOR),
                MoenSensor(coordinator, device_id, device_name, POWER_SOURCE_SENSOR),
                MoenSensor(
                    coordinator, device_id, device_name, FIRMWARE_VERSION_SENSOR
                ),
                MoenSensor(coordinator, device_id, device_name, LAST_CONNECT_SENSOR),
            ]
        )

    _LOGGER.info("Adding %d sensor entities", len(entities))
    async_add_entities(entities)


class MoenSensor(CoordinatorEntity, SensorEntity):
    """Generic Moen sensor entity using SensorEntityDescription."""

    def __init__(
        self,
        coordinator: MoenDataUpdateCoordinator,
        device_id: str,
        device_name: str,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_name = device_name
        self.entity_description = description
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{device_id}_{description.key}"

        # Device information
        self._attr_device_info = DeviceInfo(
            identifiers={("moen_smart_water", self._device_id)},
            name=self._device_name,
            manufacturer="Moen",
            model="Smart Faucet",
        )

        # Set initial value based on sensor type
        if description.key == "temperature":
            self._attr_native_value = 20.0
        elif description.key in ["flow_rate", "battery_percentage"]:
            self._attr_native_value = 0
        elif description.key == "last_dispense_volume":
            self._attr_native_value = 0
        else:
            self._attr_native_value = "unknown"

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        shadow = self.coordinator.get_device_shadow(self._device_id)
        details = self.coordinator.get_device_details(self._device_id)

        if not shadow:
            if self.entity_description.key == "api_status":
                self._attr_native_value = "no_data"
            elif self.entity_description.key == "last_update":
                self._attr_native_value = "failed"
            else:
                self._attr_native_value = "unknown"
            self.async_write_ha_state()
            return

        state = shadow.get("state", {}).get("reported", {})
        key = self.entity_description.key

        # Map sensor keys to shadow data fields
        if key == "faucet_state":
            if state.get("command") == "run":
                self._attr_native_value = "running"
            elif state.get("command") == "stop":
                self._attr_native_value = "stopped"
            else:
                self._attr_native_value = "idle"
        elif key == "last_dispense_volume":
            self._attr_native_value = state.get("lastDispenseVolume", 0)
        elif key == "temperature":
            self._attr_native_value = state.get("temperature", 20.0)
        elif key == "flow_rate":
            self._attr_native_value = state.get("flowRate", 0)
        elif key == "api_status":
            if self.coordinator.data:
                devices = self.coordinator.data.get("devices", {})
                device_shadows = self.coordinator.data.get("device_shadows", {})
                if self._device_id in devices and self._device_id in device_shadows:
                    self._attr_native_value = "connected"
                elif self._device_id in devices:
                    self._attr_native_value = "device_found_no_shadow"
                else:
                    self._attr_native_value = "device_not_found"
            else:
                self._attr_native_value = "no_data"
        elif key == "last_update":
            if self.coordinator.last_update_success:
                from datetime import datetime
                self._attr_native_value = datetime.now().isoformat()
            else:
                self._attr_native_value = "failed"
        elif key == "wifi_network":
            # Try device details first, then fall back to shadow
            if details:
                connectivity = details.get("connectivity", {})
                self._attr_native_value = connectivity.get(
                    "net", state.get("wifiNetwork", "unknown")
                )
            else:
                self._attr_native_value = state.get("wifiNetwork", "unknown")
        elif key == "wifi_rssi":
            # Try device details first, then fall back to shadow
            if details:
                connectivity = details.get("connectivity", {})
                rssi_value = connectivity.get("rssi")
                if rssi_value is not None:
                    self._attr_native_value = rssi_value
                else:
                    self._attr_native_value = state.get("wifiRssi")
            else:
                self._attr_native_value = state.get("wifiRssi")
        elif key == "wifi_connected":
            # Try device details first, then fall back to shadow
            if details:
                self._attr_native_value = (
                    "connected" if details.get("connected", False) else "disconnected"
                )
            else:
                self._attr_native_value = (
                    "connected" if state.get("connected", False) else "disconnected"
                )
        elif key == "battery_percentage":
            # Try device details first, then fall back to shadow
            if details:
                battery = details.get("battery", {})
                self._attr_native_value = battery.get(
                    "percentage", state.get("batteryPercentage", 100)
                )
            else:
                self._attr_native_value = state.get("batteryPercentage", 100)
        elif key == "power_source":
            # Try device details first, then fall back to shadow
            if details:
                battery = details.get("battery", {})
                self._attr_native_value = battery.get(
                    "source", state.get("powerSource", "unknown")
                )
            else:
                self._attr_native_value = state.get("powerSource", "unknown")
        elif key == "firmware_version":
            # Try device details first, then fall back to shadow
            if details:
                firmware = details.get("firmware", {})
                self._attr_native_value = firmware.get(
                    "version", state.get("firmwareVersion", "unknown")
                )
            else:
                self._attr_native_value = state.get("firmwareVersion", "unknown")
        elif key == "last_connect":
            # Try device details first, then fall back to shadow
            last_connect = None
            if details:
                last_connect = details.get("lastConnect")
            if not last_connect:
                last_connect = state.get("lastConnect")

            if last_connect:
                from datetime import datetime

                try:
                    dt = datetime.fromtimestamp(last_connect / 1000)
                    self._attr_native_value = dt.isoformat()
                except (ValueError, TypeError):
                    self._attr_native_value = "invalid_timestamp"
            else:
                self._attr_native_value = "never"

        self.async_write_ha_state()
