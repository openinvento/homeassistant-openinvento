"""Config flow for OpenInvento."""  # noqa: EXE002

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_API_KEY, CONF_URL, CONF_VERIFY_SSL, DOMAIN
from .openinvento import (
    OpenInventoApiAuthenticationError,
    OpenInventoApiClient,
    OpenInventoApiCommunicationError,
    OpenInventoApiError,
)


class OpenInventoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle OpenInvento configuration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the user step."""
        errors: dict[str, str] = {}
        if user_input:
            client = OpenInventoApiClient(
                user_input[CONF_URL],
                user_input[CONF_API_KEY],
                async_get_clientsession(self.hass),
                verify_ssl=user_input[CONF_VERIFY_SSL],
            )
            try:
                await client.async_get_inventories()
            except OpenInventoApiAuthenticationError:
                errors["base"] = "auth"
            except OpenInventoApiCommunicationError:
                errors["base"] = "connection"
            except OpenInventoApiError:
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(user_input[CONF_URL])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_URL], data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_URL, default=(user_input or {}).get(CONF_URL, "")
                    ): str,
                    vol.Required(CONF_API_KEY): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD
                        )
                    ),
                    vol.Required(
                        CONF_VERIFY_SSL, default=True
                    ): selector.BooleanSelector(),
                }
            ),
            errors=errors,
        )
