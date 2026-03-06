"""
Tests for: fastn flow (ls, generate, deploy, run, schema, get-run, update, delete)
"""
import subprocess
import os
import pytest

ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}


@pytest.mark.cli
@pytest.mark.flow
class TestFlowLs:
    """Test 'fastn flow ls' command."""

    def test_flow_ls(self, require_auth):
        """TC-CLI-FLOW-001: 'fastn flow ls' lists flows."""
        result = subprocess.run(
            ["fastn", "flow", "ls"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        assert result.returncode == 0, f"flow ls failed: {result.stderr}"

    def test_flow_ls_help(self):
        """TC-CLI-FLOW-002: 'fastn flow ls --help' shows usage."""
        result = subprocess.run(
            ["fastn", "flow", "ls", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0


@pytest.mark.cli
@pytest.mark.flow
class TestFlowGetRun:
    """Test 'fastn flow get-run' command."""

    def test_flow_get_run_help(self):
        """TC-CLI-FLOW-003: 'fastn flow get-run --help' shows usage."""
        result = subprocess.run(
            ["fastn", "flow", "get-run", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0

    def test_flow_get_run_invalid_id(self, require_auth):
        """TC-CLI-FLOW-004: 'fastn flow get-run' with invalid ID fails gracefully."""
        result = subprocess.run(
            ["fastn", "flow", "get-run", "nonexistent-run-id-00000"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        assert result.returncode != 0 or "not found" in combined.lower() or "error" in combined.lower()


@pytest.mark.cli
@pytest.mark.flow
class TestFlowDeploy:
    """Test 'fastn flow deploy' command."""

    def test_flow_deploy_help(self):
        """TC-CLI-FLOW-005: 'fastn flow deploy --help' shows usage."""
        result = subprocess.run(
            ["fastn", "flow", "deploy", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0


@pytest.mark.cli
@pytest.mark.flow
class TestFlowRun:
    """Test 'fastn flow run' command."""

    def test_flow_run_help(self):
        """TC-CLI-FLOW-006: 'fastn flow run --help' shows usage."""
        result = subprocess.run(
            ["fastn", "flow", "run", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0

    def test_flow_run_missing_id(self, require_auth):
        """TC-CLI-FLOW-007: 'fastn flow run' without flow_name shows error."""
        result = subprocess.run(
            ["fastn", "flow", "run"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        combined = result.stdout + result.stderr
        assert result.returncode != 0 or "missing" in combined.lower() or "usage" in combined.lower() or "error" in combined.lower()


@pytest.mark.cli
@pytest.mark.flow
class TestFlowGenerate:
    """Test 'fastn flow generate' command."""

    def test_flow_generate_help(self):
        """TC-CLI-FLOW-008: 'fastn flow generate --help' shows usage."""
        result = subprocess.run(
            ["fastn", "flow", "generate", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0


@pytest.mark.cli
@pytest.mark.flow
class TestFlowSchema:
    """Test 'fastn flow schema' command."""

    def test_flow_schema_help(self):
        """TC-CLI-FLOW-009: 'fastn flow schema --help' shows usage."""
        result = subprocess.run(
            ["fastn", "flow", "schema", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0


@pytest.mark.cli
@pytest.mark.flow
class TestFlowUpdate:
    """Test 'fastn flow update' command."""

    def test_flow_update_help(self):
        """TC-CLI-FLOW-010: 'fastn flow update --help' shows usage."""
        result = subprocess.run(
            ["fastn", "flow", "update", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0


@pytest.mark.cli
@pytest.mark.flow
class TestFlowDelete:
    """Test 'fastn flow delete' command."""

    def test_flow_delete_help(self):
        """TC-CLI-FLOW-011: 'fastn flow delete --help' shows usage."""
        result = subprocess.run(
            ["fastn", "flow", "delete", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0


@pytest.mark.cli
@pytest.mark.flow
class TestFlowNoArgs:
    """Test 'fastn flow' with no subcommand."""

    def test_flow_no_args(self):
        """TC-CLI-FLOW-012: 'fastn flow' shows usage with subcommands."""
        result = subprocess.run(
            ["fastn", "flow"],
            capture_output=True,
            text=True,
            timeout=15,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        assert "ls" in combined.lower(), "Expected 'ls' subcommand in flow help"
        assert "run" in combined.lower(), "Expected 'run' subcommand in flow help"


@pytest.mark.cli
@pytest.mark.flow
class TestFlowLsActive:
    """Test 'fastn flow ls --status active'."""

    def test_flow_ls_status_active(self, require_auth):
        """TC-CLI-FLOW-013: 'fastn flow ls --status active' filters by status."""
        result = subprocess.run(
            ["fastn", "flow", "ls", "--status", "active"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        assert result.returncode == 0, f"flow ls --status active failed (exit {result.returncode}): {combined[:300]}"
        assert "401" not in combined, "Got 401 unauthorized — token may be invalid"
        assert "expired" not in combined.lower(), "Token expired in flow ls --status active output"
        assert "unauthorized" not in combined.lower(), "Unauthorized error in flow ls output"


@pytest.mark.cli
@pytest.mark.flow
class TestFlowRunActual:
    """Test actual flow run execution."""

    def test_flow_run_testflow(self, require_auth):
        """TC-CLI-FLOW-014: 'fastn flow run testFlow' executes successfully.
        NOTE: BUG-003 (UnicodeEncodeError on ✓ char) only triggers when writing to
        the Windows cp1252 console directly. With capture_output=True and
        PYTHONIOENCODING=utf-8 in ENV the subprocess buffer handles it fine — exit 0.
        """
        result = subprocess.run(
            ["fastn", "flow", "run", "testFlow"],
            capture_output=True,
            text=True,
            timeout=60,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        assert "401" not in combined, "Got 401 unauthorized — token may be invalid"
        assert "expired" not in combined.lower(), "Token expired in flow run output"
        assert "not authenticated" not in combined.lower(), "Auth failure in flow run output"
        assert result.returncode == 0, f"flow run testFlow failed (exit {result.returncode}): {combined[:400]}"

    def test_flow_run_nonexistent(self, require_auth):
        """TC-CLI-FLOW-015: 'fastn flow run nonexistent_flow' fails gracefully."""
        result = subprocess.run(
            ["fastn", "flow", "run", "nonexistent_flow_xyz"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        assert result.returncode != 0 or "not found" in combined.lower() or "error" in combined.lower()


@pytest.mark.cli
@pytest.mark.flow
class TestFlowSchemaActual:
    """Test actual flow schema retrieval."""

    def test_flow_schema_testflow(self, require_auth):
        """TC-CLI-FLOW-016: 'fastn flow schema testFlow' shows input/output schema."""
        result = subprocess.run(
            ["fastn", "flow", "schema", "testFlow"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        assert result.returncode == 0, f"flow schema testFlow failed (exit {result.returncode}): {combined[:300]}"
        assert "401" not in combined, "Got 401 unauthorized — token may be invalid"
        assert "expired" not in combined.lower(), "Token expired in flow schema output"
        assert "testflow" in combined.lower() or "inputschema" in combined.lower(), (
            f"Expected testFlow schema content in output: {combined[:200]}"
        )

    def test_flow_schema_nonexistent(self, require_auth):
        """TC-CLI-FLOW-017: 'fastn flow schema nonexistent' fails gracefully."""
        result = subprocess.run(
            ["fastn", "flow", "schema", "nonexistent_flow_xyz"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        assert result.returncode != 0 or "not found" in combined.lower() or "error" in combined.lower()


@pytest.mark.cli
@pytest.mark.flow
class TestFlowDeployActual:
    """Test actual flow deploy execution."""

    def test_flow_deploy_live(self, require_auth):
        """TC-CLI-FLOW-018: 'fastn flow deploy testFlow -s LIVE' deploys flow."""
        result = subprocess.run(
            ["fastn", "flow", "deploy", "testFlow", "-s", "LIVE"],
            capture_output=True,
            text=True,
            timeout=60,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        assert result.returncode == 0, f"flow deploy failed: {combined}"
        assert "deployed" in combined.lower() or "testflow" in combined.lower()

    def test_flow_deploy_nonexistent(self, require_auth):
        """TC-CLI-FLOW-019: 'fastn flow deploy nonexistent' fails gracefully."""
        result = subprocess.run(
            ["fastn", "flow", "deploy", "nonexistent_flow_xyz", "-s", "LIVE"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        assert result.returncode != 0 or "not found" in combined.lower() or "error" in combined.lower()


@pytest.mark.cli
@pytest.mark.flow
class TestFlowGetRunActual:
    """Test actual flow get-run execution."""

    @pytest.mark.xfail(reason="BUG-004: /api/flows/get_run returns 401 or 'resource does not exist' for valid token")
    def test_flow_get_run_actual(self, require_auth):
        """TC-CLI-FLOW-020: 'fastn flow get-run <run_id>' retrieves run status."""
        result = subprocess.run(
            ["fastn", "flow", "get-run", "testFlow"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        assert result.returncode == 0, f"flow get-run failed: {combined}"


@pytest.mark.cli
@pytest.mark.flow
class TestFlowUpdateActual:
    """Test actual flow update execution."""

    @pytest.mark.xfail(reason="BUG-004: /api/flows/update returns 401 or 'resource does not exist' for valid token")
    def test_flow_update_enabled(self, require_auth):
        """TC-CLI-FLOW-021: 'fastn flow update testFlow --enabled' enables flow."""
        result = subprocess.run(
            ["fastn", "flow", "update", "testFlow", "--enabled"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        assert result.returncode == 0, f"flow update --enabled failed: {combined}"

    @pytest.mark.xfail(reason="BUG-004: /api/flows/update returns 401 or 'resource does not exist' for valid token")
    def test_flow_update_disabled(self, require_auth):
        """TC-CLI-FLOW-023: 'fastn flow update testFlow --disabled' disables flow."""
        result = subprocess.run(
            ["fastn", "flow", "update", "testFlow", "--disabled"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        assert result.returncode == 0, f"flow update --disabled failed: {combined}"


@pytest.mark.cli
@pytest.mark.flow
class TestFlowDeleteActual:
    """Test actual flow delete execution."""

    @pytest.mark.xfail(reason="BUG-004: /api/flows/delete returns 401 or 'resource does not exist' for valid token")
    def test_flow_delete_nonexistent(self, require_auth):
        """TC-CLI-FLOW-022: 'fastn flow delete nonexistent -y' fails gracefully."""
        result = subprocess.run(
            ["fastn", "flow", "delete", "nonexistent_flow_xyz", "-y"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        # Should return "not found" but BUG-004 makes it return 401/resource error
        assert result.returncode == 0 and "not found" in combined.lower()

    @pytest.mark.xfail(reason="BUG-004: /api/flows/delete returns 'resource does not exist' for valid token")
    def test_flow_delete_testflow(self, require_auth):
        """TC-CLI-FLOW-024: 'fastn flow delete testFlow -y' deletes existing flow."""
        result = subprocess.run(
            ["fastn", "flow", "delete", "testFlow", "-y"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        combined = result.stdout + result.stderr
        assert result.returncode == 0, f"flow delete testFlow failed: {combined}"
