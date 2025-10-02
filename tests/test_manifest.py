"""Tests for the integration manifest and basic structure."""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from custom_components.moen_smart_water import __version__


class TestManifest:
    """Test cases for the integration manifest."""

    def test_manifest_exists(self):
        """Test that manifest.json exists."""
        manifest_path = Path(__file__).parent.parent / "custom_components" / "moen_smart_water" / "manifest.json"
        assert manifest_path.exists()

    def test_manifest_valid_json(self):
        """Test that manifest.json is valid JSON."""
        manifest_path = Path(__file__).parent.parent / "custom_components" / "moen_smart_water" / "manifest.json"

        with open(manifest_path) as f:
            manifest = json.load(f)

        assert isinstance(manifest, dict)

    def test_manifest_required_keys(self):
        """Test that manifest.json contains required keys."""
        manifest_path = Path(__file__).parent.parent / "custom_components" / "moen_smart_water" / "manifest.json"

        with open(manifest_path) as f:
            manifest = json.load(f)

        required_keys = [
            "domain",
            "name",
            "version",
            "codeowners",
            "config_flow",
            "dependencies",
            "documentation",
            "iot_class",
            "issue_tracker",
            "requirements"
        ]

        for key in required_keys:
            assert key in manifest, f"Missing required key: {key}"

    def test_manifest_domain(self):
        """Test that manifest domain is correct."""
        manifest_path = Path(__file__).parent.parent / "custom_components" / "moen_smart_water" / "manifest.json"

        with open(manifest_path) as f:
            manifest = json.load(f)

        assert manifest["domain"] == "moen_smart_water"

    def test_manifest_version_matches_init(self):
        """Test that manifest version matches __init__.py version."""
        manifest_path = Path(__file__).parent.parent / "custom_components" / "moen_smart_water" / "manifest.json"

        with open(manifest_path) as f:
            manifest = json.load(f)

        assert manifest["version"] == __version__

    def test_manifest_requirements(self):
        """Test that manifest has valid requirements."""
        manifest_path = Path(__file__).parent.parent / "custom_components" / "moen_smart_water" / "manifest.json"

        with open(manifest_path) as f:
            manifest = json.load(f)

        assert "requirements" in manifest
        assert isinstance(manifest["requirements"], list)
        assert len(manifest["requirements"]) > 0
        assert "requests" in manifest["requirements"][0]


class TestHACSManifest:
    """Test cases for the HACS manifest."""

    def test_hacs_json_exists(self):
        """Test that hacs.json exists."""
        hacs_path = Path(__file__).parent.parent / "hacs.json"
        assert hacs_path.exists()

    def test_hacs_json_valid(self):
        """Test that hacs.json is valid JSON."""
        hacs_path = Path(__file__).parent.parent / "hacs.json"

        with open(hacs_path) as f:
            hacs_config = json.load(f)

        assert isinstance(hacs_config, dict)

    def test_hacs_json_required_keys(self):
        """Test that hacs.json contains required keys."""
        hacs_path = Path(__file__).parent.parent / "hacs.json"

        with open(hacs_path) as f:
            hacs_config = json.load(f)

        required_keys = [
            "name",
            "content_in_root",
            "filename",
            "country",
            "homeassistant",
            "render_readme"
        ]

        for key in required_keys:
            assert key in hacs_config, f"Missing required key: {key}"

    def test_hacs_json_no_invalid_keys(self):
        """Test that hacs.json doesn't contain invalid keys."""
        hacs_path = Path(__file__).parent.parent / "hacs.json"

        with open(hacs_path) as f:
            hacs_config = json.load(f)

        # iot_class should not be in hacs.json
        assert "iot_class" not in hacs_config


class TestServicesYAML:
    """Test cases for the services.yaml file."""

    def test_services_yaml_exists(self):
        """Test that services.yaml exists."""
        services_path = Path(__file__).parent.parent / "custom_components" / "moen_smart_water" / "services.yaml"
        assert services_path.exists()

    def test_services_yaml_valid_yaml(self):
        """Test that services.yaml is valid YAML."""
        import yaml

        services_path = Path(__file__).parent.parent / "custom_components" / "moen_smart_water" / "services.yaml"

        with open(services_path) as f:
            services = yaml.safe_load(f)

        assert isinstance(services, dict)

    def test_services_yaml_has_services(self):
        """Test that services.yaml contains expected services."""
        import yaml

        services_path = Path(__file__).parent.parent / "custom_components" / "moen_smart_water" / "services.yaml"

        with open(services_path) as f:
            services = yaml.safe_load(f)

        expected_services = [
            "dispense_water",
            "stop_dispensing",
            "get_device_status",
            "get_user_profile",
            "set_temperature",
            "set_flow_rate"
        ]

        for service in expected_services:
            assert service in services, f"Missing service: {service}"
