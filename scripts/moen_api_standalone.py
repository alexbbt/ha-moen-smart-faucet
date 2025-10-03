#!/usr/bin/env python3
"""Standalone API module for Moen Smart Water integration.

This module provides a standalone version of the MoenAPI class
that can be imported by test scripts.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import the actual API class and constants from the integration
from custom_components.moen_smart_water.api import MoenAPI, CLIENT_ID

# Re-export the class and constants for easy importing
__all__ = ['MoenAPI', 'CLIENT_ID']
