"""Sensor platform for Downdetector integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import DowndetectorApiClient
from .const import (
    ATTR_BASELINE,
    ATTR_CURRENT_REPORTS,
    ATTR_LAST_UPDATED,
    ATTR_SERVICE_ID,
    ATTR_SERVICE_NAME,
    ATTR_STATUS,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_SERVICE_ID,
    CONF_SERVICE_NAME,
    DOMAIN,
    UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Downdetector sensor based on a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    client: DowndetectorApiClient = data["client"]
    service_id: str = entry.data[CONF_SERVICE_ID]
    service_name: str = entry.data[CONF_SERVICE_NAME]

    coordinator = DowndetectorDataUpdateCoordinator(
        hass, client, service_id, service_name
    )

    await coordinator.async_config_entry_first_refresh()

    async_add_entities([DowndetectorSensor(coordinator, entry)])


class DowndetectorDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Downdetector data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: DowndetectorApiClient,
        service_id: str,
        service_name: str,
    ) -> None:
        """Initialize the coordinator."""
        self.client = client
        self.service_id = service_id
        self.service_name = service_name

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{service_id}",
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            status = await self.client.get_company_status(self.service_id)
            return status
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err


class DowndetectorSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Downdetector sensor."""

    def __init__(
        self,
        coordinator: DowndetectorDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_{coordinator.service_id}"
        self._attr_name = f"{coordinator.service_name} Status"
        self._attr_icon = "mdi:web-check"
        self._entry = entry

    @property
    def state(self) -> int | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            # Return the number of current reports
            return self.coordinator.data.get("current_reports", 0)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data:
            return {}

        attrs = {
            ATTR_SERVICE_ID: self.coordinator.service_id,
            ATTR_SERVICE_NAME: self.coordinator.service_name,
            ATTR_CURRENT_REPORTS: self.coordinator.data.get("current_reports", 0),
            ATTR_BASELINE: self.coordinator.data.get("baseline", 0),
        }

        # Get status from API or determine based on reports vs baseline
        api_status = self.coordinator.data.get("status", "unknown")
        current = self.coordinator.data.get("current_reports", 0)
        baseline = self.coordinator.data.get("baseline", 0)

        # Map API status to our status
        if api_status == "danger":
            attrs[ATTR_STATUS] = "major_outage"
            self._attr_icon = "mdi:web-remove"
        elif api_status == "warning":
            attrs[ATTR_STATUS] = "minor_outage"
            self._attr_icon = "mdi:web-clock"
        elif api_status == "success":
            attrs[ATTR_STATUS] = "operational"
            self._attr_icon = "mdi:web-check"
        else:
            # Fallback to baseline comparison
            if baseline > 0 and current > baseline * 2:
                attrs[ATTR_STATUS] = "major_outage"
                self._attr_icon = "mdi:web-remove"
            elif baseline > 0 and current > baseline * 1.5:
                attrs[ATTR_STATUS] = "minor_outage"
                self._attr_icon = "mdi:web-clock"
            else:
                attrs[ATTR_STATUS] = "operational"
                self._attr_icon = "mdi:web-check"

        # Add company info if available
        if "company" in self.coordinator.data:
            company = self.coordinator.data["company"]
            attrs["company_slug"] = company.get("slug")
            attrs["company_url"] = company.get("url")

        return attrs

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    @property
    def state_class(self) -> SensorStateClass | None:
        """Return the state class of this entity."""
        return SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return "reports"
