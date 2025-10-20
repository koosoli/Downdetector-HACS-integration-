"""Config flow for Downdetector integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .api import DowndetectorApiClient
from .const import CONF_SERVICE_ID, CONF_SERVICE_NAME, CONF_CLIENT_ID, CONF_CLIENT_SECRET, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def validate_service(hass: HomeAssistant, service_id: str, client_id: str, client_secret: str) -> dict[str, Any]:
    """Validate the service ID by fetching its status."""
    session = async_get_clientsession(hass)
    client = DowndetectorApiClient(session, client_id, client_secret)

    try:
        status = await client.get_company_status(service_id)
        return {"title": service_id, "status": status}
    except Exception as err:
        _LOGGER.error("Error validating service: %s", err)
        raise


class DowndetectorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Downdetector."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._search_results: list[dict[str, Any]] = []
        self._selected_service: dict[str, Any] | None = None
        self._client_id: str = ""
        self._client_secret: str = ""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - collect API credentials."""
        errors: dict[str, str] = {}

        if user_input is not None:
            client_id = user_input.get(CONF_CLIENT_ID, "").strip()
            client_secret = user_input.get(CONF_CLIENT_SECRET, "").strip()

            if client_id and client_secret:
                try:
                    # Test the credentials
                    session = async_get_clientsession(self.hass)
                    client = DowndetectorApiClient(session, client_id, client_secret)
                    
                    if await client.test_connection():
                        self._client_id = client_id
                        self._client_secret = client_secret
                        return await self.async_step_search()
                    else:
                        errors["base"] = "invalid_auth"

                except Exception:
                    _LOGGER.exception("Unexpected exception during credential validation")
                    errors["base"] = "cannot_connect"
            else:
                errors["base"] = "invalid_credentials"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_CLIENT_ID): cv.string,
                    vol.Required(CONF_CLIENT_SECRET): cv.string,
                }
            ),
            errors=errors,
        )

    async def async_step_search(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the search step - search for companies."""
        errors: dict[str, str] = {}

        if user_input is not None:
            search_query = user_input.get("search_query", "").strip()

            if search_query:
                try:
                    session = async_get_clientsession(self.hass)
                    client = DowndetectorApiClient(session, self._client_id, self._client_secret)

                    # Search for companies
                    companies = await client.search_companies(search_query)

                    if companies:
                        self._search_results = companies
                        return await self.async_step_select_service()
                    else:
                        errors["base"] = "no_services_found"

                except Exception:
                    _LOGGER.exception("Unexpected exception during company search")
                    errors["base"] = "cannot_connect"
            else:
                errors["base"] = "invalid_search"

        return self.async_show_form(
            step_id="search",
            data_schema=vol.Schema(
                {
                    vol.Required("search_query"): cv.string,
                }
            ),
            errors=errors,
        )

    async def async_step_select_service(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle service selection from search results."""
        errors: dict[str, str] = {}

        if user_input is not None:
            selected_name = user_input["service"]

            # Find the selected service from search results
            for service in self._search_results:
                if service.get("name") == selected_name:
                    self._selected_service = service
                    break

            if self._selected_service:
                service_id = str(self._selected_service.get("id"))
                service_name = self._selected_service.get("name")

                # Check if already configured
                await self.async_set_unique_id(f"{DOMAIN}_{service_id}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=service_name,
                    data={
                        CONF_SERVICE_ID: service_id,
                        CONF_SERVICE_NAME: service_name,
                        CONF_CLIENT_ID: self._client_id,
                        CONF_CLIENT_SECRET: self._client_secret,
                    },
                )
            else:
                errors["base"] = "service_not_found"

        # Create options list for selection
        service_options = {
            service.get("name"): service.get("name")
            for service in self._search_results
            if service.get("name")
        }

        if not service_options:
            # No valid services found, go back to search
            return await self.async_step_search()

        return self.async_show_form(
            step_id="select_service",
            data_schema=vol.Schema(
                {
                    vol.Required("service"): vol.In(service_options),
                }
            ),
            errors=errors,
            description_placeholders={
                "num_results": str(len(self._search_results))
            },
        )
