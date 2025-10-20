# Downdetector HACS Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

This integration acts as your Home Assistant's version of Downdetector, leveraging the [Downdetector API](https://downdetectorapi.com/v2/docs/) to track and monitor downtime for various services in real-time—detecting spikes in outage reports from user submissions, social media, and other sources to alert you when and where issues hit.

## Features

- 🔍 **Service Search**: Search and find any service tracked by Downdetector
- 📊 **Real-time Monitoring**: Track service status with 5-minute update intervals
- 🚨 **Outage Detection**: Automatically detects minor and major outages based on report thresholds
- 📈 **Historical Baseline**: Compares current reports against baseline to determine service health
- 🏠 **Native Home Assistant Integration**: Full integration with Home Assistant's config flow

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots menu in the top right
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/koosoli/Downdetector-HACS-integration-`
6. Select category: "Integration"
7. Click "Add"
8. Find "Downdetector" in the integration list and install it
9. Restart Home Assistant

### Manual Installation

1. Download the `custom_components/downdetector` directory from this repository
2. Copy it to your Home Assistant's `custom_components` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **Downdetector**
4. Enter the name of a service you want to track (e.g., "Facebook", "Gmail", "Netflix")
5. Select the service from the search results
6. The integration will create a sensor for that service

You can add multiple services by repeating these steps.

## Sensors

Each configured service creates a sensor with the following:

### State
The sensor state shows the **current number of reports** for the service.

### Attributes
- `service_id`: The unique identifier for the service
- `service_name`: The name of the service
- `current_reports`: Current number of outage reports
- `baseline`: Normal baseline of reports for comparison
- `status`: Service status (operational, minor_outage, major_outage)
- `last_updated`: Timestamp of last status update

### Status Determination
- **Operational** (🟢): Current reports ≤ 1.5x baseline
- **Minor Outage** (🟡): Current reports > 1.5x baseline
- **Major Outage** (🔴): Current reports > 2x baseline

## Usage Examples

### Automation Example

Create an automation to notify you when a service goes down:

```yaml
automation:
  - alias: "Notify when service is down"
    trigger:
      - platform: state
        entity_id: sensor.facebook_status
        attribute: status
        to: "major_outage"
    action:
      - service: notify.mobile_app
        data:
          title: "Service Outage Alert"
          message: "Facebook is experiencing a major outage!"
```

### Dashboard Card Example

Display service status on your dashboard:

```yaml
type: entities
title: Service Status
entities:
  - entity: sensor.facebook_status
  - entity: sensor.gmail_status
  - entity: sensor.netflix_status
```

## API Information

This integration uses the [Downdetector API v2](https://downdetectorapi.com/v2/docs/). The API provides:
- Service search functionality
- Real-time status information
- Report counts and baselines
- Multiple service monitoring

## Support

For issues, feature requests, or contributions, please visit the [GitHub repository](https://github.com/koosoli/Downdetector-HACS-integration-/issues).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
