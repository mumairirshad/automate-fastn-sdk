"""
Tests for: fastn skill
"""
import subprocess
import os
import pytest

ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}


@pytest.mark.cli
@pytest.mark.skill
class TestSkillCommand:
    """Test 'fastn skill' command."""

    def test_skill_ls(self, require_auth):
        """TC-CLI-SKILL-001: 'fastn skill' lists agent skills."""
        result = subprocess.run(
            ["fastn", "skill"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        assert result.returncode == 0, f"skill command failed: {result.stderr}"

    def test_skill_help(self):
        """TC-CLI-SKILL-002: 'fastn skill --help' shows usage."""
        result = subprocess.run(
            ["fastn", "skill", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0

    def test_skill_lists_skills(self, require_auth):
        """TC-CLI-SKILL-003: 'fastn skill' output contains skill entries."""
        result = subprocess.run(
            ["fastn", "skill"],
            capture_output=True,
            text=True,
            timeout=30,
            env=ENV,
        )
        assert result.returncode == 0
        output = result.stdout.strip()
        assert "skill" in output.lower() or "found" in output.lower() or "name" in output.lower(), (
            f"Expected skill listing in output. Got: {output[:300]}"
        )
