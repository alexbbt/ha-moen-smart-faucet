> [!IMPORTANT]
> Before setting up the integration, ensure your Moen Smart Water Network faucet is connected to your network and accessible via the Moen mobile app. This integration requires your Moen account credentials and uses the reverse-engineered official Moen cloud API.

# Moen Smart Water Integration for Home Assistant

### Smart Faucet Control Made Simple
#### Control your Moen Smart Water Network faucet directly from Home Assistant

* Real-time faucet state monitoring and control
* Preset volume dispensing (250ml, 500ml, 750ml)
* Custom volume control (50-2000ml)
* Cloud connection status monitoring
* Easy UI-based configuration
* Professional Moen integration

## ⚠️ Important Notes

- This integration is **unofficial** and not affiliated with Moen
- It requires your Moen account credentials to work
- All communication goes through Moen's cloud services
- Use at your own risk - may violate Moen's Terms of Service
- The integration is based on reverse-engineering the official mobile app

### Supported Devices
#### This integration has been tested with the following Moen Smart Water Network faucet series

### MotionSense Wave Kitchen Faucets
* **Tested**: Cia model
* **Likely Compatible**: Other MotionSense Wave Kitchen Faucets
* **Unknown**: Other Moen Smart Water Network families

### Requirements
* Faucet connected to your home network
* Registered with a Moen account
* Valid Moen account credentials

> [!NOTE]
> Only tested with MotionSense Wave Kitchen Faucets (Cia model). May work with other models in the same family. [Report other models](https://github.com/alexbbt/ha-moen-smart-faucet/issues/new).

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

### Via [HACS](https://hacs.xyz/)
<a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=alexbbt&repository=ha-moen-smart-faucet&category=integration" target="_blank"><img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="Open your Home Assistant instance and open a repository inside the Home Assistant Community Store." /></a>

### Manually

Get the folder `custom_components/moen_smart_water` in your HA `config/custom_components`

## Configuration
<a href="https://my.home-assistant.io/redirect/config_flow_start/?domain=moen_smart_water" target="_blank"><img src="https://my.home-assistant.io/badges/config_flow_start.svg" alt="Open your Home Assistant instance and start setting up a new integration." /></a>

- Enter your Moen account credentials and optionally adjust the client ID.

> [!TIP]
> **Finding Your Client ID:**
> * The integration provides a default value (`moen_mobile_app`) that may work
> * For best results, extract your specific client ID using a network monitoring tool
> * Use mitmproxy to capture traffic from the official Moen app
> * Look for API calls to `*.execute-api.us-east-2.amazonaws.com`
> * Find the `client_id` field in the login request

## Entity Naming

Entities are automatically created for each connected Moen Smart Water Network faucet. They are named in the format `{entity_type}_{device_name}` for easy identification.

The integration automatically detects and creates entities for:

- **Buttons**: Start/Stop dispensing, Preset volumes (250ml, 500ml, 750ml)
- **Number**: Custom target volume control (50-2000ml)
- **Sensors**: Faucet state, Last dispense volume, Cloud connection status

> [!NOTE]
> Only entities available on your specific faucet model will be created. The integration queries your Moen account and only adds entities for faucets that are detected.

Example entity names:
- `button.start_dispense_kitchen_faucet`
- `button.preset_1_kitchen_faucet`
- `number.target_volume_kitchen_faucet`
- `sensor.faucet_state_kitchen_faucet`
- `sensor.last_dispense_volume_kitchen_faucet`
- `sensor.cloud_connected_kitchen_faucet`

### Services

You can also control the faucet programmatically using services:

```yaml
# Dispense water
service: moen_smart_water.dispense_water
data:
  device_id: "your_device_id"
  volume_ml: 500
  timeout: 120

# Stop dispensing
service: moen_smart_water.stop_dispensing
data:
  device_id: "your_device_id"

# Get device status
service: moen_smart_water.get_device_status
data:
  device_id: "your_device_id"
```

> [!TIP]
> **Finding Your Device ID:**
> * Check the Home Assistant logs after integration setup
> * Look for device discovery messages
> * Use the `moen_smart_water.get_device_status` service to list available devices

### Automations

Example automation to dispense water when motion is detected:

```yaml
- alias: "Dispense water on motion"
  trigger:
    - platform: motion
      entity_id: binary_sensor.motion_sensor
  action:
    - service: moen_smart_water.dispense_water
      data:
        device_id: "your_device_id"
        volume_ml: 250
```

> [!NOTE]
> Replace `"your_device_id"` with the actual device ID from your Moen Smart Water Network faucet. You can find this in the Home Assistant logs or by using the device status service.

## Troubleshooting

To troubleshoot your Home Assistant instance, you can add the following configuration to your configuration.yaml file:

```yaml
logger:
  default: warning  # Default log level for all components
  logs:
    custom_components.moen_smart_water: debug    # Enable debug logging for this integration
```

> [!WARNING]
> **Common Issues:**
> * Ensure the faucet is powered on and connected to your network
> * Verify your Moen account credentials are correct
> * Check that the faucet is online in the official Moen mobile app
> * Try using the default client ID (`moen_mobile_app`) first
> * Check Home Assistant logs for any error messages
> * Some faucet features may not be available on all models

## API Endpoints

The integration uses the following Moen API endpoints:
- Login: `POST /prod/auth/login`
- List devices: `GET /prod/devices`
- Device status: `GET /prod/devices/{device_id}/status`
- Send command: `POST /prod/devices/{device_id}/commands`

> [!NOTE]
> These endpoints are part of Moen's official cloud API and may change without notice. The integration will be updated accordingly.

## Security

- Credentials are stored securely in Home Assistant's configuration
- All communication uses HTTPS/TLS
- No local network access required

## Contributing

This integration is based on reverse-engineering the official Moen mobile app. If you have additional information about the API or encounter issues, please:

1. Check the existing issues
2. Create a new issue with detailed information
3. Include relevant logs and network captures (sanitized)

### Development Setup

This project uses pre-commit hooks to ensure code quality and consistency. To set up the development environment:

#### Create and activate virtual environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

#### Install pre-commit
```bash
pip install pre-commit
```

#### Install git hooks
```bash
pre-commit install
```

#### Run pre-commit on all files
```bash
pre-commit run --all-files
```

The pre-commit hooks will automatically:
- Run **ruff** for code linting and formatting
- Run **mypy** for type checking
- Ensure code follows the project's style guidelines

> [!TIP]
> Pre-commit hooks will run automatically on every commit. If you want to commit code that doesn't pass the checks, use `git commit --no-verify` (not recommended for regular development).

#### Manual Testing
You can also run the linting tools manually:

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate  # On Windows

# Install test dependencies
pip install -r requirements-test.txt

# Run ruff (code linting)
ruff check custom_components

# Run mypy (type checking)
mypy custom_components
```

## Disclaimer

This integration is not officially supported by Moen. Use at your own risk. The authors are not responsible for any damage or issues that may arise from using this integration.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
