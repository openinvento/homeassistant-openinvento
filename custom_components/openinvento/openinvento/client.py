"""HTTP client for the OpenInvento external REST API."""  # noqa: EXE002

from __future__ import annotations

import asyncio
import socket
from http import HTTPStatus
from typing import Any
from urllib.parse import urljoin

import aiohttp


class OpenInventoApiError(Exception):
    """Base OpenInvento API error."""


class OpenInventoApiAuthenticationError(OpenInventoApiError):
    """The API key is invalid or not authorized."""


class OpenInventoApiCommunicationError(OpenInventoApiError):
    """The API could not be reached."""


class OpenInventoApiClient:
    """Small async client for OpenInvento's external API."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        session: aiohttp.ClientSession,
        *,
        verify_ssl: bool = True,
    ) -> None:
        """Initialize the API client."""
        self._base_url = f"{base_url.rstrip('/')}/"
        self._session = session
        self._verify_ssl = verify_ssl
        self._headers = {
            "Authorization": f"Api-Key {api_key}",
            "Content-Type": "application/json",
        }

    async def async_get_inventories(self) -> list[dict[str, Any]]:
        """Return accessible inventories."""
        return await self._request("GET", "api/inventories/")

    async def async_get_summary(self) -> dict[str, Any]:
        """Return aggregated statistics for all accessible inventories."""
        inventories = await self.async_get_inventories()
        entries: list[dict[str, Any]] = []
        inventory_items = [
            {"uuid": item.get("uuid"), "name": item.get("name")} for item in inventories
        ]
        article_items: list[dict[str, Any]] = []
        area_items: list[dict[str, Any]] = []
        low_stock_items: list[dict[str, Any]] = []
        areas = articles = low_stock = 0
        for inventory in inventories:
            current = await self._request(
                "GET", "api/entries/", params={"inventory": inventory["uuid"]}
            )
            for item in current:
                item_with_inventory = {
                    **item,
                    "inventory": inventory.get("name", inventory["uuid"]),
                }
                entries.append(item_with_inventory)
                if item.get("type") == "article":
                    article_items.append(item_with_inventory)
                    if (
                        item.get("stock_tracking", False)
                        and item.get("quantity", 0) <= 0
                    ):
                        low_stock_items.append(item_with_inventory)
                elif item.get("type") == "area":
                    area_items.append(item_with_inventory)
            areas += sum(item.get("type") == "area" for item in current)
            articles += sum(item.get("type") == "article" for item in current)
            low_stock = len(low_stock_items)
        return {
            "inventories": len(inventories),
            "entries": len(entries),
            "areas": areas,
            "articles": articles,
            "low_stock": low_stock,
            "inventory_items": inventory_items,
            "entry_items": entries,
            "article_items": article_items,
            "area_items": area_items,
            "low_stock_items": low_stock_items,
        }

    async def async_create_entry(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create an inventory entry."""
        return await self._request("POST", "api/entries/", json=data)

    async def async_update_entry(
        self, entry_uuid: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update an inventory entry."""
        return await self._request("PATCH", f"api/entries/{entry_uuid}/", json=data)

    async def async_delete_entry(self, entry_uuid: str) -> None:
        """Delete an inventory entry."""
        await self._request("DELETE", f"api/entries/{entry_uuid}/")

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        """Perform one authenticated API request."""
        try:
            async with asyncio.timeout(30):
                async with self._session.request(
                    method,
                    urljoin(self._base_url, path),
                    headers=self._headers,
                    ssl=self._verify_ssl,
                    **kwargs,
                ) as response:
                    if response.status in (
                        HTTPStatus.UNAUTHORIZED,
                        HTTPStatus.FORBIDDEN,
                    ):
                        raise OpenInventoApiAuthenticationError
                    if response.status >= HTTPStatus.BAD_REQUEST:
                        detail = await response.text()
                        msg = f"OpenInvento API returned {response.status}: {detail}"
                        raise OpenInventoApiError(msg)  # noqa: TRY301
                    if response.status == HTTPStatus.NO_CONTENT:
                        return None
                    return await response.json()
        except OpenInventoApiError:
            raise
        except (TimeoutError, aiohttp.ClientError, socket.gaierror) as err:
            msg = f"Unable to communicate with OpenInvento: {err}"
            raise OpenInventoApiCommunicationError(msg) from err
