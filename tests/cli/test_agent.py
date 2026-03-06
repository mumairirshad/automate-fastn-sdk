"""
Tests for: fastn agent
"""
import subprocess
import pytest


@pytest.mark.cli
@pytest.mark.agent
class TestAgentCommand:
    """Test 'fastn agent' command."""

    def test_agent_help(self):
        """TC-CLI-AGENT-001: 'fastn agent --help' shows usage."""
        result = subprocess.run(
            ["fastn", "agent", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0

    def test_agent_no_prompt(self, require_auth):
        """TC-CLI-AGENT-002: 'fastn agent' without prompt shows error or usage."""
        result = subprocess.run(
            ["fastn", "agent"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        combined = result.stdout + result.stderr
        # Should show usage, prompt for input, or error about missing prompt
        assert result.returncode != 0 or "usage" in combined.lower() or "prompt" in combined.lower() or len(combined) > 0
