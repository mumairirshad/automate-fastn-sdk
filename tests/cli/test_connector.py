"""
Tests for: fastn connector (sync, ls, add, remove, run, schema)
"""
import subprocess
import os
import pytest

ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}


@pytest.mark.cli
@pytest.mark.connector
class TestConnectorSync:
    """Test 'fastn connector sync' command."""

    def test_connector_sync(self, require_auth):
        """TC-CLI-CON-001: 'fastn connector sync' downloads the registry successfully."""
        result = subprocess.run(
            ["fastn", "connector", "sync"],
            capture_output=True,
            text=True,
            timeout=120,
            env=ENV,
        )
        assert result.returncode == 0, f"connector sync failed: {result.stderr}"


@pytest.mark.cli
@pytest.mark.connector
class TestConnectorLs:
    """Test 'fastn connector ls' command."""

    def test_connector_ls(self, require_auth):
        """TC-CLI-CON-002: 'fastn connector ls' lists available connectors."""
        result = subprocess.run(
            ["fastn", "connector", "ls"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        assert result.returncode == 0, f"connector ls failed: {result.stderr}"
        output = result.stdout.strip()
        assert len(output) > 0, "connector ls returned empty output"

    def test_connector_ls_shows_connectors(self, require_auth):
        """TC-CLI-CON-003: 'fastn connector ls' output contains known connectors."""
        result = subprocess.run(
            ["fastn", "connector", "ls"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        output = result.stdout.lower()
        known = ["hubspot", "github", "jira", "gmail", "notion"]
        found = [c for c in known if c in output]
        assert len(found) > 0, (
            f"Expected at least one known connector in output. "
            f"Checked: {known}. Output: {result.stdout[:500]}"
        )

    def test_connector_ls_help(self):
        """TC-CLI-CON-004: 'fastn connector ls --help' shows usage."""
        result = subprocess.run(
            ["fastn", "connector", "ls", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0


@pytest.mark.cli
@pytest.mark.connector
class TestConnectorAdd:
    """Test 'fastn connector add' command."""

    def test_connector_add_hubspot(self, require_auth):
        """TC-CLI-CON-005: 'fastn connector add hubspot' succeeds."""
        result = subprocess.run(
            ["fastn", "connector", "add", "hubspot"],
            capture_output=True,
            text=True,
            timeout=60,
            env=ENV,
        )
        assert result.returncode == 0 or "already" in (result.stdout + result.stderr).lower(), (
            f"connector add hubspot failed: {result.stderr}"
        )

    def test_connector_add_invalid(self, require_auth):
        """TC-CLI-CON-006: 'fastn connector add nonexistent_xyz' fails gracefully."""
        result = subprocess.run(
            ["fastn", "connector", "add", "nonexistent_xyz_connector_12345"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        assert result.returncode != 0 or "not found" in (result.stdout + result.stderr).lower() or "error" in (result.stdout + result.stderr).lower(), (
            f"Expected error for nonexistent connector. Got: {result.stdout}"
        )

    def test_connector_add_help(self):
        """TC-CLI-CON-007: 'fastn connector add --help' shows usage."""
        result = subprocess.run(
            ["fastn", "connector", "add", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0


@pytest.mark.cli
@pytest.mark.connector
class TestConnectorRemove:
    """Test 'fastn connector remove' command."""

    def test_connector_remove_help(self):
        """TC-CLI-CON-008: 'fastn connector remove --help' shows usage."""
        result = subprocess.run(
            ["fastn", "connector", "remove", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0

    def test_connector_remove_nonexistent(self, require_auth):
        """TC-CLI-CON-009: Removing a non-installed connector fails gracefully."""
        result = subprocess.run(
            ["fastn", "connector", "remove", "nonexistent_xyz_connector_12345"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        assert result.returncode != 0 or "not found" in combined.lower() or "not installed" in combined.lower(), (
            f"Expected graceful error for removing nonexistent connector. Got: {combined}"
        )


@pytest.mark.cli
@pytest.mark.connector
class TestConnectorRun:
    """Test 'fastn connector run' command."""

    def test_connector_run_help(self):
        """TC-CLI-CON-010: 'fastn connector run --help' shows usage."""
        result = subprocess.run(
            ["fastn", "connector", "run", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0

    def test_connector_run_missing_args(self, require_auth):
        """TC-CLI-CON-011: 'fastn connector run' without args shows error or usage."""
        result = subprocess.run(
            ["fastn", "connector", "run"],
            capture_output=True,
            text=True,
            timeout=15,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        assert result.returncode != 0 or "usage" in combined.lower() or "missing" in combined.lower() or "error" in combined.lower()


@pytest.mark.cli
@pytest.mark.connector
class TestConnectorSchema:
    """Test 'fastn connector schema' command."""

    def test_connector_schema_help(self):
        """TC-CLI-CON-012: 'fastn connector schema --help' shows usage."""
        result = subprocess.run(
            ["fastn", "connector", "schema", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0

    def test_connector_schema_github(self, require_auth):
        """TC-CLI-CON-013: 'fastn connector schema github' shows JSON schema."""
        result = subprocess.run(
            ["fastn", "connector", "schema", "github"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        assert result.returncode == 0, f"connector schema github failed (exit {result.returncode}): {combined[:300]}"
        assert "401" not in combined, "Got 401 unauthorized — token may be invalid"
        assert "expired" not in combined.lower(), "Token expired in schema output"
        assert "github" in combined.lower(), f"Expected github content in schema output: {combined[:200]}"


@pytest.mark.cli
@pytest.mark.connector
class TestConnectorNoArgs:
    """Test 'fastn connector' with no subcommand."""

    def test_connector_no_args(self):
        """TC-CLI-CON-014: 'fastn connector' shows usage with subcommands."""
        result = subprocess.run(
            ["fastn", "connector"],
            capture_output=True,
            text=True,
            timeout=15,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        assert "ls" in combined.lower(), "Expected 'ls' subcommand in output"
        assert "sync" in combined.lower(), "Expected 'sync' subcommand in output"
        assert "run" in combined.lower(), "Expected 'run' subcommand in output"


@pytest.mark.cli
@pytest.mark.connector
class TestConnectorLsActive:
    """Test 'fastn connector ls --active' command."""

    def test_connector_ls_active(self, require_auth):
        """TC-CLI-CON-015: 'fastn connector ls --active' shows only active connectors."""
        result = subprocess.run(
            ["fastn", "connector", "ls", "--active"],
            capture_output=True,
            text=True,
            timeout=50,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        assert result.returncode == 0, f"connector ls --active failed (exit {result.returncode}): {combined[:300]}"
        assert "401" not in combined, "Got 401 unauthorized — token may be invalid"
        assert "expired" not in combined.lower(), "Token expired in ls --active output"
        assert "active connectors" in combined.lower(), f"Expected 'active connectors' in output: {combined[:200]}"


@pytest.mark.cli
@pytest.mark.connector
class TestConnectorDetail:
    """Test 'fastn connector <name>' for showing connector tools."""

    def test_connector_show_github(self, require_auth):
        """TC-CLI-CON-016: 'fastn connector github' shows tools for github connector."""
        result = subprocess.run(
            ["fastn", "connector", "github"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        assert "github" in combined.lower(), f"Expected 'github' in output. Got: {combined[:300]}"

    def test_connector_show_gmail(self, require_auth):
        """TC-CLI-CON-017: 'fastn connector gmail' shows tools for gmail connector."""
        result = subprocess.run(
            ["fastn", "connector", "gmail"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        assert result.returncode == 0, f"connector gmail failed (exit {result.returncode}): {combined[:300]}"
        assert "401" not in combined, "Got 401 unauthorized — token may be invalid"
        assert "expired" not in combined.lower(), "Token expired in connector gmail output"
        assert "gmail" in combined.lower(), f"Expected 'gmail' tools in output: {combined[:200]}"

    def test_connector_show_nonexistent(self, require_auth):
        """TC-CLI-CON-018: 'fastn connector nonexistent_xyz' fails gracefully."""
        result = subprocess.run(
            ["fastn", "connector", "nonexistent_xyz_00000"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        assert result.returncode != 0 or "not found" in combined.lower() or "error" in combined.lower()


@pytest.mark.cli
@pytest.mark.connector
class TestConnectorRunActual:
    """Test actual connector run execution."""

    def test_connector_run_gmail_list_tools(self, require_auth):
        """TC-CLI-CON-019: 'fastn connector run gmail' lists available Gmail tools."""
        # Run without a tool name — shows available tools (non-interactive, safe)
        # Previous version used wrong tool 'getmessages_from_gmail' + invalid --params flag
        result = subprocess.run(
            ["fastn", "connector", "run", "gmail"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        assert result.returncode == 0, f"connector run gmail failed (exit {result.returncode}): {combined[:300]}"
        assert "401" not in combined, "Got 401 unauthorized — token may be invalid"
        assert "expired" not in combined.lower(), "Token expired in connector run output"
        assert "gmail" in combined.lower(), f"Expected gmail tools listed in output: {combined[:200]}"

    @pytest.mark.xfail(reason="BUG-005: 'fastn connector run hubspot <tool>' returns 'Connector ID is required' — HubSpot OAuth connection not established in this project")
    def test_connector_run_hubspot_list_companies(self, require_auth):
        """TC-CLI-CON-020: 'fastn connector run hubspot hub_spot_list_companies' returns company list.
        NOTE: Fails with 'Connector ID is required' because HubSpot is not OAuth-connected.
        The tool name is correct; the issue is missing connector authorization on the server.
        """
        result = subprocess.run(
            ["fastn", "connector", "run", "hubspot", "hub_spot_list_companies"],
            input="\n5\n\n\n\n",  # skip optional fields, limit=5
            capture_output=True,
            text=True,
            timeout=60,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        assert result.returncode == 0, f"connector run hubspot hub_spot_list_companies failed: {combined[:400]}"
        assert "connector id is required" not in combined.lower(), (
            "BUG-005: HubSpot not connected — got 'Connector ID is required'"
        )
