"""
Tests for: fastn kit (ls, get, config)
"""
import subprocess
import os
import pytest

ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}


@pytest.mark.cli
@pytest.mark.kit
class TestKitLs:
    """Test 'fastn kit ls' command."""

    def test_kit_ls(self, require_auth):
        """TC-CLI-KIT-001: 'fastn kit ls' returns list of kit connectors."""
        result = subprocess.run(
            ["fastn", "kit", "ls"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        assert result.returncode == 0, f"kit ls failed: {result.stderr}"

    def test_kit_ls_help(self):
        """TC-CLI-KIT-002: 'fastn kit ls --help' shows usage."""
        result = subprocess.run(
            ["fastn", "kit", "ls", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0


@pytest.mark.cli
@pytest.mark.kit
class TestKitGet:
    """Test 'fastn kit get' command."""

    def test_kit_get_help(self):
        """TC-CLI-KIT-003: 'fastn kit get --help' shows usage."""
        result = subprocess.run(
            ["fastn", "kit", "get", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0


@pytest.mark.cli
@pytest.mark.kit
class TestKitConfig:
    """Test 'fastn kit config' command."""

    def test_kit_config_help(self):
        """TC-CLI-KIT-004: 'fastn kit config --help' shows usage."""
        result = subprocess.run(
            ["fastn", "kit", "config", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0

    def test_kit_config_show(self, require_auth):
        """TC-CLI-KIT-005: 'fastn kit config' shows current configuration."""
        result = subprocess.run(
            ["fastn", "kit", "config"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        assert result.returncode == 0, f"kit config failed (exit {result.returncode}): {combined[:300]}"
        assert "401" not in combined, "Got 401 unauthorized — token may be invalid"
        assert "expired" not in combined.lower(), "Token expired in kit config output"
        assert "unauthorized" not in combined.lower(), "Unauthorized error in kit config output"


@pytest.mark.cli
@pytest.mark.kit
class TestKitNoArgs:
    """Test 'fastn kit' with no subcommand."""

    def test_kit_no_args(self):
        """TC-CLI-KIT-006: 'fastn kit' shows usage with subcommands."""
        result = subprocess.run(
            ["fastn", "kit"],
            capture_output=True,
            text=True,
            timeout=15,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        assert "ls" in combined.lower(), "Expected 'ls' subcommand in kit help"
        assert "config" in combined.lower(), "Expected 'config' subcommand in kit help"


@pytest.mark.cli
@pytest.mark.kit
class TestKitGetActual:
    """Test actual kit get operations."""

    def test_kit_get_gmail(self, require_auth):
        """TC-CLI-KIT-007: 'fastn kit get Gmail' returns connector details."""
        result = subprocess.run(
            ["fastn", "kit", "get", "Gmail"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        assert result.returncode == 0, f"kit get Gmail failed (exit {result.returncode}): {combined[:300]}"
        assert "401" not in combined, "Got 401 unauthorized — token may be invalid"
        assert "expired" not in combined.lower(), "Token expired in kit get Gmail output"
        assert "gmail" in combined.lower(), f"Expected Gmail content in output: {combined[:200]}"

    def test_kit_get_nonexistent(self, require_auth):
        """TC-CLI-KIT-008: 'fastn kit get nonexistent' fails with 'not found' error."""
        result = subprocess.run(
            ["fastn", "kit", "get", "nonexistent_kit_xyz"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        # Must fail — previous assertion had `or len(combined) > 0` which always passes
        assert result.returncode != 0, f"Expected non-zero exit for nonexistent kit. Got 0: {combined[:200]}"
        assert "not found" in combined.lower() or "error" in combined.lower(), (
            f"Expected 'not found'/'error' message. Got: {combined[:200]}"
        )
        # Even for a not-found error, auth must still be valid — not a token issue
        assert "401" not in combined, "Got 401 — this is an auth failure, not a not-found error"
        assert "expired" not in combined.lower(), "Token expired — not a not-found error"


@pytest.mark.cli
@pytest.mark.kit
class TestKitConfigContent:
    """Test 'fastn kit config' content when kit tools are connected."""

    @pytest.mark.xfail(reason="BUG-006: 'fastn kit config' returns 'No Connect Kit configuration found' even when Gmail/HubSpot are connected via kit ls")
    def test_kit_config_shows_connected_tools(self, require_auth):
        """TC-CLI-KIT-009: 'fastn kit config' returns config when kit tools are connected.
        NOTE: 'fastn kit ls' shows Gmail and HubSpot connected, but 'fastn kit config'
        returns empty — server-side bug where kit config endpoint ignores connected tools.
        """
        result = subprocess.run(
            ["fastn", "kit", "config"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        assert result.returncode == 0
        assert "no connect kit configuration found" not in combined.lower(), (
            "BUG-006: kit config returns empty despite Gmail/HubSpot being connected"
        )
