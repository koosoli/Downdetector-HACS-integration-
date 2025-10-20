"""Downdetector API Client."""
import asyncio
import base64
import logging
import time
from typing import Any, Optional

import aiohttp
import async_timeout

_LOGGER = logging.getLogger(__name__)

# Official Downdetector API endpoint
# Documentation: https://downdetectorapi.com/v2/docs/
API_BASE_URL = "https://downdetectorapi.com/v2"
DEFAULT_TIMEOUT = 10
TOKEN_CACHE_SECONDS = 3300  # 55 minutes (tokens expire after 1 hour)


class DowndetectorApiClient:
    """Downdetector API Client with OAuth2 authentication."""

    def __init__(self, session: aiohttp.ClientSession, client_id: str, client_secret: str) -> None:
        """Initialize the API client.
        
        Args:
            session: aiohttp session
            client_id: API client ID
            client_secret: API client secret
        """
        self._session = session
        self._client_id = client_id
        self._client_secret = client_secret
        self._token: Optional[str] = None
        self._token_expires_at: float = 0
        self._token_lock = asyncio.Lock()

    async def _get_auth_token(self) -> str:
        """Get a valid authentication token, refreshing if necessary."""
        async with self._token_lock:
            # Check if we have a valid token
            if self._token and time.time() < self._token_expires_at:
                return self._token

            # Generate new token
            try:
                # Create basic auth header
                credentials = f"{self._client_id}:{self._client_secret}"
                encoded_credentials = base64.b64encode(credentials.encode()).decode()
                
                headers = {
                    "Authorization": f"Basic {encoded_credentials}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                
                data = "grant_type=client_credentials"
                
                async with async_timeout.timeout(DEFAULT_TIMEOUT):
                    async with self._session.post(
                        f"{API_BASE_URL}/tokens",
                        headers=headers,
                        data=data
                    ) as response:
                        response.raise_for_status()
                        token_data = await response.json()
                        
                        self._token = token_data["access_token"]
                        # Set expiry time a bit earlier to be safe
                        self._token_expires_at = time.time() + TOKEN_CACHE_SECONDS
                        
                        _LOGGER.debug("Successfully obtained new API token")
                        return self._token
                        
            except aiohttp.ClientError as err:
                _LOGGER.error("Error obtaining API token: %s", err)
                raise
            except Exception as err:
                _LOGGER.error("Unexpected error obtaining API token: %s", err)
                raise

    async def _make_authenticated_request(self, method: str, endpoint: str, **kwargs) -> dict[str, Any]:
        """Make an authenticated request to the API."""
        token = await self._get_auth_token()
        
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        kwargs["headers"] = headers
        
        url = f"{API_BASE_URL}{endpoint}"
        
        try:
            async with async_timeout.timeout(DEFAULT_TIMEOUT):
                async with self._session.request(method, url, **kwargs) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientResponseError as err:
            if err.status == 401:
                # Token might be expired, clear it and retry once
                _LOGGER.warning("API token expired, refreshing...")
                self._token = None
                self._token_expires_at = 0
                
                # Retry with new token
                token = await self._get_auth_token()
                headers["Authorization"] = f"Bearer {token}"
                
                async with async_timeout.timeout(DEFAULT_TIMEOUT):
                    async with self._session.request(method, url, **kwargs) as response:
                        response.raise_for_status()
                        return await response.json()
            raise

    async def search_companies(self, query: str) -> list[dict[str, Any]]:
        """Search for companies by name.

        Args:
            query: Search query string

        Returns:
            List of matching companies with their details
        """
        try:
            params = {"name": query}
            data = await self._make_authenticated_request(
                "GET", "/companies/search", 
                params=params
            )
            return data if isinstance(data, list) else []
        except aiohttp.ClientError as err:
            _LOGGER.error("Error searching companies: %s", err)
            raise
        except Exception as err:
            _LOGGER.error("Unexpected error searching companies: %s", err)
            raise

    async def get_company_status(self, company_id: str) -> dict[str, Any]:
        """Get the current status of a company.

        Args:
            company_id: The ID of the company to check

        Returns:
            Company status information including baseline and current reports
        """
        try:
            # Get company details with stats
            company_data = await self._make_authenticated_request(
                "GET", 
                f"/companies/{company_id}",
                params={"fields": "id,name,slug,stats_24,baseline,baseline_current,status"}
            )
            
            # Get last 15 minutes data
            last_15_data = await self._make_authenticated_request(
                "GET", 
                f"/companies/{company_id}/last_15"
            )
            
            # Combine the data
            return {
                "company": company_data,
                "current_reports": last_15_data,
                "baseline": company_data.get("baseline_current", 0),
                "status": company_data.get("status", "unknown")
            }
            
        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching company status for %s: %s", company_id, err)
            raise
        except Exception as err:
            _LOGGER.error("Unexpected error fetching company status: %s", err)
            raise

    async def test_connection(self) -> bool:
        """Test the API connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            await self._make_authenticated_request("GET", "/ping")
            return True
        except Exception as err:
            _LOGGER.error("Connection test failed: %s", err)
            return False
