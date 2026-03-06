"""
Tests for: fastn version
"""
import subprocess
import re
import pytest


@pytest.mark.cli
class TestVersionCommand:
    """Test the 'fastn version' CLI command."""

    def test_version_returns_success(self):
        """TC-CLI-VER-001: 'fastn version' exits with code 0."""
        result = subprocess.run(
            ["fastn", "version"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}. stderr: {result.stderr}"

    def test_version_output_format(self):
        """TC-CLI-VER-002: Output matches 'Fastn SDK vX.Y.Z' format."""
        result = subprocess.run(
            ["fastn", "version"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        output = result.stdout.strip()
        assert re.search(r"Fastn SDK v\d+\.\d+\.\d+", output), (
            f"Version output does not match expected pattern. Got: {output}"
        )

    def test_version_shows_current_version(self):
        """TC-CLI-VER-003: Version output contains '0.3.2' (current installed)."""
        result = subprocess.run(
            ["fastn", "version"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert "0.3.2" in result.stdout, f"Expected version 0.3.2 in output. Got: {result.stdout}"

    def test_version_shows_registry_info(self):
        """TC-CLI-VER-004: Version output includes registry version and last synced fields."""
        result = subprocess.run(
            ["fastn", "version"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        output = result.stdout.strip()
        assert "Registry version" in output, f"Missing 'Registry version' in output: {output}"
        assert "Last synced" in output, f"Missing 'Last synced' in output: {output}"
