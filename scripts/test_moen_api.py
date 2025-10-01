#!/usr/bin/env python3
"""Test script for Moen Smart Faucet API.

This script provides an easy way to test all Moen API endpoints.
It handles authentication flow and stores OAuth tokens securely.

Usage:
    python test_moen_api.py                    # Run all tests
    python test_moen_api.py --auth-only        # Test authentication only
    python test_moen_api.py --devices          # Test device-related endpoints
    python test_moen_api.py --water-control    # Test water control (with confirmation)
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict

# Import the standalone API class
from moen_api_standalone import MoenAPI


class MoenAPITester:
    """Test class for Moen API operations."""

    def __init__(self):
        """Initialize the tester."""
        self.credentials_file = Path(__file__).parent / "moen_credentials.json"
        self.api: MoenAPI | None = None

    def load_credentials(self) -> Dict[str, str] | None:
        """Load credentials from file if it exists."""
        if self.credentials_file.exists():
            try:
                with open(self.credentials_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading credentials: {e}")
                return None
        return None

    def save_credentials(self, credentials: Dict[str, str]) -> None:
        """Save credentials to file."""
        try:
            with open(self.credentials_file, 'w') as f:
                json.dump(credentials, f, indent=2)
            print(f"Credentials saved to {self.credentials_file}")
        except IOError as e:
            print(f"Error saving credentials: {e}")

    def save_tokens(self, tokens: Dict[str, Any]) -> None:
        """Save OAuth tokens to file."""
        try:
            with open(self.credentials_file, 'w') as f:
                json.dump(tokens, f, indent=2)
            print(f"OAuth tokens saved to {self.credentials_file}")
        except IOError as e:
            print(f"Error saving tokens: {e}")

    def get_credentials(self) -> Dict[str, str]:
        """Get credentials from user input or file."""
        # Try to load existing tokens first
        stored_data = self.load_credentials()

        if stored_data and 'access_token' in stored_data:
            print("Found existing OAuth tokens.")
            print(f"Client ID: {stored_data.get('client_id', 'unknown')}")
            print(f"Token expires: {stored_data.get('expires_at', 'unknown')}")

            use_existing = input("\nUse existing tokens? (y/n): ").lower().strip()
            if use_existing == 'y':
                return stored_data

        # Get new credentials for authentication
        print("\nEnter Moen API credentials for authentication:")
        client_id = input("Client ID: ").strip()
        username = input("Username (email): ").strip()
        password = input("Password: ").strip()

        credentials = {
            'client_id': client_id,
            'username': username,
            'password': password
        }

        return credentials

    def initialize_api(self) -> bool:
        """Initialize the API with credentials or tokens."""
        try:
            credentials = self.get_credentials()

            # Check if we have stored tokens
            if 'access_token' in credentials:
                # Initialize API with tokens
                self.api = MoenAPI(
                    client_id=credentials['client_id'],
                    username="",  # Not needed when using tokens
                    password=""   # Not needed when using tokens
                )
                # Set the tokens directly
                self.api.access_token = credentials['access_token']
                self.api.id_token = credentials.get('id_token')
                self.api.refresh_token = credentials.get('refresh_token')
                self.api.token_expiry = credentials.get('expires_at', 0)

                # Update session headers
                if self.api.access_token:
                    self.api.session.headers.update({
                        "Authorization": f"Bearer {self.api.access_token}"
                    })

                print("✓ Using stored OAuth tokens")
            else:
                # Initialize API with username/password for authentication
                self.api = MoenAPI(
                    client_id=credentials['client_id'],
                    username=credentials['username'],
                    password=credentials['password']
                )
                print("✓ Using username/password authentication")

            return True
        except Exception as e:
            print(f"Error initializing API: {e}")
            return False

    def test_authentication(self) -> bool:
        """Test authentication."""
        print("\n=== Testing Authentication ===")
        try:
            # Only login if we don't have valid tokens
            if not self.api.access_token or time.time() > self.api.token_expiry:
                login_result = self.api.login()
                print("✓ Authentication successful")

                # Save tokens for future use
                if login_result and 'token' in login_result:
                    token_data = login_result['token']
                    tokens_to_save = {
                        'client_id': self.api.client_id,
                        'access_token': token_data.get('access_token'),
                        'id_token': token_data.get('id_token'),
                        'refresh_token': token_data.get('refresh_token'),
                        'expires_at': self.api.token_expiry,
                        'expires_in': token_data.get('expires_in', 3600)
                    }
                    self.save_tokens(tokens_to_save)
                    print("✓ OAuth tokens saved for future use")
            else:
                print("✓ Using existing valid tokens")

            return True
        except Exception as e:
            print(f"✗ Authentication failed: {e}")
            return False

    def test_user_profile(self) -> bool:
        """Test getting user profile."""
        print("\n=== Testing User Profile ===")
        try:
            profile = self.api.get_user_profile()
            print(f"✓ User profile retrieved for: {profile.get('email', 'unknown')}")
            print(f"  Name: {profile.get('firstName', '')} {profile.get('lastName', '')}")
            print(f"  Account ID: {profile.get('account', {}).get('id', 'unknown')}")
            return True
        except Exception as e:
            print(f"✗ Failed to get user profile: {e}")
            return False

    def test_locations(self) -> bool:
        """Test getting locations."""
        print("\n=== Testing Locations ===")
        try:
            locations = self.api.get_locations()
            print(f"✓ Retrieved {len(locations)} locations")
            for location in locations:
                print(f"  - {location.get('name', 'Unknown')} ({location.get('id', 'unknown')})")
                print(f"    Address: {location.get('address', 'Unknown')}")
                print(f"    City: {location.get('city', 'Unknown')}, {location.get('state', 'Unknown')}")
            return True
        except Exception as e:
            print(f"✗ Failed to get locations: {e}")
            return False

    def test_devices(self) -> bool:
        """Test getting devices."""
        print("\n=== Testing Devices ===")
        try:
            devices = self.api.list_devices()
            print(f"✓ Retrieved {len(devices)} VAK devices")
            for device in devices:
                print(f"  - {device.get('nickname', 'Unknown')} ({device.get('duid', 'unknown')})")
                print(f"    Client ID: {device.get('clientId', 'unknown')}")
                print(f"    Connected: {device.get('connected', False)}")
                print(f"    State: {device.get('state', 'unknown')}")
                print(f"    Temperature: {device.get('temperature', 'unknown')}°C")
                print(f"    Volume: {device.get('volume', 'unknown')} μL")
            return True
        except Exception as e:
            print(f"✗ Failed to get devices: {e}")
            return False

    def test_temperature_definitions(self) -> bool:
        """Test getting temperature definitions."""
        print("\n=== Testing Temperature Definitions ===")
        try:
            user_details = self.api.get_user_details_and_temperature_definitions()
            temp_defs = user_details.get('temperatureDefinitions', {})
            print(f"✓ Retrieved temperature definitions:")
            for key, value in temp_defs.items():
                print(f"  - {key}: {value}")
            return True
        except Exception as e:
            print(f"✗ Failed to get temperature definitions: {e}")
            return False

    def test_device_shadow(self, client_id: str) -> bool:
        """Test getting device shadow."""
        print(f"\n=== Testing Device Shadow for {client_id} ===")
        try:
            shadow = self.api.get_device_shadow(client_id)
            state = shadow.get('state', {})
            reported = state.get('reported', {})
            desired = state.get('desired', {})

            print("✓ Device shadow retrieved:")
            print(f"  Current State: {reported.get('state', 'unknown')}")
            print(f"  Temperature: {reported.get('temperature', 'unknown')}°C")
            print(f"  Volume: {reported.get('volume', 'unknown')} μL")
            print(f"  Connected: {reported.get('connected', False)}")
            print(f"  Safety Mode: {reported.get('safetyModeEnabled', False)}")
            print(f"  Child Mode: {reported.get('childModeEnabled', False)}")

            if desired:
                print("  Desired Settings:")
                for key, value in desired.items():
                    print(f"    - {key}: {value}")

            return True
        except Exception as e:
            print(f"✗ Failed to get device shadow: {e}")
            return False

    def test_water_control(self, client_id: str) -> bool:
        """Test water control functions."""
        print(f"\n=== Testing Water Control for {client_id} ===")

        try:
            # Test getting current state
            print("Getting current device state...")
            shadow = self.api.get_device_shadow(client_id)
            current_state = shadow.get('state', {}).get('reported', {}).get('state', 'unknown')
            print(f"Current state: {current_state}")

            # Test stopping water (in case it's running)
            print("Stopping water flow...")
            result = self.api.stop_water_flow(client_id)
            print(f"Stop result: {result}")

            # Test setting coldest temperature
            print("Setting coldest temperature...")
            result = self.api.set_coldest(client_id)
            print(f"Coldest result: {result}")

            # Wait a moment
            import time
            print("Waiting 3 seconds...")
            time.sleep(3)

            # Test stopping again
            print("Stopping water flow...")
            result = self.api.stop_water_flow(client_id)
            print(f"Stop result: {result}")

            print("✓ Water control test completed")
            return True

        except Exception as e:
            print(f"✗ Water control test failed: {e}")
            return False

    def test_usage_data(self, client_id: str) -> bool:
        """Test getting usage data."""
        print(f"\n=== Testing Usage Data for {client_id} ===")
        try:
            usage = self.api.get_daily_usage(client_id)
            current = usage.get('current', {})
            total_usage = current.get('total', 0)
            print(f"✓ Daily usage retrieved: {total_usage} μL total")

            usage_by_hour = current.get('usage', {})
            if usage_by_hour:
                print("  Usage by hour:")
                for hour, amount in usage_by_hour.items():
                    if amount > 0:
                        print(f"    {hour}:00 - {amount} μL")

            return True
        except Exception as e:
            print(f"✗ Failed to get usage data: {e}")
            return False

    def run_tests(self, test_type: str = "all") -> None:
        """Run specified API tests."""
        print("Moen Smart Faucet API Tester")
        print("=" * 40)

        if not self.initialize_api():
            print("Failed to initialize API. Exiting.")
            return

        # Test authentication
        if not self.test_authentication():
            print("Authentication failed. Exiting.")
            return

        if test_type in ["all", "auth-only"]:
            print("\n✓ Authentication test completed!")
            if test_type == "auth-only":
                return

        # Test basic API calls
        if test_type in ["all", "basic", "devices"]:
            self.test_user_profile()
            self.test_locations()
            self.test_devices()
            self.test_temperature_definitions()

        # Test device-specific endpoints
        if test_type in ["all", "devices", "water-control"]:
            devices = self.api.get_cached_devices()
            if devices:
                device = devices[0]  # Use first device
                client_id = device.get('clientId')

                if client_id:
                    self.test_device_shadow(client_id)
                    self.test_usage_data(client_id)

                    if test_type in ["all", "water-control"]:
                        # Ask user if they want to test water control
                        test_water = input(f"\nTest water control for {device.get('nickname', 'device')}? (y/n): ").lower().strip()
                        if test_water == 'y':
                            self.test_water_control(client_id)
                else:
                    print("No client ID found for device testing")
            else:
                print("No devices found for testing")

        print("\n" + "=" * 40)
        print("API testing completed!")

    def test_endpoint(self, endpoint_name: str, test_func, *args, **kwargs) -> bool:
        """Helper method to test individual endpoints with consistent output."""
        print(f"\n=== Testing {endpoint_name} ===")
        try:
            result = test_func(*args, **kwargs)
            print(f"✓ {endpoint_name} test passed")
            return True
        except Exception as e:
            print(f"✗ {endpoint_name} test failed: {e}")
            return False

    def list_available_endpoints(self) -> None:
        """List all available API endpoints for testing."""
        print("\nAvailable API Endpoints:")
        print("-" * 30)
        print("Authentication:")
        print("  - login()")
        print("  - get_user_profile()")
        print("\nDevice Management:")
        print("  - get_locations()")
        print("  - list_devices()")
        print("  - get_device_details(device_id)")
        print("  - get_device_shadow(client_id)")
        print("\nWater Control:")
        print("  - start_water_flow(client_id, temperature, flow_rate)")
        print("  - stop_water_flow(client_id)")
        print("  - set_coldest(client_id)")
        print("  - set_hottest(client_id)")
        print("  - set_specific_temperature(client_id, temp_celsius)")
        print("\nAnalytics:")
        print("  - get_daily_usage(client_id)")
        print("  - get_session_data(client_id)")
        print("\nSettings:")
        print("  - update_device_settings(client_id, settings)")
        print("  - set_freeze_enable(client_id, enabled)")
        print("  - set_timeouts(client_id, ...)")
        print("  - set_flow_rate(client_id, rate)")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Test Moen Smart Faucet API endpoints",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_moen_api.py                    # Run all tests
  python test_moen_api.py --auth-only        # Test authentication only
  python test_moen_api.py --devices          # Test device-related endpoints
  python test_moen_api.py --water-control    # Test water control (with confirmation)
        """
    )

    parser.add_argument(
        "--auth-only",
        action="store_true",
        help="Test authentication only"
    )
    parser.add_argument(
        "--devices",
        action="store_true",
        help="Test device-related endpoints"
    )
    parser.add_argument(
        "--water-control",
        action="store_true",
        help="Test water control functions (requires confirmation)"
    )
    parser.add_argument(
        "--list-endpoints",
        action="store_true",
        help="List all available API endpoints"
    )

    args = parser.parse_args()

    # Handle list endpoints option
    if args.list_endpoints:
        tester = MoenAPITester()
        tester.list_available_endpoints()
        return

    # Determine test type based on arguments
    if args.auth_only:
        test_type = "auth-only"
    elif args.devices:
        test_type = "devices"
    elif args.water_control:
        test_type = "water-control"
    else:
        test_type = "all"

    tester = MoenAPITester()
    tester.run_tests(test_type)


if __name__ == "__main__":
    main()
