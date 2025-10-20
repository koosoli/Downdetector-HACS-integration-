# Downdetector HACS Integration Configuration Example

This file demonstrates how to configure the Downdetector integration.

## Prerequisites

**⚠️ IMPORTANT:** You need valid Downdetector API credentials to use this integration.

1. **Sign up for Downdetector Enterprise:** Visit [https://downdetector.com/enterprise](https://downdetector.com/enterprise)
2. **Get API access:** This is a paid service with different tiers
3. **Obtain credentials:** Get your Client ID and Client Secret from [https://dashboard.downdetector.com/api/tokens/](https://dashboard.downdetector.com/api/tokens/)

## Installation Steps

1. Install the integration via HACS or manually
2. Go to **Settings** → **Devices & Services** → **Add Integration**
3. Search for "Downdetector"
4. **Enter your API credentials:**
   - Client ID: (from Downdetector Dashboard)
   - Client Secret: (from Downdetector Dashboard)
5. **Search for a service** (e.g., "Facebook", "Netflix", "Gmail", "Signal")
6. **Select the desired service** from the search results
7. The sensor will be created automatically

## Configuration

The integration is configured entirely through the Home Assistant UI. No YAML configuration is required.

### Supported Services

You can track any service that appears on Downdetector, including but not limited to:

- **Social Media:** Facebook, Twitter, Instagram, TikTok, Snapchat, Signal
- **Communication:** WhatsApp, Telegram, Discord, Zoom, Microsoft Teams
- **Streaming:** Netflix, YouTube, Spotify, Twitch, Disney+
- **Gaming:** PlayStation Network, Xbox Live, Steam, Epic Games
- **Email:** Gmail, Yahoo Mail, Outlook
- **Cloud Services:** AWS, Google Cloud, Microsoft Azure
- **E-commerce:** Amazon, eBay, PayPal, Shopify
- **Financial:** PayPal, Stripe, Square, Coinbase

### Example Sensor Names

After configuration, sensors will be created with names like:
- `sensor.facebook_status`
- `sensor.netflix_status`
- `sensor.gmail_status`
- `sensor.signal_status`

## Sensor Attributes

Each sensor provides the following attributes:

```yaml
state: 15  # Current number of reports
attributes:
  service_id: "42"
  service_name: "Facebook"
  current_reports: 15
  baseline: 8
  status: "minor_outage"  # operational, minor_outage, major_outage
  company_slug: "facebook"
  company_url: "https://downdetector.com/status/facebook"
```

## Usage in Automations

```yaml
# Example automation to notify when a service is down
automation:
  - alias: "Service Outage Notification"
    trigger:
      - platform: state
        entity_id: sensor.facebook_status
        attribute: status
        to: "major_outage"
    action:
      - service: notify.mobile_app
        data:
          title: "🚨 Service Alert"
          message: "{{ trigger.to_state.attributes.service_name }} is experiencing a major outage!"
          data:
            url: "{{ trigger.to_state.attributes.company_url }}"

# Monitor multiple services at once
automation:
  - alias: "Critical Services Monitor"
    trigger:
      - platform: state
        entity_id: 
          - sensor.facebook_status
          - sensor.netflix_status
          - sensor.gmail_status
          - sensor.signal_status
        attribute: status
        to: "major_outage"
    action:
      - service: persistent_notification.create
        data:
          title: "Service Outage Detected"
          message: >
            {{ trigger.to_state.attributes.service_name }} is down!
            Current reports: {{ trigger.to_state.state }}
            Baseline: {{ trigger.to_state.attributes.baseline }}
          notification_id: "service_outage_{{ trigger.entity_id }}"

# Automation to clear notifications when service recovers
automation:
  - alias: "Service Recovery Notification"
    trigger:
      - platform: state
        entity_id: 
          - sensor.facebook_status
          - sensor.netflix_status
          - sensor.gmail_status
        attribute: status
        to: "operational"
        from: 
          - "minor_outage"
          - "major_outage"
    action:
      - service: persistent_notification.dismiss
        data:
          notification_id: "service_outage_{{ trigger.entity_id }}"
      - service: notify.mobile_app
        data:
          title: "✅ Service Recovered"
          message: "{{ trigger.to_state.attributes.service_name }} is back online!"
```

## Dashboard Examples

### Simple Entity Card
```yaml
type: entity
entity: sensor.facebook_status
name: Facebook Status
icon: mdi:facebook
```

### Custom Status Card with Color Coding
```yaml
type: entities
title: Service Status Monitor
entities:
  - entity: sensor.facebook_status
    name: Facebook
    icon: mdi:facebook
  - entity: sensor.netflix_status  
    name: Netflix
    icon: mdi:netflix
  - entity: sensor.gmail_status
    name: Gmail
    icon: mdi:gmail
  - entity: sensor.signal_status
    name: Signal
    icon: mdi:signal
state_color: true
show_header_toggle: false
```

### Conditional Card (Show only during outages)
```yaml
type: conditional
conditions:
  - entity: sensor.facebook_status
    attribute: status
    state_not: "operational"
card:
  type: entity
  entity: sensor.facebook_status
  name: Facebook Outage Detected
  icon: mdi:alert-circle
  state_color: true
```

### Markdown Card with Status Summary
```yaml
type: markdown
content: |
  ## Service Status Summary
  
  {% set services = [
    states('sensor.facebook_status'),
    states('sensor.netflix_status'), 
    states('sensor.gmail_status')
  ] %}
  
  {% for service in services %}
  {% set entity = 'sensor.' + service.entity_id.split('.')[1] %}
  {% set status = state_attr(entity, 'status') %}
  {% set icon = '🟢' if status == 'operational' else '🟡' if status == 'minor_outage' else '🔴' %}
  {{ icon }} **{{ state_attr(entity, 'service_name') }}**: {{ status.replace('_', ' ').title() }}
  {% endfor %}
```

## Advanced Configuration

### Multiple Services
You can add multiple instances of the integration to monitor different services. Each service will get its own sensor. You only need to enter your API credentials once.

### Update Frequency
The integration updates every 5 minutes by default. This provides a good balance between data freshness and API rate limit usage.

### API Rate Limits
- Be mindful of your API rate limits based on your Downdetector plan
- The integration uses efficient caching to minimize API calls
- Tokens are automatically renewed before expiration

## Troubleshooting

### "Invalid API credentials"
1. Double-check your Client ID and Client Secret from the Downdetector Dashboard
2. Ensure your Downdetector account has active API access
3. Verify you haven't exceeded your API rate limits

### Service Not Found
If a service isn't found during setup:
1. Try the exact name as shown on downdetector.com (e.g., "Signal" not "Signal Messenger")
2. Search for popular variations: "Google" vs "Google Services" vs "Gmail"
3. Check the official Downdetector website to see how the service is listed
4. Try parent company names (e.g., "Meta" for Facebook services)

### Authenticated Connection Failed
1. Check your internet connection and firewall settings
2. Verify the Downdetector API endpoints are accessible
3. Check Home Assistant logs for specific error messages:
   ```bash
   docker logs homeassistant | grep downdetector
   ```
4. Try reloading the integration: **Settings** → **Devices & Services** → **Downdetector** → **Reload**

### Sensor Shows "Unavailable"
If sensors show as unavailable:
1. Check API rate limits - you may need to upgrade your plan
2. Verify your credentials haven't expired
3. Look for specific error messages in Home Assistant logs
4. Test the connection by trying to add a new service

### Getting API Access
If you don't have API access:
1. Visit [Downdetector Enterprise](https://downdetector.com/enterprise)
2. Contact sales for pricing and plan options
3. This is a commercial API service - free tier is not available
4. For questions: support@downdetector.com
