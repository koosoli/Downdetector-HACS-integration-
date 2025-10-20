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
from .const import CONF_SERVICE_ID, CONF_SERVICE_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def validate_service(hass: HomeAssistant, service_id: str) -> dict[str, Any]:
    """Validate the service ID by fetching its status."""
    session = async_get_clientsession(hass)
    client = DowndetectorApiClient(session)

    try:
        status = await client.get_service_status(service_id)
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

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - search for services."""
        errors: dict[str, str] = {}

        if user_input is not None:
            search_query = user_input.get("search_query", "").strip()

            if search_query:
                try:
                    session = async_get_clientsession(self.hass)
                    client = DowndetectorApiClient(session)

                    # Search for services
                    services = await client.search_services(search_query)

                    if not services:
                        # If no results from search, try getting all services and filter
                        all_services = await client.get_all_services()
                        services = [
                            s for s in all_services
                            if search_query.lower() in s.get("name", "").lower()
                        ]

                    if services:
                        self._search_results = services
                        return await self.async_step_select_service()
                    else:
                        errors["base"] = "no_services_found"

                except Exception:
                    _LOGGER.exception("Unexpected exception during service search")
                    errors["base"] = "cannot_connect"
            else:
                errors["base"] = "invalid_search"

        return self.async_show_form(
            step_id="user",
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
                service_id = self._selected_service.get("id") or self._selected_service.get("slug")
                service_name = self._selected_service.get("name")

                # Check if already configured
                await self.async_set_unique_id(f"{DOMAIN}_{service_id}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=service_name,
                    data={
                        CONF_SERVICE_ID: service_id,
                        CONF_SERVICE_NAME: service_name,
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
            return await self.async_step_user()

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
