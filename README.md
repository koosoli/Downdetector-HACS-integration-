# Downdetector HACS Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

This integration acts as your Home Assistant's version of Downdetector, leveraging the [Downdetector API](https://downdetectorapi.com/v2/docs/) to track and monitor downtime for various services in real-time—detecting spikes in outage reports from user submissions, social media, and other sources to alert you when and where issues hit.

## 🚨 IMPORTANT: API Credentials Required

**This integration requires Downdetector API credentials to function.** The Downdetector API is a **paid service** provided by Downdetector Enterprise. You cannot use this integration without valid API credentials.

### Getting API Credentials

1. **Visit [Downdetector Enterprise](https://downdetector.com/enterprise)** to learn about their API offerings
2. **Sign up for a Downdetector API plan** - this is a paid service
3. **Access the [Downdetector Dashboard](https://dashboard.downdetector.com/api/tokens/)** after signup
4. **Generate your API credentials:**
   - Client ID
   - Client Secret

### API Costs

- The Downdetector API is a **commercial service with rate limits and costs**
- Pricing depends on your usage tier and requirements
- Contact Downdetector support for pricing details: support@downdetector.com

## Features

- 🔍 **Service Search**: Search and find any service tracked by Downdetector
- 📊 **Real-time Monitoring**: Track service status with 5-minute update intervals
- 🚨 **Outage Detection**: Automatically detects minor and major outages based on API status
- 📈 **Historical Baseline**: Uses Downdetector's baseline data for accurate status determination
- 🏠 **Native Home Assistant Integration**: Full integration with Home Assistant's config flow
- 🔐 **OAuth2 Authentication**: Secure token-based authentication with automatic renewal

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

1. **Get your API credentials** from [Downdetector Dashboard](https://dashboard.downdetector.com/api/tokens/)
2. Go to **Settings** → **Devices & Services**
3. Click **+ Add Integration**
4. Search for **Downdetector**
5. **Enter your API credentials:**
   - Client ID (from Downdetector Dashboard)
   - Client Secret (from Downdetector Dashboard)
6. **Search for a service** (e.g., "Facebook", "Gmail", "Netflix", "Signal")
7. **Select the service** from the search results
8. The integration will create a sensor for that service

You can add multiple services by repeating steps 2-8 (you only need to enter credentials once).

## Sensors

Each configured service creates a sensor with the following:

### State
The sensor state shows the **current number of reports** for the service.

### Attributes
- `service_id`: The unique identifier for the service
- `service_name`: The name of the service
- `current_reports`: Current number of outage reports
- `baseline`: Normal baseline of reports for comparison
- `status`: Service status from API (operational, minor_outage, major_outage)
- `company_slug`: Company slug identifier
- `company_url`: Direct link to the service's Downdetector page

### Status Values
- **operational**: Service is running normally (🟢)
- **minor_outage**: Service is experiencing issues (🟡)
- **major_outage**: Service has significant problems (🔴)

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

## Troubleshooting

### "Failed to connect to Downdetector API"

1. **Check your credentials** - Ensure Client ID and Client Secret are correct
2. **Verify API access** - Make sure your Downdetector account has API access
3. **Check rate limits** - You may have exceeded your API rate limits
4. **Contact Downdetector** - For API issues, contact support@downdetector.com

### "No services found"

1. **Try different search terms** - Use official service names (e.g., "Facebook" not "FB")
2. **Check spelling** - Ensure correct spelling of service names
3. **Use popular services** - Try well-known services like "Google", "Microsoft", "Amazon"

## API Information

This integration uses the [Downdetector API v2](https://downdetectorapi.com/v2/docs/). Key features:
- OAuth2 authentication with automatic token renewal
- Company search functionality (`/companies/search`)
- Real-time status information (`/companies/{id}/status`)
- Report counts and baselines (`/companies/{id}/last_15`)
- Rate limiting and usage tracking

## Support


**For API-related issues, contact Downdetector directly:** support@downdetector.com


