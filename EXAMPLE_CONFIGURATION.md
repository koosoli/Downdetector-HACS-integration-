# Example configuration for Downdetector integration

## Installation

1. Install via HACS or manually copy `custom_components/downdetector` to your Home Assistant config directory
2. Restart Home Assistant
3. Go to Settings -> Devices & Services -> Add Integration
4. Search for "Downdetector"
5. Follow the configuration flow

## Example Configuration (via UI)

The integration is configured through the UI config flow:

1. **Search for Service**: Enter the name of a service (e.g., "Facebook", "Gmail", "Netflix")
2. **Select Service**: Choose from the search results
3. The sensor will be created automatically

## Example Sensors

After configuration, you'll get sensors like:
- `sensor.facebook_status`
- `sensor.gmail_status`
- `sensor.netflix_status`

## Example Automations

### Notify on Major Outage

```yaml
automation:
  - alias: "Notify Major Service Outage"
    trigger:
      - platform: state
        entity_id: sensor.facebook_status
        attribute: status
        to: "major_outage"
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Service Outage Alert"
          message: "{{ trigger.to_state.name }} is experiencing a major outage!"
          data:
            priority: high
```

### Notify on Any Service Issue

```yaml
automation:
  - alias: "Notify Any Service Issue"
    trigger:
      - platform: state
        entity_id:
          - sensor.facebook_status
          - sensor.gmail_status
          - sensor.netflix_status
        attribute: status
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.attributes.status != 'operational' }}"
    action:
      - service: notify.mobile_app
        data:
          title: "Service Status Change"
          message: >
            {{ trigger.to_state.name }} status: {{ trigger.to_state.attributes.status }}
            ({{ trigger.to_state.state }} reports)
```

### Dashboard Status Card

```yaml
type: entities
title: Service Status Monitor
entities:
  - entity: sensor.facebook_status
    secondary_info: last-changed
  - entity: sensor.gmail_status
    secondary_info: last-changed
  - entity: sensor.netflix_status
    secondary_info: last-changed
```

### Conditional Status Display

```yaml
type: conditional
conditions:
  - entity: sensor.facebook_status
    state_not: "0"
card:
  type: entity
  entity: sensor.facebook_status
  name: "⚠️ Facebook Issues Detected"
```

## Sensor Attributes

Each sensor provides these attributes:
- `service_id`: Unique identifier for the service
- `service_name`: Display name of the service
- `current_reports`: Current number of outage reports
- `baseline`: Normal baseline of reports
- `status`: Current status (operational, minor_outage, major_outage)
- `last_updated`: Timestamp of last update

## Lovelace Card Example

```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      ## Service Health Monitor
      Track the status of your important services
  - type: entities
    entities:
      - type: custom:template-entity-row
        entity: sensor.facebook_status
        name: Facebook
        state: >
          {% if state_attr('sensor.facebook_status', 'status') == 'operational' %}
            ✅ Operational
          {% elif state_attr('sensor.facebook_status', 'status') == 'minor_outage' %}
            ⚠️ Minor Issues
          {% else %}
            🔴 Major Outage
          {% endif %}
        secondary: "{{ state('sensor.facebook_status') }} reports"
```

## Tips

1. **Update Frequency**: The integration polls the API every 5 minutes
2. **Multiple Services**: You can add as many services as you want by adding the integration multiple times
3. **Service Names**: Use exact service names or search terms that match the Downdetector database
4. **Status Thresholds**:
   - Operational: Current reports ≤ 1.5x baseline
   - Minor Outage: Current reports > 1.5x baseline
   - Major Outage: Current reports > 2x baseline
