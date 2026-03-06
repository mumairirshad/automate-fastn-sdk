"""
Root conftest.py - shared fixtures for fastn-ai SDK test automation.

Auto-refreshes tokens before test session using auth_helper.
"""
import json
import os
import subprocess
import sys
import pytest

# Project paths
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_CONFIG = os.path.join(PROJECT_DIR, ".fastn", "config.json")
HOME_CONFIG = os.path.join(os.path.expanduser("~"), ".fastn", "config.json")


def _load_fastn_config():
    """Load .fastn/config.json - prefer local project config."""
    for path in [LOCAL_CONFIG, HOME_CONFIG]:
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
    return {}


def _ensure_auth():
    """Ensure tokens are fresh before running tests."""
    sys.path.insert(0, PROJECT_DIR)
    try:
        from auth_helper import ensure_fresh_token
        return ensure_fresh_token()
    except Exception as e:
        print(f"Auto-refresh failed: {e}")
        return False


def _is_authenticated():
    """Check if fastn session is valid by running 'fastn whoami'."""
    try:
        result = subprocess.run(
            ["fastn", "whoami"],
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            cwd=PROJECT_DIR,
        )
        return result.returncode == 0
    except Exception:
        return False


# Auto-refresh tokens at module load time
_ensure_auth()


@pytest.fixture(scope="session")
def fastn_config():
    """Return the loaded .fastn/config.json as a dict."""
    return _load_fastn_config()


@pytest.fixture(scope="session")
def is_authenticated():
    """Return True if fastn session is active."""
    return _is_authenticated()


@pytest.fixture(scope="session")
def require_auth(is_authenticated):
    """Skip test if not authenticated."""
    if not is_authenticated:
        pytest.skip("Not authenticated. Run 'fastn login' first.")


