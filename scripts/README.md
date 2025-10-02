# Moen Smart Faucet API Test Scripts

This directory contains test scripts for the Moen Smart Faucet API integration.

## Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the test script:
   ```bash
   python test_moen_api.py
   ```

## Test Script Features

The `test_moen_api.py` script provides comprehensive testing of the Moen Smart Faucet API:

### Authentication
- Handles OAuth2 authentication flow
- Stores OAuth tokens securely in a git-ignored file (`moen_credentials.json`)
- Prompts for username/password on first run, then saves tokens
- Reuses stored OAuth tokens on subsequent runs (no password storage)

### API Testing
- **User Profile**: Retrieves and displays user account information
- **Locations**: Lists all available locations
- **Devices**: Lists VAK (smart faucet) devices, filtering out FLO devices
- **Temperature Definitions**: Gets temperature settings (hot, warm, cold)
- **Device Shadow**: Retrieves current device state and configuration
- **Usage Data**: Gets daily water usage statistics
- **Water Control**: Tests water flow control (with user confirmation)

### Safety Features
- Water control tests require explicit user confirmation
- Automatically stops water flow after testing
- Comprehensive error handling and logging

## Authentication

The script uses OAuth2 authentication:

**First Run:**
- Prompts for Client ID, Username, and Password
- Authenticates with Moen API to get OAuth tokens
- Saves OAuth tokens (access_token, refresh_token, etc.) to `moen_credentials.json`
- **Passwords are NOT stored** - only OAuth tokens are saved

**Subsequent Runs:**
- Uses stored OAuth tokens for authentication
- Automatically refreshes tokens when they expire
- No need to re-enter username/password

The token file (`moen_credentials.json`) is git-ignored for security.

## Usage Examples

### Basic API Testing
```bash
# Run all tests
python test_moen_api.py

# Test authentication only
python test_moen_api.py --auth-only

# Test device-related endpoints
python test_moen_api.py --devices

# Test water control (requires confirmation)
python test_moen_api.py --water-control

# List all available endpoints
python test_moen_api.py --list-endpoints

# Show help
python test_moen_api.py --help
```

### Quick Endpoint Testing
For testing individual endpoints quickly:
```bash
# Test specific methods
python test_endpoint.py "get_user_profile()"
python test_endpoint.py "list_devices()"
python test_endpoint.py "get_device_shadow('101046568')"
python test_endpoint.py "set_coldest('101046568')"
```

### Testing Specific Functions
The script includes interactive prompts for testing water control functions. Only proceed with water control tests if you're in a safe environment where water flow is acceptable.

## API Endpoints Tested

The script tests all major API endpoints documented in `../apis.md`:

1. **OAuth2 Token** - Authentication
2. **User Profile** - Account information
3. **Locations** - Property/location data
4. **Devices** - Smart faucet devices
5. **Temperature Definitions** - Temperature settings
6. **Device Shadow** - Current device state
7. **Usage Data** - Water usage statistics
8. **Session Data** - Device usage sessions
9. **Water Control** - Start/stop water flow
10. **Device Settings** - Configuration updates

## Troubleshooting

- **Authentication Errors**: Verify your credentials are correct
- **Network Errors**: Check your internet connection
- **Device Not Found**: Ensure your Moen smart water device is connected and registered
- **Permission Errors**: Make sure the script has write permissions for the credentials file

## Security Notes

- **OAuth tokens only**: Username and password are never stored
- Tokens are stored locally and are not transmitted anywhere except to Moen API
- The token file is git-ignored and should not be committed to version control
- Water control functions require explicit user confirmation for safety
- Tokens automatically expire and refresh as needed
