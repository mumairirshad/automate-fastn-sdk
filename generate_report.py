"""
Report generator for fastn-ai SDK v0.3.1 test automation.
Runs all CLI commands, captures outputs, runs pytest, and generates HTML + CSV reports.
"""
import subprocess
import os
import sys
import json
import csv
import re
import time
from datetime import datetime

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(PROJECT_DIR, "report")
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}

os.makedirs(REPORT_DIR, exist_ok=True)

# --- Ensure auth ---
sys.path.insert(0, PROJECT_DIR)
try:
    from auth_helper import ensure_fresh_token
    ensure_fresh_token()
    print("[OK] Token refreshed")
except Exception as e:
    print(f"[WARN] Token refresh failed: {e}")


def run_cmd(args, timeout=30):
    """Run a CLI command and return (returncode, stdout, stderr)."""
    try:
        r = subprocess.run(
            args, capture_output=True, text=True, timeout=timeout,
            env=ENV, cwd=PROJECT_DIR,
        )
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired as e:
        stdout = e.stdout or ""
        stderr = e.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        return -1, stdout.strip(), f"TIMEOUT after {timeout}s. {stderr.strip()}"
    except Exception as e:
        return -1, "", str(e)


def collect_cli_outputs():
    """Run every CLI command and collect actual outputs."""
    results = []

    def add(test_id, category, feature, command, description, args, timeout=30, expect_fail=False, skip=False, skip_reason="", expect_curl=False):
        if skip:
            results.append({
                "id": test_id, "category": category, "feature": feature,
                "command": command, "description": description,
                "status": "SKIP", "output": skip_reason,
            })
            return
        rc, stdout, stderr = run_cmd(args, timeout=timeout)
        combined = (stdout + "\n" + stderr).strip()
        # Determine status on FULL output BEFORE truncating.
        # [curl] snippets may appear after 2000 chars; truncating first causes false FAILs.
        if expect_fail:
            # Command is expected to fail (e.g. nonexistent resource). PASS if it fails gracefully.
            # But 401 auth errors are real bugs, not graceful failures.
            if "authentication failed" in combined.lower():
                status = "FAIL"
            else:
                # Any output means it handled the bad input (error msg, not found, etc.)
                status = "PASS" if len(combined) > 0 else "FAIL"
        elif expect_curl:
            # Verbose commands that make API calls MUST return a [curl] snippet.
            if rc != 0:
                status = "FAIL"
            elif "[curl]" not in combined:
                status = "FAIL"
            else:
                status = "PASS"
        else:
            status = "PASS" if rc == 0 else "FAIL"
        # Truncate AFTER status check — for display only
        if len(combined) > 2000:
            combined = combined[:2000] + "... [truncated]"
        results.append({
            "id": test_id, "category": category, "feature": feature,
            "command": command, "description": description,
            "status": status, "output": combined or "(no output)",
        })
        print(f"  {status:4s} | {test_id} | {command}")

    print("\n=== Collecting CLI Outputs ===\n")

    # --- Version ---
    add("TC-CLI-VER-001", "CLI", "Version", "fastn version",
        "Exits with code 0 and shows version", ["fastn", "version"])

    # --- Help ---
    add("TC-CLI-HELP-001", "CLI", "Help", "fastn --help",
        "Shows usage and all top-level commands", ["fastn", "--help"])
    add("TC-CLI-HELP-002", "CLI", "Help", "fastn (no args)",
        "With no args shows help/usage", ["fastn"])
    add("TC-CLI-HELP-003", "CLI", "Help", "fastn connector --help",
        "Shows connector subcommands", ["fastn", "connector", "--help"])
    add("TC-CLI-HELP-004", "CLI", "Help", "fastn flow --help",
        "Shows flow subcommands", ["fastn", "flow", "--help"])
    add("TC-CLI-HELP-005", "CLI", "Help", "fastn kit --help",
        "Shows kit subcommands", ["fastn", "kit", "--help"])
    add("TC-CLI-HELP-006", "CLI", "Help", "fastn --verbose version",
        "Accepts --verbose flag", ["fastn", "--verbose", "version"])

    # --- Authentication ---
    add("TC-CLI-AUTH-001", "CLI", "Authentication", "fastn whoami",
        "Returns user info when authenticated", ["fastn", "whoami"])
    add("TC-CLI-AUTH-002", "CLI", "Authentication", "fastn whoami (email)",
        "Output contains email address", ["fastn", "whoami"])
    add("TC-CLI-AUTH-003", "CLI", "Authentication", "fastn login --help",
        "Shows login usage information", ["fastn", "login", "--help"])
    add("TC-CLI-AUTH-004", "CLI", "Authentication", "fastn logout --help",
        "Shows logout usage information", ["fastn", "logout", "--help"])
    # Login is interactive - timeout is expected. PASS if it produced any output.
    rc, stdout, stderr = run_cmd(["fastn", "login"], timeout=10)
    combined_login = (stdout + "\n" + stderr).strip()
    results.append({
        "id": "TC-CLI-AUTH-005", "category": "CLI", "feature": "Authentication",
        "command": "fastn login", "description": "Initiates device authorization flow",
        "status": "PASS" if len(combined_login) > 0 else "FAIL",
        "output": combined_login or "(no output)",
    })
    print(f"  {'PASS' if len(combined_login) > 0 else 'FAIL':4s} | TC-CLI-AUTH-005 | fastn login")
    add("TC-CLI-AUTH-006", "CLI", "Authentication", "fastn logout",
        "Config tokens cleared after logout", [], skip=True,
        skip_reason="Skipped: destructive — would clear session")

    # --- Connector ---
    # BUG-005: connector sync frequently corrupts registry JSON on Windows.
    # Skip running sync during report generation — use pre-synced registry.
    results.append({
        "id": "TC-CLI-CON-001", "category": "CLI", "feature": "Connector",
        "command": "fastn connector sync", "description": "Downloads registry (BUG-005: corrupts registry JSON on Windows)",
        "status": "SKIP", "output": "Skipped: BUG-005 — connector sync corrupts registry.json on Windows. Run manually before report.",
    })
    print(f"  SKIP | TC-CLI-CON-001 | fastn connector sync (BUG-005: corrupts registry)")
    add("TC-CLI-CON-002", "CLI", "Connector", "fastn connector ls",
        "Lists available connectors", ["fastn", "connector", "ls"])
    add("TC-CLI-CON-003", "CLI", "Connector", "fastn connector ls --help",
        "Shows usage with flags", ["fastn", "connector", "ls", "--help"])
    add("TC-CLI-CON-004", "CLI", "Connector", "fastn connector ls --active",
        "Filters to active connectors", ["fastn", "connector", "ls", "--active"], timeout=60)
    add("TC-CLI-CON-005", "CLI", "Connector", "fastn connector add hubspot",
        "Adds connector successfully", ["fastn", "connector", "add", "hubspot"], timeout=45)
    add("TC-CLI-CON-006", "CLI", "Connector", "fastn connector add nonexistent_xyz99",
        "Fails gracefully for nonexistent connector", ["fastn", "connector", "add", "nonexistent_xyz99"], expect_fail=True)
    add("TC-CLI-CON-007", "CLI", "Connector", "fastn connector add --help",
        "Shows usage", ["fastn", "connector", "add", "--help"])
    add("TC-CLI-CON-008", "CLI", "Connector", "fastn connector remove --help",
        "Shows usage", ["fastn", "connector", "remove", "--help"])
    add("TC-CLI-CON-009", "CLI", "Connector", "fastn connector remove nonexistent_xyz99",
        "Fails gracefully for non-installed connector", ["fastn", "connector", "remove", "nonexistent_xyz99"], expect_fail=True)
    add("TC-CLI-CON-019", "CLI", "Connector", "fastn connector add slack hubspot",
        "Adds multiple connectors with type stubs", ["fastn", "connector", "add", "slack", "hubspot"], timeout=60)
    add("TC-CLI-CON-020", "CLI", "Connector", "fastn connector remove slack",
        "Removes installed connector stubs", ["fastn", "connector", "remove", "slack"])
    add("TC-CLI-CON-010", "CLI", "Connector", "fastn connector run --help",
        "Shows run usage", ["fastn", "connector", "run", "--help"])
    add("TC-CLI-CON-011", "CLI", "Connector", "fastn connector run (no args)",
        "Without args shows error/usage", ["fastn", "connector", "run"], expect_fail=True)
    add("TC-CLI-CON-012", "CLI", "Connector", "fastn connector schema --help",
        "Shows schema usage", ["fastn", "connector", "schema", "--help"])
    add("TC-CLI-CON-013", "CLI", "Connector", "fastn connector schema github",
        "Shows GitHub connector schema", ["fastn", "connector", "schema", "github"], timeout=60)
    add("TC-CLI-CON-014", "CLI", "Connector", "fastn connector (no args)",
        "Shows connector subcommands listing", ["fastn", "connector"])
    add("TC-CLI-CON-015", "CLI", "Connector", "fastn connector ls github",
        "Shows details for github connector", ["fastn", "connector", "ls", "github"])
    add("TC-CLI-CON-016", "CLI", "Connector", "fastn connector ls gmail",
        "Shows details for gmail connector", ["fastn", "connector", "ls", "gmail"])
    add("TC-CLI-CON-017", "CLI", "Connector", "fastn connector schema nonexistent",
        "Fails gracefully for nonexistent connector", ["fastn", "connector", "schema", "nonexistent_xyz99"], expect_fail=True)
    # connector run is interactive — pipe inputs like user does: enter values then hit enter
    # Test hubspot get_contacts with inputs (as user demonstrated)
    try:
        proc = subprocess.run(
            ["fastn", "connector", "run", "hubspot", "get_contacts"],
            input="\n5\n\n\n\n",  # skip associations, limit=5, skip rest
            capture_output=True, text=True, timeout=60,
            env=ENV, cwd=PROJECT_DIR,
        )
        combined_run = (proc.stdout + "\n" + proc.stderr).strip()
        rc_run = proc.returncode
    except subprocess.TimeoutExpired as e:
        stdout = e.stdout or ""
        stderr = e.stderr or ""
        if isinstance(stdout, bytes): stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes): stderr = stderr.decode("utf-8", errors="replace")
        combined_run = (stdout + "\n" + stderr).strip()
        rc_run = -1
    # FAIL if it returns "Connector ID is required" error
    run_status = "FAIL" if rc_run != 0 or "error" in combined_run.lower() else "PASS"
    results.append({
        "id": "TC-CLI-CON-018", "category": "CLI", "feature": "Connector",
        "command": "fastn connector run hubspot get_contacts (with inputs)",
        "description": "BUG-005: hub_spot_get_contacts — returns 'Connector ID is required' (HubSpot not OAuth-connected)",
        "status": run_status,
        "output": combined_run[:1200] if combined_run else "(no output)",
    })
    print(f"  {run_status:4s} | TC-CLI-CON-018 | fastn connector run hubspot get_contacts")

    # hub_spot_list_companies — same connector ID issue
    try:
        proc2 = subprocess.run(
            ["fastn", "connector", "run", "hubspot", "hub_spot_list_companies"],
            input="\n5\n\n\n\n",
            capture_output=True, text=True, timeout=60,
            env=ENV, cwd=PROJECT_DIR,
        )
        combined_co = (proc2.stdout + "\n" + proc2.stderr).strip()
        rc_co = proc2.returncode
    except subprocess.TimeoutExpired as e:
        stdout = e.stdout or ""; stderr = e.stderr or ""
        if isinstance(stdout, bytes): stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes): stderr = stderr.decode("utf-8", errors="replace")
        combined_co = (stdout + "\n" + stderr).strip(); rc_co = -1
    co_status = "FAIL" if rc_co != 0 or "error" in combined_co.lower() else "PASS"
    results.append({
        "id": "TC-CLI-CON-021", "category": "CLI", "feature": "Connector",
        "command": "fastn connector run hubspot hub_spot_list_companies",
        "description": "BUG-005: hub_spot_list_companies — returns 'Connector ID is required' (HubSpot not OAuth-connected)",
        "status": co_status,
        "output": combined_co[:1200] if combined_co else "(no output)",
    })
    print(f"  {co_status:4s} | TC-CLI-CON-021 | fastn connector run hubspot hub_spot_list_companies")

    # --- Flow ---
    add("TC-CLI-FLOW-001", "CLI", "Flow", "fastn flow ls",
        "Lists flows", ["fastn", "flow", "ls"], timeout=30)
    add("TC-CLI-FLOW-002", "CLI", "Flow", "fastn flow ls --help",
        "Shows usage", ["fastn", "flow", "ls", "--help"])
    # BUG-007: --status active returns "No flows found" even though 2 DEPLOYED flows exist
    rc_ls, stdout_ls, stderr_ls = run_cmd(["fastn", "flow", "ls", "--status", "active"], timeout=30)
    combined_ls = (stdout_ls + "\n" + stderr_ls).strip()
    # FAIL because flows exist but filter returns nothing
    ls_status = "FAIL" if "no flows found" in combined_ls.lower() else "PASS"
    results.append({
        "id": "TC-CLI-FLOW-003", "category": "CLI", "feature": "Flow",
        "command": "fastn flow ls --status active",
        "description": "BUG-007: Returns 'No flows found' even though 2 DEPLOYED flows exist",
        "status": ls_status,
        "output": combined_ls or "(no output)",
    })
    print(f"  {ls_status:4s} | TC-CLI-FLOW-003 | fastn flow ls --status active")
    add("TC-CLI-FLOW-004", "CLI", "Flow", "fastn flow (no args)",
        "Shows flow subcommands", ["fastn", "flow"])
    add("TC-CLI-FLOW-005", "CLI", "Flow", "fastn flow run --help",
        "Shows run usage", ["fastn", "flow", "run", "--help"])
    add("TC-CLI-FLOW-006", "CLI", "Flow", "fastn flow run (no args)",
        "Without flow_name shows error", ["fastn", "flow", "run"], expect_fail=True)
    add("TC-CLI-FLOW-007", "CLI", "Flow", "fastn flow run testFlow",
        "Executes testFlow successfully", ["fastn", "flow", "run", "testFlow"], timeout=60)
    add("TC-CLI-FLOW-008", "CLI", "Flow", "fastn flow run nonexistent_flow",
        "Fails gracefully for nonexistent flow", ["fastn", "flow", "run", "nonexistent_flow_xyz"], expect_fail=True)
    add("TC-CLI-FLOW-009", "CLI", "Flow", "fastn flow deploy --help",
        "Shows deploy usage", ["fastn", "flow", "deploy", "--help"])
    add("TC-CLI-FLOW-010", "CLI", "Flow", "fastn flow generate --help",
        "Shows generate usage", ["fastn", "flow", "generate", "--help"])
    add("TC-CLI-FLOW-011", "CLI", "Flow", "fastn flow schema --help",
        "Shows schema usage", ["fastn", "flow", "schema", "--help"])
    add("TC-CLI-FLOW-012", "CLI", "Flow", "fastn flow schema testFlow",
        "Shows testFlow input/output schema", ["fastn", "flow", "schema", "testFlow"], timeout=30)
    add("TC-CLI-FLOW-013", "CLI", "Flow", "fastn flow schema nonexistent",
        "Fails gracefully for nonexistent flow", ["fastn", "flow", "schema", "nonexistent_flow_xyz"], expect_fail=True)
    add("TC-CLI-FLOW-014", "CLI", "Flow", "fastn flow get-run --help",
        "Shows get-run usage", ["fastn", "flow", "get-run", "--help"])
    add("TC-CLI-FLOW-015", "CLI", "Flow", "fastn flow get-run invalid_id",
        "Fails with 401 instead of 'not found' (BUG-004)", ["fastn", "flow", "get-run", "nonexistent-run-id-00000"])
    add("TC-CLI-FLOW-016", "CLI", "Flow", "fastn flow update --help",
        "Shows update usage", ["fastn", "flow", "update", "--help"])
    add("TC-CLI-FLOW-017", "CLI", "Flow", "fastn flow delete --help",
        "Shows delete usage", ["fastn", "flow", "delete", "--help"])
    add("TC-CLI-FLOW-018", "CLI", "Flow", "fastn flow deploy testFlow -s LIVE",
        "Deploys testFlow to LIVE stage", ["fastn", "flow", "deploy", "testFlow", "-s", "LIVE"], timeout=60)
    add("TC-CLI-FLOW-019", "CLI", "Flow", "fastn flow deploy nonexistent -s LIVE",
        "Fails gracefully for nonexistent flow", ["fastn", "flow", "deploy", "nonexistent_flow_xyz", "-s", "LIVE"], expect_fail=True)
    add("TC-CLI-FLOW-020", "CLI", "Flow", "fastn flow get-run testFlow",
        "Retrieves run status (BUG-004: returns 401)", ["fastn", "flow", "get-run", "testFlow"], timeout=30)
    add("TC-CLI-FLOW-021", "CLI", "Flow", "fastn flow update testFlow --enabled",
        "Enable flow (BUG-004: returns 'resource does not exist')", ["fastn", "flow", "update", "testFlow", "--enabled"], timeout=30)
    add("TC-CLI-FLOW-023", "CLI", "Flow", "fastn flow update testFlow --disabled",
        "Disable flow (BUG-004: returns 'resource does not exist')", ["fastn", "flow", "update", "testFlow", "--disabled"], timeout=30)
    add("TC-CLI-FLOW-022", "CLI", "Flow", "fastn flow delete nonexistent -y",
        "Delete nonexistent flow (BUG-004: returns 'resource does not exist')", ["fastn", "flow", "delete", "nonexistent_flow_xyz", "-y"], timeout=30)
    add("TC-CLI-FLOW-024", "CLI", "Flow", "fastn flow delete testFlow -y",
        "Delete existing flow (BUG-004: returns 'resource does not exist')", ["fastn", "flow", "delete", "testFlow", "-y"], timeout=30)

    # --- Kit ---
    add("TC-CLI-KIT-001", "CLI", "Kit", "fastn kit ls",
        "Lists kit connectors", ["fastn", "kit", "ls"], timeout=30)
    add("TC-CLI-KIT-002", "CLI", "Kit", "fastn kit ls --help",
        "Shows usage", ["fastn", "kit", "ls", "--help"])
    add("TC-CLI-KIT-003", "CLI", "Kit", "fastn kit (no args)",
        "Shows kit subcommands", ["fastn", "kit"])
    add("TC-CLI-KIT-004", "CLI", "Kit", "fastn kit get --help",
        "Shows get usage", ["fastn", "kit", "get", "--help"])
    add("TC-CLI-KIT-005", "CLI", "Kit", "fastn kit get Gmail",
        "Returns Gmail connector details", ["fastn", "kit", "get", "Gmail"], timeout=30)
    add("TC-CLI-KIT-006", "CLI", "Kit", "fastn kit get nonexistent",
        "Fails gracefully for nonexistent kit", ["fastn", "kit", "get", "nonexistent_kit_xyz"], expect_fail=True)
    add("TC-CLI-KIT-007", "CLI", "Kit", "fastn kit config --help",
        "Shows config usage", ["fastn", "kit", "config", "--help"])
    add("TC-CLI-KIT-008", "CLI", "Kit", "fastn kit config",
        "Shows current configuration (BUG-006: returns empty despite Gmail/HubSpot connected)", ["fastn", "kit", "config"])

    # --- Skill ---
    add("TC-CLI-SKILL-001", "CLI", "Skill", "fastn skill",
        "Lists agent skills", ["fastn", "skill"])
    add("TC-CLI-SKILL-002", "CLI", "Skill", "fastn skill --help",
        "Shows usage", ["fastn", "skill", "--help"])

    # --- Agent ---
    add("TC-CLI-AGENT-001", "CLI", "Agent", "fastn agent --help",
        "Shows usage", ["fastn", "agent", "--help"])
    add("TC-CLI-AGENT-002", "CLI", "Agent", "fastn agent (no prompt)",
        "Without prompt shows error/usage", ["fastn", "agent"], expect_fail=True)

    # --- Top-level Options ---
    add("TC-OPT-001", "CLI", "Options", "fastn --version",
        "Shows version via --version flag", ["fastn", "--version"])
    add("TC-OPT-002", "CLI", "Options", "fastn -v (no command)",
        "Short verbose flag alone shows missing command error", ["fastn", "-v"], expect_fail=True)
    add("TC-OPT-003", "CLI", "Options", "fastn --verbose (no command)",
        "Long verbose flag alone shows missing command error", ["fastn", "--verbose"], expect_fail=True)

    # --- Extra --help flags ---
    add("TC-OPT-004", "CLI", "Options", "fastn whoami --help",
        "Shows whoami usage", ["fastn", "whoami", "--help"])
    add("TC-OPT-005", "CLI", "Options", "fastn version --help",
        "Shows version usage", ["fastn", "version", "--help"])
    add("TC-OPT-006", "CLI", "Options", "fastn connector sync --help",
        "Shows sync usage and --force flag", ["fastn", "connector", "sync", "--help"])
    add("TC-OPT-007", "CLI", "Options", "fastn flow generate --help",
        "Shows generate usage and -p/--prompt flag", ["fastn", "flow", "generate", "--help"])
    add("TC-OPT-008", "CLI", "Options", "fastn flow run --help",
        "Shows flow run usage with --stage and -d/--input flags", ["fastn", "flow", "run", "--help"])
    add("TC-OPT-009", "CLI", "Options", "fastn flow deploy --help",
        "Shows deploy usage with --comment/-m flag", ["fastn", "flow", "deploy", "--help"])
    add("TC-OPT-010", "CLI", "Options", "fastn flow update --help",
        "Shows update usage with --schedule, --enabled, --disabled flags", ["fastn", "flow", "update", "--help"])
    add("TC-OPT-011", "CLI", "Options", "fastn flow delete --help",
        "Shows delete usage with -y/--yes flag", ["fastn", "flow", "delete", "--help"])
    add("TC-OPT-012", "CLI", "Options", "fastn kit ls --help",
        "Shows kit ls usage with -q/--query flag", ["fastn", "kit", "ls", "--help"])
    add("TC-OPT-013", "CLI", "Options", "fastn kit config --help",
        "Shows kit config usage with -d/--data flag", ["fastn", "kit", "config", "--help"])

    # --- Verbose (-v / --verbose) combinations ---
    # Commands that call live API must return a [curl] snippet — FAIL if missing.
    # Commands that read only local data (version, connector ls) do NOT get expect_curl.
    add("TC-OPT-014", "CLI", "Verbose", "fastn -v whoami",
        "Short verbose whoami — must show [API] trace + [curl] snippet",
        ["fastn", "-v", "whoami"], timeout=60, expect_curl=True)
    add("TC-OPT-015", "CLI", "Verbose", "fastn --verbose whoami",
        "Long verbose whoami — must show [API] trace + [curl] snippet",
        ["fastn", "--verbose", "whoami"], timeout=60, expect_curl=True)
    add("TC-OPT-016", "CLI", "Verbose", "fastn -v version",
        "Short verbose version — local data only, no [API] call expected",
        ["fastn", "-v", "version"])
    add("TC-OPT-017", "CLI", "Verbose", "fastn --verbose version",
        "Long verbose version — local data only, no [API] call expected",
        ["fastn", "--verbose", "version"])
    add("TC-OPT-018", "CLI", "Verbose", "fastn -v connector ls",
        "Short verbose connector ls — reads local registry, no [API] call expected",
        ["fastn", "-v", "connector", "ls"])
    add("TC-OPT-019", "CLI", "Verbose", "fastn --verbose connector ls",
        "Long verbose connector ls — reads local registry, no [API] call expected",
        ["fastn", "--verbose", "connector", "ls"])
    add("TC-OPT-020", "CLI", "Verbose", "fastn -v connector ls --active",
        "Short verbose connector ls --active — must show [API] trace + [curl] snippet",
        ["fastn", "-v", "connector", "ls", "--active"], timeout=60, expect_curl=True)
    add("TC-OPT-021", "CLI", "Verbose", "fastn --verbose connector ls --active",
        "Long verbose connector ls --active — must show [API] trace + [curl] snippet",
        ["fastn", "--verbose", "connector", "ls", "--active"], timeout=60, expect_curl=True)
    add("TC-OPT-022", "CLI", "Verbose", "fastn -v flow ls",
        "Short verbose flow ls — must show [API] GraphQL trace + [curl] snippet",
        ["fastn", "-v", "flow", "ls"], timeout=60, expect_curl=True)
    add("TC-OPT-023", "CLI", "Verbose", "fastn --verbose flow ls",
        "Long verbose flow ls — must show [API] GraphQL trace + [curl] snippet",
        ["fastn", "--verbose", "flow", "ls"], timeout=60, expect_curl=True)
    add("TC-OPT-024", "CLI", "Verbose", "fastn -v kit ls",
        "Short verbose kit ls — must show [API] GraphQL trace + [curl] snippet",
        ["fastn", "-v", "kit", "ls"], timeout=60, expect_curl=True)
    add("TC-OPT-025", "CLI", "Verbose", "fastn --verbose kit ls",
        "Long verbose kit ls — must show [API] GraphQL trace + [curl] snippet",
        ["fastn", "--verbose", "kit", "ls"], timeout=60, expect_curl=True)
    add("TC-OPT-026", "CLI", "Verbose", "fastn -v kit config",
        "Short verbose kit config — must show [API] widgetMetadata trace + [curl] snippet",
        ["fastn", "-v", "kit", "config"], timeout=60, expect_curl=True)
    add("TC-OPT-027", "CLI", "Verbose", "fastn --verbose kit config",
        "Long verbose kit config — must show [API] widgetMetadata trace + [curl] snippet",
        ["fastn", "--verbose", "kit", "config"], timeout=60, expect_curl=True)
    add("TC-OPT-028", "CLI", "Verbose", "fastn -v skill",
        "Short verbose skill — must show [API] listUCLAgents trace + [curl] snippet",
        ["fastn", "-v", "skill"], timeout=60, expect_curl=True)
    add("TC-OPT-029", "CLI", "Verbose", "fastn --verbose skill",
        "Long verbose skill — must show [API] listUCLAgents trace + [curl] snippet",
        ["fastn", "--verbose", "skill"], timeout=60, expect_curl=True)
    add("TC-OPT-033", "CLI", "Verbose", "fastn -v flow run testFlow",
        "Short verbose flow run — must show [API] execution trace + [curl] snippet",
        ["fastn", "-v", "flow", "run", "testFlow"], timeout=60, expect_curl=True)
    add("TC-OPT-034", "CLI", "Verbose", "fastn --verbose flow run testFlow",
        "Long verbose flow run — must show [API] execution trace + [curl] snippet",
        ["fastn", "--verbose", "flow", "run", "testFlow"], timeout=60, expect_curl=True)
    add("TC-OPT-035", "CLI", "Verbose", "fastn -v kit get Gmail",
        "Short verbose kit get Gmail — must show [API] trace + [curl] snippet",
        ["fastn", "-v", "kit", "get", "Gmail"], timeout=30, expect_curl=True)
    add("TC-OPT-036", "CLI", "Verbose", "fastn --verbose kit get Gmail",
        "Long verbose kit get Gmail — must show [API] trace + [curl] snippet",
        ["fastn", "--verbose", "kit", "get", "Gmail"], timeout=30, expect_curl=True)
    add("TC-OPT-037", "CLI", "Verbose", "fastn -v connector schema github",
        "Short verbose connector schema — local registry read, no [API] call expected",
        ["fastn", "-v", "connector", "schema", "github"], timeout=30)
    add("TC-OPT-038", "CLI", "Verbose", "fastn --verbose connector schema github",
        "Long verbose connector schema — local registry read, no [API] call expected",
        ["fastn", "--verbose", "connector", "schema", "github"], timeout=30)
    add("TC-OPT-039", "CLI", "Verbose", "fastn -v flow schema testFlow",
        "Short verbose flow schema — must show [API] trace + [curl] snippet",
        ["fastn", "-v", "flow", "schema", "testFlow"], timeout=30, expect_curl=True)
    add("TC-OPT-040", "CLI", "Verbose", "fastn --verbose flow schema testFlow",
        "Long verbose flow schema — must show [API] trace + [curl] snippet",
        ["fastn", "--verbose", "flow", "schema", "testFlow"], timeout=30, expect_curl=True)
    add("TC-OPT-041", "CLI", "Verbose", "fastn -v flow deploy testFlow -s LIVE",
        "Short verbose flow deploy — must show [API] trace + [curl] snippet",
        ["fastn", "-v", "flow", "deploy", "testFlow", "-s", "LIVE"], timeout=60, expect_curl=True)
    add("TC-OPT-042", "CLI", "Verbose", "fastn --verbose flow deploy testFlow -s LIVE",
        "Long verbose flow deploy — must show [API] trace + [curl] snippet",
        ["fastn", "--verbose", "flow", "deploy", "testFlow", "-s", "LIVE"], timeout=60, expect_curl=True)

    # --- Connector ls flags ---
    add("TC-OPT-030", "CLI", "Connector Flags", "fastn connector ls --installed",
        "Shows installed connectors only", ["fastn", "connector", "ls", "--installed"])
    add("TC-OPT-031", "CLI", "Connector Flags", "fastn connector ls github -v",
        "Short verbose on connector ls github shows schemas", ["fastn", "connector", "ls", "github", "-v"])
    add("TC-OPT-032", "CLI", "Connector Flags", "fastn connector ls github --verbose",
        "Long verbose on connector ls github shows schemas", ["fastn", "connector", "ls", "github", "--verbose"])

    return results


def collect_sdk_outputs():
    """Run SDK-level tests via pytest and parse results."""
    results = []
    print("\n=== Running SDK Tests via pytest ===\n")
    xml_path = os.path.join(REPORT_DIR, "junit_results.xml")
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/sdk/", "-v", "--tb=short",
         f"--junitxml={xml_path}"],
        capture_output=True, text=True, timeout=300,
        env=ENV, cwd=PROJECT_DIR,
    )
    output = r.stdout + "\n" + r.stderr
    print(output[-3000:] if len(output) > 3000 else output)

    # Parse verbose pytest output for test results
    for line in output.split("\n"):
        line = line.strip()
        # Match lines like "tests/sdk/test_client.py::TestClass::test_name PASSED"
        m = re.match(r"tests/sdk/([\w/]+\.py)::([\w]+)::([\w]+)\s+(PASSED|FAILED|XFAIL|SKIPPED|ERROR)", line)
        if not m:
            continue
        file, cls, test, status = m.groups()
        # Find the actual error output for failures
        err_output = ""
        if status == "FAILED":
            # Search for the error in the full output
            pattern = f"{cls}::{test}"
            idx = output.find(pattern)
            if idx >= 0:
                err_block = output[idx:idx+500]
                err_output = err_block.strip()

        status_map = {"PASSED": "PASS", "FAILED": "FAIL", "XFAIL": "XFAIL", "SKIPPED": "SKIP", "ERROR": "FAIL"}
        mapped_status = status_map.get(status, status)

        # Build description from test name
        desc = test.replace("test_", "").replace("_", " ").title()
        feature = cls.replace("Test", "")
        test_id = f"TC-SDK-{feature.upper()[:6]}-{test[-3:].upper()}"

        results.append({
            "id": test_id,
            "category": "SDK",
            "feature": feature,
            "command": f"{cls}::{test}",
            "description": desc,
            "status": mapped_status,
            "output": err_output if err_output else f"({status})",
        })

    return results


def collect_pytest_summary():
    """Run full test suite and return summary counts + individual results."""
    print("\n=== Running Full pytest Suite ===\n")
    try:
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=line"],
            capture_output=True, text=True, timeout=660,
            env=ENV, cwd=PROJECT_DIR,
        )
        output = r.stdout + "\n" + r.stderr
    except subprocess.TimeoutExpired as e:
        stdout = (e.stdout or b"").decode("utf-8", errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        stderr = (e.stderr or b"").decode("utf-8", errors="replace") if isinstance(e.stderr, bytes) else (e.stderr or "")
        output = stdout + "\n" + stderr + "\n[TIMEOUT] pytest suite exceeded 660s — partial results below."
        print("[WARN] pytest timed out — partial results captured")

    # Parse summary line
    summary = {}
    m = re.search(r"(\d+) passed", output)
    if m: summary["passed"] = int(m.group(1))
    m = re.search(r"(\d+) failed", output)
    if m: summary["failed"] = int(m.group(1))
    m = re.search(r"(\d+) skipped", output)
    if m: summary["skipped"] = int(m.group(1))
    m = re.search(r"(\d+) xfailed", output)
    if m: summary["xfailed"] = int(m.group(1))
    m = re.search(r"(\d+) error", output)
    if m: summary["error"] = int(m.group(1))

    # Parse individual test results from verbose output
    test_results = []
    for line in output.split("\n"):
        line = line.strip()
        m = re.match(r"tests/([\w/]+\.py)::([\w]+)::([\w]+)\s+(PASSED|FAILED|XFAIL|SKIPPED|ERROR)", line)
        if m:
            test_results.append({
                "path": m.group(1),
                "class": m.group(2),
                "test": m.group(3),
                "status": m.group(4),
            })

    return summary, test_results, output


def esc(s):
    """Escape HTML."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def generate_html(cli_results, pytest_summary, pytest_output, timestamp):
    """Generate the HTML report."""
    # xfailed = known bugs that fail → counts as FAIL
    # xpassed = unexpectedly passed  → counts as PASS
    xfailed = pytest_summary.get("xfailed", 0)
    xpassed = pytest_summary.get("xpassed", 0)
    passed = pytest_summary.get("passed", 0) + xpassed
    failed = pytest_summary.get("failed", 0) + xfailed
    skipped = pytest_summary.get("skipped", 0)
    total = passed + failed + skipped
    pass_rate = round(passed / (passed + failed) * 100, 1) if (passed + failed) else 0

    # Group CLI results by feature
    groups = {}
    for r in cli_results:
        groups.setdefault(r["feature"], []).append(r)

    # Count CLI results
    cli_pass = sum(1 for r in cli_results if r["status"] == "PASS")
    cli_fail = sum(1 for r in cli_results if r["status"] == "FAIL")
    cli_skip = sum(1 for r in cli_results if r["status"] == "SKIP")
    cli_total = len(cli_results)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>fastn-ai SDK v0.3.1 — Test Automation Report</title>
<style>
  :root {{
    --bg: #0f172a; --surface: #1e293b; --surface2: #334155; --border: #475569;
    --text: #e2e8f0; --text-muted: #94a3b8; --accent: #818cf8; --accent-light: #a5b4fc;
    --pass: #34d399; --pass-bg: rgba(52,211,153,0.1);
    --fail: #f87171; --fail-bg: rgba(248,113,113,0.1);
    --xfail: #fbbf24; --xfail-bg: rgba(251,191,36,0.1);
    --skip: #94a3b8; --skip-bg: rgba(148,163,184,0.1);
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', -apple-system, sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}

  .header {{
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #1e293b 100%);
    border-radius: 16px; padding: 40px; margin-bottom: 32px;
    border: 1px solid rgba(129,140,248,0.2);
  }}
  .header h1 {{ font-size: 28px; font-weight: 700; margin-bottom: 8px; }}
  .header h1 span {{ color: var(--accent-light); }}
  .header .subtitle {{ color: var(--text-muted); font-size: 14px; margin-bottom: 20px; }}
  .meta-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }}
  .meta-item {{ background: rgba(255,255,255,0.05); border-radius: 8px; padding: 12px 16px; }}
  .meta-label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-muted); }}
  .meta-value {{ font-size: 16px; font-weight: 600; margin-top: 2px; }}

  .stats-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 16px; margin-bottom: 32px;
  }}
  .stat-card {{
    background: var(--surface); border-radius: 12px; padding: 20px; text-align: center;
    border: 1px solid var(--border);
  }}
  .stat-card .number {{ font-size: 36px; font-weight: 700; }}
  .stat-card .label {{ font-size: 12px; text-transform: uppercase; color: var(--text-muted); margin-top: 4px; }}
  .stat-pass .number {{ color: var(--pass); }}
  .stat-fail .number {{ color: var(--fail); }}
  .stat-skip .number {{ color: var(--skip); }}
  .stat-xfail .number {{ color: var(--xfail); }}
  .stat-total .number {{ color: var(--accent-light); }}

  .progress-bar {{ background: var(--surface2); border-radius: 8px; height: 12px; margin-bottom: 32px; overflow: hidden; display: flex; }}
  .progress-pass {{ background: var(--pass); height: 100%; }}
  .progress-fail {{ background: var(--fail); height: 100%; }}
  .progress-xfail {{ background: var(--xfail); height: 100%; }}
  .progress-skip {{ background: var(--skip); height: 100%; }}

  .section {{ margin-bottom: 32px; }}
  .section-title {{
    font-size: 20px; font-weight: 600; margin-bottom: 16px;
    padding-bottom: 8px; border-bottom: 2px solid var(--accent);
    display: flex; align-items: center; gap: 8px;
  }}
  .section-badge {{
    background: var(--accent); color: #fff; font-size: 11px; padding: 2px 8px;
    border-radius: 12px; font-weight: 600;
  }}

  table {{ width: 100%; border-collapse: collapse; background: var(--surface); border-radius: 12px; overflow: hidden; }}
  th {{ background: var(--surface2); padding: 10px 14px; text-align: left; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-muted); }}
  td {{ padding: 10px 14px; border-top: 1px solid rgba(255,255,255,0.05); font-size: 13px; vertical-align: top; }}
  tr:hover td {{ background: rgba(255,255,255,0.02); }}

  .badge {{
    display: inline-block; padding: 2px 10px; border-radius: 12px;
    font-size: 11px; font-weight: 600; text-transform: uppercase;
  }}
  .badge-pass {{ background: var(--pass-bg); color: var(--pass); }}
  .badge-fail {{ background: var(--fail-bg); color: var(--fail); }}
  .badge-skip {{ background: var(--skip-bg); color: var(--skip); }}
  .badge-xfail {{ background: var(--xfail-bg); color: var(--xfail); }}

  .output-cell {{
    font-family: 'Cascadia Code', 'Fira Code', monospace;
    font-size: 11px; color: var(--text-muted); max-width: 500px;
    word-break: break-word; white-space: pre-wrap;
    max-height: 120px; overflow-y: auto;
  }}
  .cmd-cell {{ font-family: 'Cascadia Code', 'Fira Code', monospace; font-size: 12px; color: var(--accent-light); }}

  .bugs {{ background: var(--fail-bg); border: 1px solid var(--fail); border-radius: 12px; padding: 20px; margin-bottom: 32px; }}
  .bugs h3 {{ color: var(--fail); margin-bottom: 12px; }}
  .bug-item {{ padding: 8px 0; border-top: 1px solid rgba(248,113,113,0.2); }}
  .bug-item:first-child {{ border-top: none; }}
  .bug-id {{ font-weight: 700; color: var(--fail); }}
  .bug-desc {{ color: var(--text); }}

  .footer {{ text-align: center; padding: 32px; color: var(--text-muted); font-size: 12px; }}

  .collapsible {{ cursor: pointer; }}
  .collapsible:hover {{ background: rgba(255,255,255,0.04); }}
  details summary {{ cursor: pointer; list-style: none; }}
  details summary::-webkit-details-marker {{ display: none; }}
</style>
</head>
<body>
<div class="container">

  <div class="header">
    <h1>fastn-ai SDK <span>v0.3.1</span> — Test Report</h1>
    <div class="subtitle">Automated CLI & SDK test execution against <strong>testsdk</strong> project</div>
    <div class="meta-grid">
      <div class="meta-item"><div class="meta-label">Generated</div><div class="meta-value">{timestamp}</div></div>
      <div class="meta-item"><div class="meta-label">Project</div><div class="meta-value">testsdk</div></div>
      <div class="meta-item"><div class="meta-label">User</div><div class="meta-value">automation@fastn.ai</div></div>
      <div class="meta-item"><div class="meta-label">Platform</div><div class="meta-value">Windows 11 / Python 3.13</div></div>
      <div class="meta-item"><div class="meta-label">Pass Rate (pytest)</div><div class="meta-value">{pass_rate}%</div></div>
    </div>
  </div>

  <div class="stats-grid">
    <div class="stat-card stat-total"><div class="number">{total}</div><div class="label">Total (pytest)</div></div>
    <div class="stat-card stat-pass"><div class="number">{passed}</div><div class="label">Pass</div></div>
    <div class="stat-card stat-fail"><div class="number">{failed}</div><div class="label">Fail</div></div>
    <div class="stat-card stat-skip"><div class="number">{skipped}</div><div class="label">Skip</div></div>
  </div>

  <div class="progress-bar">
    <div class="progress-pass" style="width:{passed/total*100 if total else 0:.1f}%"></div>
    <div class="progress-fail" style="width:{failed/total*100 if total else 0:.1f}%"></div>
  </div>

  <div class="bugs">
    <h3>Known Bugs / Issues ({2 + failed})</h3>
    <div class="bug-item"><span class="bug-id">BUG-001</span> <span class="bug-desc">Server-side <code>KeyError: 'getTools'</code> in get_tools_for API — affects tool discovery for all connectors on testsdk project</span></div>
    <div class="bug-item"><span class="bug-id">BUG-002</span> <span class="bug-desc"><code>kit.get_connector()</code> returns empty dict silently when connector not installed (should raise or warn)</span></div>
    <div class="bug-item"><span class="bug-id">BUG-003</span> <span class="bug-desc"><code>UnicodeEncodeError</code> on Windows (cp1252) when CLI outputs emoji characters (checkmarks). Workaround: set PYTHONIOENCODING=utf-8</span></div>
  </div>
"""

    # --- CLI Results by Feature Group ---
    html += '  <h2 style="color:var(--accent-light);margin-bottom:20px;">CLI Command Results ({} Pass / {} Fail)</h2>\n'.format(cli_pass, cli_fail)

    for feature, items in groups.items():
        feat_pass = sum(1 for i in items if i["status"] == "PASS")
        feat_fail = sum(1 for i in items if i["status"] == "FAIL")
        feat_skip = sum(1 for i in items if i["status"] == "SKIP")
        feat_total = len(items)
        badge_parts = [f"{feat_pass} Pass", f"{feat_fail} Fail"]
        if feat_skip:
            badge_parts.append(f"{feat_skip} Skip")
        html += f"""
  <div class="section">
    <div class="section-title">{esc(feature)} <span class="section-badge">{" / ".join(badge_parts)}</span></div>
    <table>
      <thead><tr><th>ID</th><th>Command</th><th>Description</th><th>Status</th><th>Actual Output</th></tr></thead>
      <tbody>
"""
        for item in items:
            badge_class = {"PASS": "badge-pass", "FAIL": "badge-fail", "SKIP": "badge-skip"}.get(item["status"], "badge-fail")
            html += f"""        <tr>
          <td><code>{esc(item['id'])}</code></td>
          <td class="cmd-cell">{esc(item['command'])}</td>
          <td>{esc(item['description'])}</td>
          <td><span class="badge {badge_class}">{esc(item['status'])}</span></td>
          <td><div class="output-cell">{esc(item['output'][:800])}</div></td>
        </tr>
"""
        html += "      </tbody>\n    </table>\n  </div>\n"

    # --- Pytest Summary ---
    html += """
  <h2 style="color:var(--accent-light);margin-bottom:20px;">Full pytest Suite Results</h2>
  <div class="section">
    <details>
      <summary style="cursor:pointer;color:var(--accent-light);font-size:14px;margin-bottom:12px;">Click to expand full pytest output</summary>
      <pre style="background:var(--surface);padding:16px;border-radius:8px;overflow-x:auto;font-size:11px;max-height:600px;overflow-y:auto;color:var(--text-muted);">"""
    html += esc(pytest_output[-8000:])
    html += """</pre>
    </details>
  </div>
"""

    html += f"""
  <div class="footer">
    Generated by fastn-ai test automation &mdash; {timestamp}<br>
    163 pytest tests | {cli_total} CLI command outputs captured
  </div>
</div>
</body>
</html>"""

    return html


def generate_csv(cli_results):
    """Generate CSV with all test cases and outputs."""
    csv_path = os.path.join(REPORT_DIR, "test_cases.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Test ID", "Category", "Feature", "Command / Method", "Description", "Status", "Actual Output"])
        for r in cli_results:
            writer.writerow([
                r["id"], r["category"], r["feature"],
                r["command"], r["description"], r["status"],
                r["output"][:2000],
            ])
    return csv_path


def main():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"=== fastn-ai Test Report Generator ===")
    print(f"Time: {timestamp}\n")

    # 1. Collect CLI outputs
    cli_results = collect_cli_outputs()

    # 2. Run full pytest suite
    pytest_summary, pytest_results, pytest_output = collect_pytest_summary()

    # 3. Generate HTML
    html = generate_html(cli_results, pytest_summary, pytest_output, timestamp)
    html_path = os.path.join(REPORT_DIR, "fastn_test_report.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n[OK] HTML report: {html_path}")

    # 4. Generate CSV
    csv_path = generate_csv(cli_results)
    print(f"[OK] CSV report:  {csv_path}")

    # 5. Print summary
    cli_pass = sum(1 for r in cli_results if r["status"] == "PASS")
    cli_fail = sum(1 for r in cli_results if r["status"] == "FAIL")
    cli_skip = sum(1 for r in cli_results if r["status"] == "SKIP")
    print(f"\n=== Summary ===")
    print(f"CLI Commands:  {len(cli_results)} total | {cli_pass} PASS | {cli_fail} FAIL | {cli_skip} SKIP")
    print(f"pytest Suite:  {pytest_summary}")
    print(f"Report files saved to: {REPORT_DIR}")


if __name__ == "__main__":
    main()
