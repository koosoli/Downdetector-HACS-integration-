# Integration Information

## Overview
This is a Home Assistant Custom Component (HACS integration) for monitoring service status using the Downdetector API.

## Features Implemented

### ✅ Core Functionality
- **Service Search**: Search for any service tracked by Downdetector
- **Real-time Monitoring**: Monitor service status with 5-minute polling intervals
- **Outage Detection**: Automatically detect and classify outages (minor/major)
- **Multiple Services**: Track unlimited services simultaneously

### ✅ Home Assistant Integration
- **Config Flow**: User-friendly setup via Home Assistant UI
- **Sensor Platform**: Creates sensors for each monitored service
- **Attributes**: Rich sensor attributes including baseline, reports, and status
- **Icons**: Dynamic icons based on service status
- **Translations**: English translations included

### ✅ HACS Compatibility
- **hacs.json**: Proper HACS metadata file
- **manifest.json**: Complete integration manifest
- **Documentation**: Comprehensive README and examples

## File Structure

```
custom_components/downdetector/
├── __init__.py              # Main integration setup
├── api.py                   # Downdetector API client
├── config_flow.py           # Configuration flow with search
├── const.py                 # Constants and configuration keys
├── manifest.json            # Integration metadata
├── sensor.py                # Sensor platform implementation
├── strings.json             # UI strings
└── translations/
    └── en.json              # English translations
```

## API Client (`api.py`)

### Methods
1. **`search_services(query: str)`** - Search for services by name
2. **`get_service_status(service_id: str)`** - Get current service status
3. **`get_all_services()`** - Get list of all available services

### API Endpoint
Base URL: `https://downdetectorapi.com/v2`

## Configuration Flow (`config_flow.py`)

### Steps
1. **User Step**: User enters search query for service
2. **Select Service**: User selects from search results
3. **Create Entry**: Integration creates sensor with unique ID

### Features
- Service search with fallback to filtering all services
- Unique ID validation to prevent duplicates
- Error handling for API connectivity issues

## Sensor Platform (`sensor.py`)

### Sensor Entity
- **State**: Number of current reports
- **Unit**: "reports"
- **State Class**: Measurement

### Attributes
- `service_id`: Service identifier
- `service_name`: Display name
- `current_reports`: Current report count
- `baseline`: Normal baseline reports
- `status`: Service status (operational, minor_outage, major_outage)
- `last_updated`: Last update timestamp

### Status Logic
- **Operational**: current_reports ≤ 1.5× baseline (🟢)
- **Minor Outage**: current_reports > 1.5× baseline (🟡)
- **Major Outage**: current_reports > 2× baseline (🔴)

### Update Coordinator
- **Interval**: 300 seconds (5 minutes)
- **Error Handling**: Proper exception handling with UpdateFailed

## Constants (`const.py`)

### Domain
`DOMAIN = "downdetector"`

### Configuration Keys
- `CONF_SERVICE_ID`: Service identifier key
- `CONF_SERVICE_NAME`: Service name key

### Attributes
- `ATTR_BASELINE`: Baseline reports attribute
- `ATTR_CURRENT_REPORTS`: Current reports attribute
- `ATTR_SERVICE_ID`: Service ID attribute
- `ATTR_SERVICE_NAME`: Service name attribute
- `ATTR_STATUS`: Status attribute
- `ATTR_LAST_UPDATED`: Last updated attribute

### Settings
- `UPDATE_INTERVAL`: 300 seconds (5 minutes)
- `DEFAULT_NAME`: "Downdetector"

## Manifest (`manifest.json`)

- **Domain**: downdetector
- **Name**: Downdetector
- **Config Flow**: Enabled
- **Integration Type**: service
- **IoT Class**: cloud_polling
- **Requirements**: aiohttp>=3.8.0
- **Version**: 1.0.0

## Testing & Validation

### Included Test Scripts
1. **`validate_integration.py`**: Validates file structure and JSON
2. **`test_structure.py`**: Validates code structure with AST parsing

### Linting
All Python files pass flake8 linting with:
- Max line length: 120
- Ignored: E501, W503

### Syntax
All Python files compile without errors.

## Installation Methods

### Via HACS (Recommended)
1. Add custom repository
2. Install "Downdetector"
3. Restart Home Assistant
4. Configure via UI

### Manual
1. Copy `custom_components/downdetector` to config
2. Restart Home Assistant
3. Configure via UI

## Usage Examples

### Basic Automation
```yaml
automation:
  - alias: "Notify on outage"
    trigger:
      platform: state
      entity_id: sensor.facebook_status
      attribute: status
      to: "major_outage"
    action:
      service: notify.mobile_app
      data:
        message: "Facebook is down!"
```

### Dashboard Card
```yaml
type: entities
title: Service Status
entities:
  - sensor.facebook_status
  - sensor.gmail_status
```

## API Rate Limiting Considerations

The integration polls the Downdetector API every 5 minutes per service. With multiple services configured:
- 1 service: 12 requests/hour
- 5 services: 60 requests/hour
- 10 services: 120 requests/hour

Adjust `UPDATE_INTERVAL` in `const.py` if needed.

## Error Handling

### API Errors
- Connection timeouts (10 second timeout)
- HTTP errors with proper logging
- Graceful fallback on search failures

### Configuration Errors
- Duplicate service prevention
- Invalid search query handling
- Service not found handling

## Future Enhancements (Not Implemented)

Potential improvements:
1. Configurable update intervals per service
2. Historical outage tracking
3. Service categories/groups
4. Notification triggers within the integration
5. Binary sensor for up/down status
6. Device class assignments

## Credits

- **API**: [Downdetector API v2](https://downdetectorapi.com/v2/docs/)
- **Home Assistant**: [Home Assistant](https://www.home-assistant.io/)
- **HACS**: [Home Assistant Community Store](https://hacs.xyz/)

## License

MIT License - See LICENSE file for details
