# Moen Smart Faucet Integration for Home Assistant

This is an **unofficial** Home Assistant integration for Moen Smart Faucets (U by Moen). It allows you to control your smart faucet through Home Assistant using the official Moen cloud API.

## ⚠️ Important Notes

- This integration is **unofficial** and not affiliated with Moen
- It requires your Moen account credentials to work
- All communication goes through Moen's cloud services
- Use at your own risk - may violate Moen's Terms of Service
- The integration is based on reverse-engineering the official mobile app

## Features

- **Button Controls**:
  - Start/Stop dispensing water
  - Preset volume buttons (250ml, 500ml, 750ml)
- **Number Entity**: Adjustable target volume (50-2000ml)
- **Sensors**:
  - Faucet state
  - Last dispense volume
  - Cloud connection status
- **Services**: Programmatic control via Home Assistant services

## Installation

### Method 1: HACS (Recommended)

1. Add this repository to HACS as a custom repository
2. Install "Moen Smart Faucet (Unofficial)" from HACS
3. Restart Home Assistant

### Method 2: Manual Installation

1. Copy the `custom_components/moen_faucet` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Moen Smart Faucet (Unofficial)"
4. Enter your Moen account credentials:
   - **Client ID**: Your Moen app client ID (default: "moen_mobile_app" - see troubleshooting)
   - **Username**: Your Moen account email
   - **Password**: Your Moen account password

## Getting Your Client ID

The Client ID is required for API authentication. The integration provides a default value (`moen_mobile_app`) that may work, but for best results you should find your specific client ID by:

1. Using a network monitoring tool (like mitmproxy) to capture traffic from the official Moen app
2. Looking for API calls to `*.execute-api.us-east-2.amazonaws.com`
3. Finding the `client_id` field in the login request

**Note**: Try the default value first - it may work for many users. Only extract the specific client ID if you encounter authentication issues.

## Usage

### Entities

After setup, you'll have the following entities for each faucet:

**Buttons:**
- `button.start_dispense` - Start dispensing water
- `button.stop_dispense` - Stop dispensing water
- `button.preset_1` - Dispense 250ml
- `button.preset_2` - Dispense 500ml
- `button.preset_3` - Dispense 750ml

**Number:**
- `number.target_volume` - Set custom dispense volume (50-2000ml)

**Sensors:**
- `sensor.faucet_state` - Current faucet state
- `sensor.last_dispense_volume` - Volume of last dispense
- `sensor.cloud_connected` - Cloud connection status

### Services

You can also control the faucet programmatically using services:

```yaml
# Dispense water
service: moen_faucet.dispense_water
data:
  device_id: "your_device_id"
  volume_ml: 500
  timeout: 120

# Stop dispensing
service: moen_faucet.stop_dispensing
data:
  device_id: "your_device_id"

# Get device status
service: moen_faucet.get_device_status
data:
  device_id: "your_device_id"
```

### Automations

Example automation to dispense water when motion is detected:

```yaml
- alias: "Dispense water on motion"
  trigger:
    - platform: motion
      entity_id: binary_sensor.motion_sensor
  action:
    - service: moen_faucet.dispense_water
      data:
        device_id: "your_device_id"
        volume_ml: 250
```

## Troubleshooting

### Common Issues

1. **"Invalid credentials" error**:
   - Double-check your username and password
   - Ensure you're using the correct Client ID

2. **"Cannot connect" error**:
   - Check your internet connection
   - Verify the API endpoints are correct (may need updating)

3. **No devices found**:
   - Ensure your Moen account has devices registered
   - Check that the device is online in the official app

### Logs

Enable debug logging to troubleshoot issues:

```yaml
logger:
  default: info
  logs:
    custom_components.moen_faucet: debug
```

## API Endpoints

The integration uses the following Moen API endpoints:
- Login: `POST /prod/auth/login`
- List devices: `GET /prod/devices`
- Device status: `GET /prod/devices/{device_id}/status`
- Send command: `POST /prod/devices/{device_id}/commands`

## Security

- Credentials are stored securely in Home Assistant's configuration
- All communication uses HTTPS/TLS
- No local network access required

## Contributing

This integration is based on reverse-engineering the official Moen mobile app. If you have additional information about the API or encounter issues, please:

1. Check the existing issues
2. Create a new issue with detailed information
3. Include relevant logs and network captures (sanitized)

## Disclaimer

This integration is not officially supported by Moen. Use at your own risk. The authors are not responsible for any damage or issues that may arise from using this integration.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
