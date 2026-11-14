"""Runtime data types for OpenInvento."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

    from .openinvento import OpenInventoApiClient


@dataclass
class OpenInventoRuntimeData:
    """Runtime data for one OpenInvento instance."""

    client: OpenInventoApiClient
    coordinator: DataUpdateCoordinator


type OpenInventoConfigEntry = ConfigEntry[OpenInventoRuntimeData]
