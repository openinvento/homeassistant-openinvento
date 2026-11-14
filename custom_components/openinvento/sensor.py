#!/usr/bin/env python3
"""Sensors for OpenInvento inventory statistics."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .data import OpenInventoConfigEntry

DESCRIPTIONS = (
    SensorEntityDescription(
        key="articles", name="Articles", icon="mdi:package-variant"
    ),
    SensorEntityDescription(key="areas", name="Areas", icon="mdi:map-marker"),
    SensorEntityDescription(key="low_stock", name="Low stock items", icon="mdi:alert"),
    SensorEntityDescription(
        key="entries", name="Inventory entries", icon="mdi:format-list-bulleted"
    ),
    SensorEntityDescription(
        key="inventories", name="Inventories", icon="mdi:warehouse"
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: OpenInventoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenInvento sensors."""
    async_add_entities(
        OpenInventoSensor(entry.runtime_data.coordinator, description)
        for description in DESCRIPTIONS
    )


class OpenInventoSensor(CoordinatorEntity, SensorEntity):
    """An OpenInvento summary sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.config_entry.entry_id)},
            "name": "OpenInvento",
            "manufacturer": "OpenInvento",
        }

    @property
    def native_value(self) -> int:
        """Return the statistic value."""
        return self.coordinator.data[self.entity_description.key]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the entries represented by this sensor."""
        attribute_key = {
            "inventories": "inventory_items",
            "entries": "entry_items",
            "articles": "article_items",
            "areas": "area_items",
            "low_stock": "low_stock_items",
        }[self.entity_description.key]
        return {"items": self.coordinator.data[attribute_key]}
