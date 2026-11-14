"""Home Assistant integration for OpenInvento."""  # noqa: EXE002

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_API_KEY,
    CONF_URL,
    CONF_VERIFY_SSL,
    DOMAIN,
    LOGGER,
    SERVICE_CREATE_ENTRY,
    SERVICE_DELETE_ENTRY,
    SERVICE_UPDATE_ENTRY,
)
from .data import OpenInventoRuntimeData
from .openinvento import OpenInventoApiClient

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall

    from .data import OpenInventoConfigEntry

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: OpenInventoConfigEntry) -> bool:
    """Set up OpenInvento from a config entry."""
    client = OpenInventoApiClient(
        base_url=entry.data[CONF_URL],
        api_key=entry.data[CONF_API_KEY],
        session=async_get_clientsession(hass),
        verify_ssl=entry.data.get(CONF_VERIFY_SSL, True),
    )
    coordinator = DataUpdateCoordinator(
        hass,
        LOGGER,
        name=DOMAIN,
        update_interval=timedelta(minutes=5),
        update_method=client.async_get_summary,
    )
    entry.runtime_data = OpenInventoRuntimeData(client=client, coordinator=coordinator)
    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def create_entry(call: ServiceCall) -> None:
        """Create an inventory entry."""
        await client.async_create_entry(dict(call.data))
        await coordinator.async_request_refresh()

    async def update_entry(call: ServiceCall) -> None:
        """Update an inventory entry."""
        data = dict(call.data)
        entry_uuid = data.pop("uuid")
        await client.async_update_entry(entry_uuid, data)
        await coordinator.async_request_refresh()

    async def delete_entry(call: ServiceCall) -> None:
        """Delete an inventory entry."""
        await client.async_delete_entry(call.data["uuid"])
        await coordinator.async_request_refresh()

    hass.services.async_register(DOMAIN, SERVICE_CREATE_ENTRY, create_entry)
    hass.services.async_register(DOMAIN, SERVICE_UPDATE_ENTRY, update_entry)
    hass.services.async_register(DOMAIN, SERVICE_DELETE_ENTRY, delete_entry)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: OpenInventoConfigEntry
) -> bool:
    """Unload an OpenInvento config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        for service in (
            SERVICE_CREATE_ENTRY,
            SERVICE_UPDATE_ENTRY,
            SERVICE_DELETE_ENTRY,
        ):
            hass.services.async_remove(DOMAIN, service)
    return unloaded
