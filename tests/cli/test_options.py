"""
Tests for: --help, -v, --verbose options on every fastn command and subcommand.

Covers:
  - fastn --help / --version
  - fastn <cmd> --help  (all top-level commands)
  - fastn connector <sub> --help  (all connector subcommands)
  - fastn flow <sub> --help  (all flow subcommands)
  - fastn kit <sub> --help  (all kit subcommands)
  - fastn -v / --verbose on every command that makes API calls
  - fastn connector ls -v  (subcommand-level verbose: shows tool schemas)
  - fastn connector ls --installed  (subcommand-level flag)
  - fastn connector ls --active  (subcommand-level flag)
"""
import os
import subprocess
import pytest


def run(args, timeout=30, env_utf8=True):
    """Run a fastn CLI command and return CompletedProcess."""
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"} if env_utf8 else None
    return subprocess.run(
        ["fastn"] + args,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


def combined(result):
    """Return stdout + stderr merged."""
    return result.stdout + result.stderr


# ---------------------------------------------------------------------------
# TC-OPT-001..002  Top-level --help and --version
# ---------------------------------------------------------------------------

@pytest.mark.cli
class TestTopLevelOptions:

    def test_help_flag(self):
        """TC-OPT-001: 'fastn --help' exits 0 and lists every top-level command."""
        r = run(["--help"])
        assert r.returncode == 0, r.stderr
        out = r.stdout.lower()
        for cmd in ["login", "logout", "whoami", "connector", "flow", "kit", "skill", "agent", "version"]:
            assert cmd in out, f"'{cmd}' missing from --help output"

    def test_version_flag(self):
        """TC-OPT-002: 'fastn --version' exits 0 and shows version string."""
        r = run(["--version"])
        assert r.returncode == 0, r.stderr
        assert "version" in combined(r).lower()

    def test_verbose_flag_short_requires_command(self):
        """TC-OPT-003: 'fastn -v' alone (no subcommand) exits non-zero with usage hint."""
        r = run(["-v"])
        assert r.returncode != 0
        assert "missing command" in combined(r).lower()

    def test_verbose_flag_long_requires_command(self):
        """TC-OPT-004: 'fastn --verbose' alone (no subcommand) exits non-zero with usage hint."""
        r = run(["--verbose"])
        assert r.returncode != 0
        assert "missing command" in combined(r).lower()


# ---------------------------------------------------------------------------
# TC-OPT-010..019  --help on every top-level command
# ---------------------------------------------------------------------------

@pytest.mark.cli
class TestCommandHelp:

    def test_login_help(self):
        """TC-OPT-010: 'fastn login --help' exits 0 and shows usage."""
        r = run(["login", "--help"])
        assert r.returncode == 0, r.stderr
        assert "usage" in r.stdout.lower()

    def test_logout_help(self):
        """TC-OPT-011: 'fastn logout --help' exits 0 and shows usage."""
        r = run(["logout", "--help"])
        assert r.returncode == 0, r.stderr
        assert "usage" in r.stdout.lower()

    def test_whoami_help(self):
        """TC-OPT-012: 'fastn whoami --help' exits 0 and shows usage."""
        r = run(["whoami", "--help"])
        assert r.returncode == 0, r.stderr
        assert "usage" in r.stdout.lower()

    def test_version_help(self):
        """TC-OPT-013: 'fastn version --help' exits 0 and shows usage."""
        r = run(["version", "--help"])
        assert r.returncode == 0, r.stderr
        assert "usage" in r.stdout.lower()

    def test_skill_help(self):
        """TC-OPT-014: 'fastn skill --help' exits 0 and shows usage."""
        r = run(["skill", "--help"])
        assert r.returncode == 0, r.stderr
        assert "usage" in r.stdout.lower()

    def test_agent_help(self):
        """TC-OPT-015: 'fastn agent --help' exits 0, shows options and usage examples."""
        r = run(["agent", "--help"])
        assert r.returncode == 0, r.stderr
        out = r.stdout.lower()
        assert "usage" in out
        for opt in ["--connector", "--max-turns", "-y", "--eval", "--model"]:
            assert opt in r.stdout, f"Expected option '{opt}' in agent --help"

    def test_connector_help(self):
        """TC-OPT-016: 'fastn connector --help' exits 0 and lists subcommands."""
        r = run(["connector", "--help"])
        assert r.returncode == 0, r.stderr
        out = r.stdout.lower()
        for sub in ["ls", "add", "remove", "sync", "run", "schema"]:
            assert sub in out, f"'{sub}' missing from connector --help"

    def test_flow_help(self):
        """TC-OPT-017: 'fastn flow --help' exits 0 and lists subcommands."""
        r = run(["flow", "--help"])
        assert r.returncode == 0, r.stderr
        out = r.stdout.lower()
        for sub in ["ls", "generate", "run", "deploy", "schema", "get-run", "update", "delete"]:
            assert sub in out, f"'{sub}' missing from flow --help"

    def test_kit_help(self):
        """TC-OPT-018: 'fastn kit --help' exits 0 and lists subcommands."""
        r = run(["kit", "--help"])
        assert r.returncode == 0, r.stderr
        out = r.stdout.lower()
        for sub in ["ls", "get", "config"]:
            assert sub in out, f"'{sub}' missing from kit --help"


# ---------------------------------------------------------------------------
# TC-OPT-020..025  --help on every connector subcommand
# ---------------------------------------------------------------------------

@pytest.mark.cli
class TestConnectorSubcommandHelp:

    def test_connector_ls_help(self):
        """TC-OPT-020: 'fastn connector ls --help' shows --active, --installed, -v flags."""
        r = run(["connector", "ls", "--help"])
        assert r.returncode == 0, r.stderr
        out = r.stdout
        assert "--active" in out
        assert "--installed" in out
        assert "-v" in out or "--verbose" in out

    def test_connector_add_help(self):
        """TC-OPT-021: 'fastn connector add --help' exits 0."""
        r = run(["connector", "add", "--help"])
        assert r.returncode == 0, r.stderr
        assert "usage" in r.stdout.lower()

    def test_connector_remove_help(self):
        """TC-OPT-022: 'fastn connector remove --help' exits 0."""
        r = run(["connector", "remove", "--help"])
        assert r.returncode == 0, r.stderr
        assert "usage" in r.stdout.lower()

    def test_connector_sync_help(self):
        """TC-OPT-023: 'fastn connector sync --help' shows --force flag."""
        r = run(["connector", "sync", "--help"])
        assert r.returncode == 0, r.stderr
        assert "--force" in r.stdout

    def test_connector_run_help(self):
        """TC-OPT-024: 'fastn connector run --help' shows --connection-id and --tenant."""
        r = run(["connector", "run", "--help"])
        assert r.returncode == 0, r.stderr
        assert "--connection-id" in r.stdout
        assert "--tenant" in r.stdout

    def test_connector_schema_help(self):
        """TC-OPT-025: 'fastn connector schema --help' exits 0."""
        r = run(["connector", "schema", "--help"])
        assert r.returncode == 0, r.stderr
        assert "usage" in r.stdout.lower()


# ---------------------------------------------------------------------------
# TC-OPT-030..037  --help on every flow subcommand
# ---------------------------------------------------------------------------

@pytest.mark.cli
class TestFlowSubcommandHelp:

    def test_flow_ls_help(self):
        """TC-OPT-030: 'fastn flow ls --help' shows --status filter option."""
        r = run(["flow", "ls", "--help"])
        assert r.returncode == 0, r.stderr
        assert "--status" in r.stdout

    def test_flow_generate_help(self):
        """TC-OPT-031: 'fastn flow generate --help' shows -p/--prompt option."""
        r = run(["flow", "generate", "--help"])
        assert r.returncode == 0, r.stderr
        assert "--prompt" in r.stdout or "-p" in r.stdout

    def test_flow_run_help(self):
        """TC-OPT-032: 'fastn flow run --help' shows --stage and --input options."""
        r = run(["flow", "run", "--help"])
        assert r.returncode == 0, r.stderr
        assert "--stage" in r.stdout
        assert "--input" in r.stdout or "-d" in r.stdout

    def test_flow_deploy_help(self):
        """TC-OPT-033: 'fastn flow deploy --help' shows --stage and --comment options."""
        r = run(["flow", "deploy", "--help"])
        assert r.returncode == 0, r.stderr
        assert "--stage" in r.stdout
        assert "--comment" in r.stdout or "-m" in r.stdout

    def test_flow_schema_help(self):
        """TC-OPT-034: 'fastn flow schema --help' exits 0."""
        r = run(["flow", "schema", "--help"])
        assert r.returncode == 0, r.stderr
        assert "usage" in r.stdout.lower()

    def test_flow_get_run_help(self):
        """TC-OPT-035: 'fastn flow get-run --help' exits 0."""
        r = run(["flow", "get-run", "--help"])
        assert r.returncode == 0, r.stderr
        assert "usage" in r.stdout.lower()

    def test_flow_update_help(self):
        """TC-OPT-036: 'fastn flow update --help' shows --schedule, --enabled/--disabled."""
        r = run(["flow", "update", "--help"])
        assert r.returncode == 0, r.stderr
        assert "--schedule" in r.stdout
        assert "--enabled" in r.stdout
        assert "--disabled" in r.stdout

    def test_flow_delete_help(self):
        """TC-OPT-037: 'fastn flow delete --help' shows -y/--yes option."""
        r = run(["flow", "delete", "--help"])
        assert r.returncode == 0, r.stderr
        assert "-y" in r.stdout or "--yes" in r.stdout


# ---------------------------------------------------------------------------
# TC-OPT-040..042  --help on every kit subcommand
# ---------------------------------------------------------------------------

@pytest.mark.cli
class TestKitSubcommandHelp:

    def test_kit_ls_help(self):
        """TC-OPT-040: 'fastn kit ls --help' shows -q/--query option."""
        r = run(["kit", "ls", "--help"])
        assert r.returncode == 0, r.stderr
        assert "--query" in r.stdout or "-q" in r.stdout

    def test_kit_get_help(self):
        """TC-OPT-041: 'fastn kit get --help' exits 0."""
        r = run(["kit", "get", "--help"])
        assert r.returncode == 0, r.stderr
        assert "usage" in r.stdout.lower()

    def test_kit_config_help(self):
        """TC-OPT-042: 'fastn kit config --help' shows -d/--data option."""
        r = run(["kit", "config", "--help"])
        assert r.returncode == 0, r.stderr
        assert "--data" in r.stdout or "-d" in r.stdout


# ---------------------------------------------------------------------------
# TC-OPT-050..059  Global -v / --verbose on every command that hits the API
# ---------------------------------------------------------------------------

@pytest.mark.cli
class TestVerboseGlobalFlag:
    """
    The global -v / --verbose flag prints [API] markers showing
    the HTTP method, URL, headers, payload, and curl equivalent.
    Commands that read from local registry (connector ls, version)
    do NOT show [API] markers.
    Commands that call the live API (whoami, connector ls --active,
    flow ls, kit ls, kit config, skill) DO show [API] markers.
    """

    def test_short_v_whoami(self):
        """TC-OPT-050: 'fastn -v whoami' exits 0, shows [API] trace and [curl] snippet."""
        r = run(["-v", "whoami"])
        assert r.returncode == 0, r.stderr
        out = combined(r)
        assert "automation@fastn.ai" in out
        assert "[API]" in out, "Expected [API] trace in verbose whoami output"
        assert "[curl]" in out, "Expected [curl] snippet in verbose whoami output"

    def test_long_verbose_whoami(self):
        """TC-OPT-051: 'fastn --verbose whoami' shows [API] trace and [curl] snippet."""
        r = run(["--verbose", "whoami"])
        assert r.returncode == 0, r.stderr
        out = combined(r)
        assert "automation@fastn.ai" in out
        assert "[API]" in out, "Expected [API] trace in verbose whoami output"
        assert "[curl]" in out, "Expected [curl] snippet in verbose whoami output"

    def test_short_v_version(self):
        """TC-OPT-052: 'fastn -v version' exits 0 (no API call, no [API] markers)."""
        r = run(["-v", "version"])
        assert r.returncode == 0, r.stderr
        assert "fastn sdk" in combined(r).lower()
        # version reads local data — no API call expected
        assert "[API]" not in combined(r)

    def test_long_verbose_version(self):
        """TC-OPT-053: 'fastn --verbose version' exits 0."""
        r = run(["--verbose", "version"])
        assert r.returncode == 0, r.stderr
        assert "fastn sdk" in combined(r).lower()

    def test_short_v_connector_ls(self):
        """TC-OPT-054: 'fastn -v connector ls' lists connectors (local registry, no [API])."""
        r = run(["-v", "connector", "ls"])
        assert r.returncode == 0, r.stderr
        assert "connectors" in combined(r).lower()

    def test_long_verbose_connector_ls(self):
        """TC-OPT-055: 'fastn --verbose connector ls' lists connectors."""
        r = run(["--verbose", "connector", "ls"])
        assert r.returncode == 0, r.stderr
        assert "connectors" in combined(r).lower()

    def test_short_v_connector_ls_active_shows_api(self):
        """TC-OPT-056: 'fastn -v connector ls --active' shows [API] trace and [curl] snippet."""
        r = run(["-v", "connector", "ls", "--active"])
        assert r.returncode == 0, r.stderr
        out = combined(r)
        assert "401" not in out, "Got 401 unauthorized — token may be invalid"
        assert "expired" not in out.lower(), "Token expired in verbose connector ls --active"
        assert "[API]" in out, "Expected [API] trace in verbose output"
        assert "https://live.fastn.ai" in out
        assert "[curl]" in out, "Expected [curl] snippet in verbose connector ls --active"

    def test_long_verbose_connector_ls_active_shows_api(self):
        """TC-OPT-057: 'fastn --verbose connector ls --active' shows [API] and curl snippet."""
        r = run(["--verbose", "connector", "ls", "--active"])
        assert r.returncode == 0, r.stderr
        out = combined(r)
        assert "401" not in out, "Got 401 unauthorized — token may be invalid"
        assert "expired" not in out.lower(), "Token expired"
        assert "[API]" in out
        assert "[curl]" in out

    def test_short_v_flow_ls_shows_api(self):
        """TC-OPT-058: 'fastn -v flow ls' shows [API] GraphQL call and [curl] snippet.
        NOTE: exit code may be non-zero due to BUG-003 (UnicodeEncodeError on table
        render with box-drawing chars on Windows cp1252). The [API] call itself succeeds.
        """
        r = run(["-v", "flow", "ls"])
        out = combined(r)
        assert "401" not in out, "Got 401 unauthorized — token may be invalid"
        assert "unauthorized" not in out.lower(), "Unauthorized error in flow ls"
        assert "expired" not in out.lower(), "Token expired in flow ls"
        assert "[API]" in out, "Expected [API] trace in verbose output for flow ls"
        assert "/api/graphql" in out
        assert "[curl]" in out, "Expected [curl] snippet in verbose flow ls"

    def test_long_verbose_flow_ls_shows_api(self):
        """TC-OPT-059: 'fastn --verbose flow ls' shows GraphQL query payload and [curl] snippet."""
        r = run(["--verbose", "flow", "ls"])
        out = combined(r)
        assert "401" not in out, "Got 401 unauthorized — token may be invalid"
        assert "expired" not in out.lower(), "Token expired"
        assert "[API]" in out
        assert "graphql" in out.lower()
        assert "[curl]" in out, "Expected [curl] snippet in verbose flow ls"

    def test_short_v_kit_ls_shows_api(self):
        """TC-OPT-060: 'fastn -v kit ls' shows [API] GraphQL call and [curl] snippet."""
        r = run(["-v", "kit", "ls"])
        out = combined(r)
        assert "401" not in out, "Got 401 unauthorized — token may be invalid"
        assert "expired" not in out.lower(), "Token expired"
        assert "[API]" in out
        assert "[curl]" in out, "Expected [curl] snippet in verbose kit ls"
        assert "widgetConnectors" in out or "graphql" in out.lower()

    def test_long_verbose_kit_ls_shows_api(self):
        """TC-OPT-061: 'fastn --verbose kit ls' shows [API] and curl."""
        r = run(["--verbose", "kit", "ls"])
        out = combined(r)
        assert "401" not in out, "Got 401 unauthorized — token may be invalid"
        assert "expired" not in out.lower(), "Token expired"
        assert "[API]" in out
        assert "[curl]" in out

    def test_short_v_kit_config_shows_api(self):
        """TC-OPT-062: 'fastn -v kit config' shows [API] call and [curl] snippet."""
        r = run(["-v", "kit", "config"])
        assert r.returncode == 0, r.stderr
        out = combined(r)
        assert "401" not in out, "Got 401 unauthorized — token may be invalid"
        assert "expired" not in out.lower(), "Token expired"
        assert "[API]" in out
        assert "[curl]" in out, "Expected [curl] snippet in verbose kit config"
        assert "widgetMetadata" in out

    def test_long_verbose_kit_config_shows_api(self):
        """TC-OPT-063: 'fastn --verbose kit config' shows full curl command."""
        r = run(["--verbose", "kit", "config"])
        assert r.returncode == 0, r.stderr
        out = combined(r)
        assert "401" not in out, "Got 401 unauthorized — token may be invalid"
        assert "expired" not in out.lower(), "Token expired"
        assert "[API]" in out
        assert "[curl]" in out

    def test_short_v_skill_shows_api(self):
        """TC-OPT-064: 'fastn -v skill' shows [API] GraphQL call and [curl] snippet."""
        r = run(["-v", "skill"])
        assert r.returncode == 0, r.stderr
        out = combined(r)
        assert "401" not in out, "Got 401 unauthorized — token may be invalid"
        assert "expired" not in out.lower(), "Token expired"
        assert "[API]" in out
        assert "[curl]" in out, "Expected [curl] snippet in verbose skill"
        assert "listUCLAgents" in out or "graphql" in out.lower()

    def test_long_verbose_skill_shows_api(self):
        """TC-OPT-065: 'fastn --verbose skill' shows [API] and [curl]."""
        r = run(["--verbose", "skill"])
        assert r.returncode == 0, r.stderr
        out = combined(r)
        assert "401" not in out, "Got 401 unauthorized — token may be invalid"
        assert "expired" not in out.lower(), "Token expired"
        assert "[API]" in out
        assert "[curl]" in out

    def test_short_v_flow_run_shows_api(self):
        """TC-OPT-066: 'fastn -v flow run testFlow' shows [API] call and [curl] snippet."""
        r = run(["-v", "flow", "run", "testFlow"], timeout=60)
        out = combined(r)
        assert "401" not in out, "Got 401 unauthorized — token may be invalid"
        assert "expired" not in out.lower(), "Token expired"
        assert "[API]" in out, "Expected [API] trace in verbose flow run testFlow"
        assert "[curl]" in out, "Expected [curl] snippet in verbose flow run testFlow"

    def test_long_verbose_flow_run_shows_api(self):
        """TC-OPT-067: 'fastn --verbose flow run testFlow' shows [API] and [curl] snippet."""
        r = run(["--verbose", "flow", "run", "testFlow"], timeout=60)
        out = combined(r)
        assert "401" not in out, "Got 401 unauthorized — token may be invalid"
        assert "expired" not in out.lower(), "Token expired"
        assert "[API]" in out, "Expected [API] trace in verbose flow run testFlow"
        assert "[curl]" in out, "Expected [curl] snippet in verbose flow run testFlow"

    def test_short_v_kit_get_shows_api(self):
        """TC-OPT-068: 'fastn -v kit get Gmail' shows [API] call and [curl] snippet."""
        r = run(["-v", "kit", "get", "Gmail"], timeout=30)
        assert r.returncode == 0, r.stderr
        out = combined(r)
        assert "401" not in out, "Got 401 unauthorized — token may be invalid"
        assert "expired" not in out.lower(), "Token expired"
        assert "[API]" in out, "Expected [API] trace in verbose kit get Gmail"
        assert "[curl]" in out, "Expected [curl] snippet in verbose kit get Gmail"

    def test_long_verbose_kit_get_shows_api(self):
        """TC-OPT-069: 'fastn --verbose kit get Gmail' shows [API] and [curl] snippet."""
        r = run(["--verbose", "kit", "get", "Gmail"], timeout=30)
        assert r.returncode == 0, r.stderr
        out = combined(r)
        assert "401" not in out, "Got 401 unauthorized — token may be invalid"
        assert "expired" not in out.lower(), "Token expired"
        assert "[API]" in out, "Expected [API] trace in verbose kit get Gmail"
        assert "[curl]" in out, "Expected [curl] snippet in verbose kit get Gmail"

    def test_short_v_connector_schema_local(self):
        """TC-OPT-074: 'fastn -v connector schema github' exits 0 — local registry, no [API] call."""
        r = run(["-v", "connector", "schema", "github"], timeout=30)
        assert r.returncode == 0, r.stderr
        out = combined(r)
        assert "input" in out.lower() or "output" in out.lower(), \
            "Expected schema fields in connector schema output"

    def test_long_verbose_connector_schema_local(self):
        """TC-OPT-075: 'fastn --verbose connector schema github' exits 0 — local registry, no [API] call."""
        r = run(["--verbose", "connector", "schema", "github"], timeout=30)
        assert r.returncode == 0, r.stderr
        out = combined(r)
        assert "input" in out.lower() or "output" in out.lower(), \
            "Expected schema fields in connector schema output"

    def test_short_v_flow_schema_shows_api(self):
        """TC-OPT-076: 'fastn -v flow schema testFlow' shows [API] trace and [curl] snippet."""
        r = run(["-v", "flow", "schema", "testFlow"], timeout=30)
        assert r.returncode == 0, r.stderr
        out = combined(r)
        assert "401" not in out, "Got 401 unauthorized — token may be invalid"
        assert "expired" not in out.lower(), "Token expired"
        assert "[API]" in out, "Expected [API] trace in verbose flow schema testFlow"
        assert "[curl]" in out, "Expected [curl] snippet in verbose flow schema testFlow"

    def test_long_verbose_flow_schema_shows_api(self):
        """TC-OPT-077: 'fastn --verbose flow schema testFlow' shows [API] and [curl] snippet."""
        r = run(["--verbose", "flow", "schema", "testFlow"], timeout=30)
        assert r.returncode == 0, r.stderr
        out = combined(r)
        assert "401" not in out, "Got 401 unauthorized — token may be invalid"
        assert "expired" not in out.lower(), "Token expired"
        assert "[API]" in out, "Expected [API] trace in verbose flow schema testFlow"
        assert "[curl]" in out, "Expected [curl] snippet in verbose flow schema testFlow"

    def test_short_v_flow_deploy_shows_api(self):
        """TC-OPT-078: 'fastn -v flow deploy testFlow -s LIVE' shows [API] trace and [curl] snippet."""
        r = run(["-v", "flow", "deploy", "testFlow", "-s", "LIVE"], timeout=60)
        assert r.returncode == 0, r.stderr
        out = combined(r)
        assert "401" not in out, "Got 401 unauthorized — token may be invalid"
        assert "expired" not in out.lower(), "Token expired"
        assert "[API]" in out, "Expected [API] trace in verbose flow deploy"
        assert "[curl]" in out, "Expected [curl] snippet in verbose flow deploy"

    def test_long_verbose_flow_deploy_shows_api(self):
        """TC-OPT-079: 'fastn --verbose flow deploy testFlow -s LIVE' shows [API] and [curl] snippet."""
        r = run(["--verbose", "flow", "deploy", "testFlow", "-s", "LIVE"], timeout=60)
        assert r.returncode == 0, r.stderr
        out = combined(r)
        assert "401" not in out, "Got 401 unauthorized — token may be invalid"
        assert "expired" not in out.lower(), "Token expired"
        assert "[API]" in out, "Expected [API] trace in verbose flow deploy"
        assert "[curl]" in out, "Expected [curl] snippet in verbose flow deploy"


# ---------------------------------------------------------------------------
# TC-OPT-070..073  Subcommand-level verbose / flags (connector ls)
# ---------------------------------------------------------------------------

@pytest.mark.cli
class TestConnectorLsSubcommandFlags:

    def test_connector_ls_active_flag(self):
        """TC-OPT-070: 'fastn connector ls --active' exits 0, lists active connectors."""
        r = run(["connector", "ls", "--active"])
        assert r.returncode == 0, r.stderr
        out = combined(r).lower()
        assert "active connectors" in out or "connectors" in out

    @pytest.mark.xfail(reason="BUG-003: UnicodeEncodeError on box-drawing chars (─) crashes table render on Windows cp1252")
    def test_connector_ls_installed_flag(self):
        """TC-OPT-071: 'fastn connector ls --installed' exits 0 and lists installed connectors."""
        r = run(["connector", "ls", "--installed"])
        out = combined(r)
        # Auth errors must never appear regardless of BUG-003
        assert "401" not in out, "Got 401 unauthorized — token may be invalid"
        assert "expired" not in out.lower(), "Token expired"
        # Exposes BUG-003: table render crashes with UnicodeEncodeError on ─ char
        assert r.returncode == 0, f"connector ls --installed failed (exit {r.returncode}): {out[:200]}"
        assert "installed" in out.lower() or "connectors" in out.lower()

    def test_connector_ls_verbose_short_shows_schemas(self):
        """TC-OPT-072: 'fastn connector ls github -v' shows input/output schemas per tool."""
        r = run(["connector", "ls", "github", "-v"])
        assert r.returncode == 0, r.stderr
        out = combined(r)
        assert "Input:" in out or "input" in out.lower()
        assert "Output:" in out or "output" in out.lower()

    def test_connector_ls_verbose_long_shows_schemas(self):
        """TC-OPT-073: 'fastn connector ls github --verbose' same as -v."""
        r = run(["connector", "ls", "github", "--verbose"])
        assert r.returncode == 0, r.stderr
        out = combined(r)
        assert "input" in out.lower()
        assert "output" in out.lower()
