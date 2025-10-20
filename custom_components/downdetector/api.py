"""Downdetector API Client."""
import logging
from typing import Any

import aiohttp
import async_timeout

_LOGGER = logging.getLogger(__name__)

API_BASE_URL = "https://downdetectorapi.com/v2"
DEFAULT_TIMEOUT = 10


class DowndetectorApiClient:
    """Downdetector API Client."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self._session = session

    async def search_services(self, query: str) -> list[dict[str, Any]]:
        """Search for services by name.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching services with their details
        """
        try:
            async with async_timeout.timeout(DEFAULT_TIMEOUT):
                url = f"{API_BASE_URL}/services"
                params = {"search": query}
                async with self._session.get(url, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data.get("services", [])
        except aiohttp.ClientError as err:
            _LOGGER.error("Error searching services: %s", err)
            raise
        except Exception as err:
            _LOGGER.error("Unexpected error searching services: %s", err)
            raise

    async def get_service_status(self, service_id: str) -> dict[str, Any]:
        """Get the current status of a service.
        
        Args:
            service_id: The ID of the service to check
            
        Returns:
            Service status information including baseline and current reports
        """
        try:
            async with async_timeout.timeout(DEFAULT_TIMEOUT):
                url = f"{API_BASE_URL}/services/{service_id}/status"
                async with self._session.get(url) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching service status for %s: %s", service_id, err)
            raise
        except Exception as err:
            _LOGGER.error("Unexpected error fetching service status: %s", err)
            raise

    async def get_all_services(self) -> list[dict[str, Any]]:
        """Get all available services.
        
        Returns:
            List of all services
        """
        try:
            async with async_timeout.timeout(DEFAULT_TIMEOUT):
                url = f"{API_BASE_URL}/services"
                async with self._session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data.get("services", [])
        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching all services: %s", err)
            raise
        except Exception as err:
            _LOGGER.error("Unexpected error fetching all services: %s", err)
            raise
