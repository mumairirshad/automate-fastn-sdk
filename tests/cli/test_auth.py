"""
Tests for: fastn login, fastn logout, fastn whoami
"""
import subprocess
import json
import os
import pytest

ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}


@pytest.mark.cli
@pytest.mark.auth
class TestWhoamiCommand:
    """Test the 'fastn whoami' CLI command."""

    def test_whoami_authenticated(self, require_auth):
        """TC-CLI-AUTH-001: 'fastn whoami' returns user info when authenticated."""
        result = subprocess.run(
            ["fastn", "whoami"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"whoami failed: {result.stderr}"
        output = result.stdout.strip()
        # Should display user name or email
        assert len(output) > 0, "whoami returned empty output"

    def test_whoami_shows_email(self, require_auth):
        """TC-CLI-AUTH-002: 'fastn whoami' output contains an email address."""
        result = subprocess.run(
            ["fastn", "whoami"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"whoami failed: {result.stderr}"
        output = result.stdout.strip()
        # Must contain an email address — loose fallback removed: len > 3 always passes
        assert "@" in output, (
            f"whoami output does not contain an email address: {output}"
        )
        # Must not contain auth errors even if exit code is 0
        assert "401" not in output, "Got 401 in whoami output — token may be invalid"
        assert "expired" not in output.lower(), "Token expired message in whoami output"
        assert "not authenticated" not in output.lower(), "Auth failure in whoami output"


@pytest.mark.cli
@pytest.mark.auth
class TestWhoamiUnauthenticated:
    """Test 'fastn whoami' when not authenticated."""

    def test_whoami_fails_when_expired(self):
        """TC-CLI-AUTH-003: 'fastn whoami' returns error when session expired."""
        # This test verifies the error behavior; it only runs meaningfully
        # if the session is actually expired. We test the error message format.
        result = subprocess.run(
            ["fastn", "whoami"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            error_output = result.stderr + result.stdout
            assert "login" in error_output.lower() or "expired" in error_output.lower() or "auth" in error_output.lower(), (
                f"Error message should mention login/expired/auth. Got: {error_output}"
            )


@pytest.mark.cli
@pytest.mark.auth
class TestLoginCommand:
    """Test the 'fastn login' CLI command behavior."""

    def test_login_help(self):
        """TC-CLI-AUTH-004: 'fastn login --help' shows usage information."""
        result = subprocess.run(
            ["fastn", "login", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0, f"login --help failed: {result.stderr}"
        assert "login" in result.stdout.lower() or "auth" in result.stdout.lower(), (
            f"Help output should mention login. Got: {result.stdout}"
        )


@pytest.mark.cli
@pytest.mark.auth
class TestLogoutCommand:
    """Test the 'fastn logout' CLI command behavior."""

    def test_logout_help(self):
        """TC-CLI-AUTH-005: 'fastn logout --help' shows usage information."""
        result = subprocess.run(
            ["fastn", "logout", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0, f"logout --help failed: {result.stderr}"

    def test_logout_config_cleanup(self, require_auth):
        """TC-CLI-AUTH-006: After logout, config tokens are cleared."""
        # NOTE: This test actually logs out. It is DESTRUCTIVE.
        # Only run this if you want to test logout behavior.
        pytest.skip(
            "Skipping destructive logout test. "
            "Remove this skip to test logout (will require re-login)."
        )


@pytest.mark.cli
@pytest.mark.auth
class TestWhoamiDetails:
    """Test 'fastn whoami' detailed output."""

    def test_whoami_shows_user_id(self, require_auth):
        """TC-CLI-AUTH-007: 'fastn whoami' output contains User ID."""
        result = subprocess.run(
            ["fastn", "whoami"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        assert result.returncode == 0
        assert "user id" in result.stdout.lower(), (
            f"Expected 'User ID' in whoami output. Got: {result.stdout}"
        )

    def test_whoami_shows_logged_in_as(self, require_auth):
        """TC-CLI-AUTH-008: 'fastn whoami' output shows 'Logged in as'."""
        result = subprocess.run(
            ["fastn", "whoami"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        assert result.returncode == 0
        assert "logged in as" in result.stdout.lower(), (
            f"Expected 'Logged in as' in whoami output. Got: {result.stdout}"
        )


@pytest.mark.cli
@pytest.mark.auth
class TestLoginFlow:
    """Test 'fastn login' command behavior (non-interactive checks)."""

    def test_login_starts_device_flow(self):
        """TC-CLI-AUTH-009: 'fastn login' initiates device authorization flow."""
        # Login is interactive - it starts a device flow and waits for browser auth.
        # We run it with a short timeout and expect it to produce output before timing out.
        try:
            result = subprocess.run(
                ["fastn", "login"],
                capture_output=True,
                text=True,
                timeout=10,
                env=ENV,
            )
            combined = result.stdout + result.stderr
        except subprocess.TimeoutExpired as e:
            # Expected: login waits for user to authorize in browser
            stdout = e.stdout or ""
            stderr = e.stderr or ""
            if isinstance(stdout, bytes):
                stdout = stdout.decode("utf-8", errors="replace")
            if isinstance(stderr, bytes):
                stderr = stderr.decode("utf-8", errors="replace")
            combined = stdout + stderr
        assert len(combined.strip()) > 0, "login command produced no output before timeout"


@pytest.mark.cli
@pytest.mark.auth
class TestLogoutActual:
    """Test 'fastn logout' actual execution."""

    def test_logout_help_shows_usage(self):
        """TC-CLI-AUTH-010: 'fastn logout --help' describes logout behavior."""
        result = subprocess.run(
            ["fastn", "logout", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
            env=ENV,
        )
        assert result.returncode == 0
        assert "logout" in result.stdout.lower() or "log out" in result.stdout.lower()
