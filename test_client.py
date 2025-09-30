#!/usr/bin/env python3
"""Test script for Moen Faucet client."""

import asyncio
import logging
import sys
from pathlib import Path

# Add the custom_components directory to the path
sys.path.insert(0, str(Path(__file__).parent / "custom_components"))

from moen_faucet.client import MoenClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_client():
    """Test the Moen client with user credentials."""
    print("Moen Faucet Client Test")
    print("=" * 30)

    # Get credentials from user
    client_id = input("Enter your Client ID (or press Enter for default 'moen_mobile_app'): ").strip()
    if not client_id:
        client_id = "moen_mobile_app"
        print("Using default client ID: moen_mobile_app")

    username = input("Enter your username (email): ").strip()
    password = input("Enter your password: ").strip()

    if not all([username, password]):
        print("Error: Username and password are required")
        return

    # Create client
    client = MoenClient(client_id, username, password)

    try:
        # Test login
        print("\n1. Testing login...")
        login_result = await asyncio.get_event_loop().run_in_executor(None, client.login)
        print(f"✓ Login successful: {login_result}")

        # Test device list
        print("\n2. Getting devices...")
        devices = await asyncio.get_event_loop().run_in_executor(None, client.list_devices)
        print(f"✓ Found {len(devices)} devices:")
        for i, device in enumerate(devices, 1):
            device_id = device.get("id", device.get("device_id", "unknown"))
            device_name = device.get("name", f"Device {i}")
            print(f"  {i}. {device_name} (ID: {device_id})")

        if devices:
            # Test device status
            device_id = devices[0].get("id", devices[0].get("device_id"))
            print(f"\n3. Getting status for device {device_id}...")
            status = await asyncio.get_event_loop().run_in_executor(
                None, client.get_device_status, device_id
            )
            print(f"✓ Device status: {status}")

            # Test dispense command (dry run - don't actually dispense)
            print(f"\n4. Testing dispense command for device {device_id}...")
            print("   (This is a dry run - no water will be dispensed)")

            # You can uncomment the following lines to actually test dispense
            # try:
            #     result = await asyncio.get_event_loop().run_in_executor(
            #         None, client.start_dispense, device_id, 50, 10
            #     )
            #     print(f"✓ Dispense command sent: {result}")
            # except Exception as e:
            #     print(f"✗ Dispense command failed: {e}")

        print("\n✓ All tests completed successfully!")

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        logger.exception("Test failed")


if __name__ == "__main__":
    asyncio.run(test_client())
