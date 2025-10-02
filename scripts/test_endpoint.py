#!/usr/bin/env python3
"""Quick endpoint tester for Moen Smart Faucet API.

This script allows you to quickly test individual API endpoints.

Usage:
    python test_endpoint.py "get_user_profile()"
    python test_endpoint.py "list_devices()"
    python test_endpoint.py "set_coldest('101046568')"
"""

import sys
from pathlib import Path

# Add the scripts directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from moen_api_standalone import MoenAPI


def main():
    """Test a specific endpoint."""
    if len(sys.argv) != 2:
        print('Usage: python test_endpoint.py "method_name(args)"')
        print("\nExamples:")
        print('  python test_endpoint.py "get_user_profile()"')
        print('  python test_endpoint.py "list_devices()"')
        print("  python test_endpoint.py \"set_coldest('101046568')\"")
        sys.exit(1)

    # Get the method call from command line
    method_call = sys.argv[1]

    # Initialize API (will prompt for credentials if needed)
    print("Initializing Moen API...")
    api = MoenAPI("", "")  # Will be set by credentials loading

    # Load credentials
    credentials_file = Path(__file__).parent / "moen_credentials.json"
    if credentials_file.exists():
        import json

        with open(credentials_file) as f:
            creds = json.load(f)

        if "access_token" in creds:
            # Use stored tokens
            api.access_token = creds["access_token"]
            api.id_token = creds.get("id_token")
            api.refresh_token = creds.get("refresh_token")
            api.token_expiry = creds.get("expires_at", 0)

            if api.access_token:
                api.session.headers.update(
                    {"Authorization": f"Bearer {api.access_token}"}
                )

            # Check if token needs refresh
            import time
            if time.time() > api.token_expiry:
                if api.refresh_token:
                    print("Token expired, attempting refresh...")
                    if api._refresh_access_token():
                        print("✓ Token refreshed successfully")
                        # Save refreshed tokens
                        import json
                        refreshed_creds = {
                            "access_token": api.access_token,
                            "id_token": api.id_token,
                            "refresh_token": api.refresh_token,
                            "expires_at": api.token_expiry,
                        }
                        with open(credentials_file, "w") as f:
                            json.dump(refreshed_creds, f, indent=2)
                        print("✓ Refreshed tokens saved")
                    else:
                        print("✗ Token refresh failed")
                        sys.exit(1)
                else:
                    print("✗ Token expired and no refresh token available")
                    sys.exit(1)
            else:
                print("✓ Using stored OAuth tokens")
        else:
            print("No valid tokens found. Please run the main test script first.")
            sys.exit(1)
    else:
        print("No credentials found. Please run the main test script first.")
        sys.exit(1)

    # Execute the method call
    print(f"\nExecuting: {method_call}")
    print("-" * 50)

    try:
        # Use eval to execute the method call (safe in this context)
        result = eval(f"api.{method_call}")
        print("✓ Success!")
        print(f"Result: {result}")
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
