"""
Tests for: fastn --help and fastn <command> --help
"""
import subprocess
import pytest


@pytest.mark.cli
class TestMainHelp:
    """Test the main 'fastn --help' command."""

    def test_main_help(self):
        """TC-CLI-HELP-001: 'fastn --help' shows usage and all top-level commands."""
        result = subprocess.run(
            ["fastn", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0, f"fastn --help failed: {result.stderr}"
        output = result.stdout.lower()
        # Verify key commands are listed
        expected_commands = ["login", "logout", "connector", "flow", "version"]
        for cmd in expected_commands:
            assert cmd in output, f"Expected command '{cmd}' in help output"

    def test_main_no_args(self):
        """TC-CLI-HELP-002: 'fastn' with no args shows usage with all commands."""
        result = subprocess.run(
            ["fastn"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        combined = result.stdout + result.stderr
        assert len(combined.strip()) > 0, "Expected some output when running 'fastn' with no args"
        # Verify all top-level commands are listed
        expected = ["login", "logout", "whoami", "connector", "flow", "kit", "skill", "agent", "version"]
        for cmd in expected:
            assert cmd in combined.lower(), f"Expected '{cmd}' in main menu output"

    def test_connector_help(self):
        """TC-CLI-HELP-003: 'fastn connector --help' shows subcommands."""
        result = subprocess.run(
            ["fastn", "connector", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0
        output = result.stdout.lower()
        expected_subs = ["ls", "sync", "add", "run"]
        for sub in expected_subs:
            assert sub in output, f"Expected subcommand '{sub}' in connector help"

    def test_flow_help(self):
        """TC-CLI-HELP-004: 'fastn flow --help' shows subcommands."""
        result = subprocess.run(
            ["fastn", "flow", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0
        output = result.stdout.lower()
        expected_subs = ["ls", "run"]
        for sub in expected_subs:
            assert sub in output, f"Expected subcommand '{sub}' in flow help"

    def test_kit_help(self):
        """TC-CLI-HELP-005: 'fastn kit --help' shows subcommands."""
        result = subprocess.run(
            ["fastn", "kit", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0

    def test_verbose_flag(self):
        """TC-CLI-HELP-006: 'fastn --verbose version' accepts --verbose flag."""
        result = subprocess.run(
            ["fastn", "--verbose", "version"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0
