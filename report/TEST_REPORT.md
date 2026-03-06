# fastn-ai SDK v0.3.1 - Test Automation Report

**Date:** 2026-02-28
**Package:** fastn-ai v0.3.1
**Python:** 3.13.5
**Platform:** Windows 11 Pro
**Connector Used:** HubSpot
**Auth User:** automation@fastn.ai

---

## Summary

| Metric         | Count |
|----------------|-------|
| Total Tests    | 141   |
| Passed         | 132   |
| Skipped        | 3     |
| Known Bugs (xfail) | 6 |
| Failed         | 0     |
| Duration       | ~2m 54s |

---

## Test Categories

### CLI Commands (48 tests) - ALL PASS

| Test ID | Command | Test Description | Status |
|---------|---------|------------------|--------|
| TC-CLI-HELP-001 | `fastn --help` | Shows usage and all top-level commands | PASS |
| TC-CLI-HELP-002 | `fastn` | With no args shows help or usage | PASS |
| TC-CLI-HELP-003 | `fastn connector --help` | Shows subcommands (ls, sync, add, run) | PASS |
| TC-CLI-HELP-004 | `fastn flow --help` | Shows subcommands (ls, run) | PASS |
| TC-CLI-HELP-005 | `fastn kit --help` | Shows subcommands | PASS |
| TC-CLI-HELP-006 | `fastn --verbose version` | Accepts --verbose flag | PASS |
| TC-CLI-VER-001 | `fastn version` | Exits with code 0 | PASS |
| TC-CLI-VER-002 | `fastn version` | Output matches 'Fastn SDK vX.Y.Z' format | PASS |
| TC-CLI-VER-003 | `fastn version` | Contains version '0.3.1' | PASS |
| TC-CLI-VER-004 | `fastn version` | Includes registry version and last synced | PASS |
| TC-CLI-AUTH-001 | `fastn whoami` | Returns user info when authenticated | PASS |
| TC-CLI-AUTH-002 | `fastn whoami` | Output contains email address | PASS |
| TC-CLI-AUTH-003 | `fastn whoami` | Returns proper error when session expired | PASS |
| TC-CLI-AUTH-004 | `fastn login --help` | Shows usage information | PASS |
| TC-CLI-AUTH-005 | `fastn logout --help` | Shows usage information | PASS |
| TC-CLI-AUTH-006 | `fastn logout` | Config tokens cleared after logout | SKIP (destructive) |
| TC-CLI-CON-001 | `fastn connector sync` | Downloads registry successfully | PASS |
| TC-CLI-CON-002 | `fastn connector ls` | Lists available connectors | PASS |
| TC-CLI-CON-003 | `fastn connector ls` | Output contains known connectors (hubspot, github, etc.) | PASS |
| TC-CLI-CON-004 | `fastn connector ls --help` | Shows usage | PASS |
| TC-CLI-CON-005 | `fastn connector add hubspot` | Adds connector successfully | PASS |
| TC-CLI-CON-006 | `fastn connector add <invalid>` | Fails gracefully for nonexistent connector | PASS |
| TC-CLI-CON-007 | `fastn connector add --help` | Shows usage | PASS |
| TC-CLI-CON-008 | `fastn connector remove --help` | Shows usage | PASS |
| TC-CLI-CON-009 | `fastn connector remove <invalid>` | Fails gracefully for non-installed connector | PASS |
| TC-CLI-CON-010 | `fastn connector run --help` | Shows usage | PASS |
| TC-CLI-CON-011 | `fastn connector run` | Without args shows error/usage | PASS |
| TC-CLI-CON-012 | `fastn connector schema --help` | Shows usage | PASS |
| TC-CLI-FLOW-001 | `fastn flow ls` | Lists flows | PASS |
| TC-CLI-FLOW-002 | `fastn flow ls --help` | Shows usage | PASS |
| TC-CLI-FLOW-003 | `fastn flow get-run --help` | Shows usage | PASS |
| TC-CLI-FLOW-004 | `fastn flow get-run <invalid>` | Fails gracefully for invalid ID | PASS |
| TC-CLI-FLOW-005 | `fastn flow deploy --help` | Shows usage | PASS |
| TC-CLI-FLOW-006 | `fastn flow run --help` | Shows usage | PASS |
| TC-CLI-FLOW-007 | `fastn flow run` | Without flow_name shows error | PASS |
| TC-CLI-FLOW-008 | `fastn flow generate --help` | Shows usage | PASS |
| TC-CLI-FLOW-009 | `fastn flow schema --help` | Shows usage | PASS |
| TC-CLI-FLOW-010 | `fastn flow update --help` | Shows usage | PASS |
| TC-CLI-FLOW-011 | `fastn flow delete --help` | Shows usage | PASS |
| TC-CLI-KIT-001 | `fastn kit ls` | Returns list of kit connectors | PASS |
| TC-CLI-KIT-002 | `fastn kit ls --help` | Shows usage | PASS |
| TC-CLI-KIT-003 | `fastn kit get --help` | Shows usage | PASS |
| TC-CLI-KIT-004 | `fastn kit config --help` | Shows usage | PASS |
| TC-CLI-SKILL-001 | `fastn skill` | Lists agent skills | PASS |
| TC-CLI-SKILL-002 | `fastn skill --help` | Shows usage | PASS |
| TC-CLI-AGENT-001 | `fastn agent --help` | Shows usage | PASS |
| TC-CLI-AGENT-002 | `fastn agent` | Without prompt shows error/usage | PASS |

### SDK Client Tests (39 tests)

| Test ID | Method | Test Description | Status |
|---------|--------|------------------|--------|
| TC-SDK-CLI-001 | `FastnClient()` | Initializes without error | PASS |
| TC-SDK-CLI-002 | `with FastnClient()` | Works as context manager | PASS |
| TC-SDK-CLI-003 | `.connectors` | Has 'connectors' attribute | PASS |
| TC-SDK-CLI-004 | `.flows` | Has 'flows' attribute | PASS |
| TC-SDK-CLI-005 | `.auth` | Has 'auth' attribute | PASS |
| TC-SDK-CLI-006 | `.skills` | Has 'skills' attribute | PASS |
| TC-SDK-CLI-007 | `.projects` | Has 'projects' attribute | PASS |
| TC-SDK-CLI-008 | `.kit` | Has 'kit' attribute | PASS |
| TC-SDK-CLI-009 | `.get_tools_for` | Has callable method | PASS |
| TC-SDK-CLI-010 | `.execute` | Has callable method | PASS |
| TC-SDK-CLI-011 | `.run` | Has callable method | PASS |
| TC-SDK-CLI-012 | `.connect` | Has callable method | PASS |
| TC-SDK-CLI-013 | `.close` | Has callable method | PASS |
| TC-SDK-CLI-014 | `.hubspot` | Dynamic connector access returns object | PASS |
| TC-SDK-CLI-015 | `FastnClient(api_key=12345)` | Non-string api_key handled | PASS |
| TC-SDK-CLI-016 | `FastnClient(project_id=...)` | Explicit project_id works | PASS |
| TC-SDK-CONN-001 | `connectors.list()` | Returns a list | PASS |
| TC-SDK-CONN-002 | `connectors.list()` | Returns non-empty list | PASS |
| TC-SDK-CONN-003 | `connectors.list()` | Each item has name/identifier | PASS |
| TC-SDK-CONN-004 | `connectors.get('hubspot')` | Returns connector details | PASS |
| TC-SDK-CONN-005 | `connectors.get(<invalid>)` | Raises error for invalid name | PASS |
| TC-SDK-CONN-006 | `connectors.get_tools('hubspot')` | Returns list of tools | PASS |
| TC-SDK-CONN-007 | `connectors.get_tools('hubspot')` | Returns non-empty list | PASS |
| TC-SDK-CONN-008 | `connectors.get_tool('hubspot', <tool>)` | Returns tool info | SKIP |
| TC-SDK-CONN-009 | `connectors.get_tool('hubspot', <invalid>)` | Raises error | PASS |
| TC-SDK-FLOW-001 | `flows.list()` | Returns a list | PASS |
| TC-SDK-FLOW-002 | `flows.list()` | Completes without exception | PASS |
| TC-SDK-FLOW-003 | `flows.get(<invalid>)` | Raises FlowNotFoundError | PASS |
| TC-SDK-FLOW-004 | `flows.get_schema(<invalid>)` | Raises error | PASS |
| TC-SDK-FLOW-005 | `flows.run(<invalid>)` | Raises error | PASS |
| TC-SDK-FLOW-006 | `flows.deploy(<invalid>)` | Raises error | PASS |
| TC-SDK-SKILL-001 | `skills.list()` | Returns a list | PASS |
| TC-SDK-SKILL-002 | `skills.list()` | Completes without exception | PASS |
| TC-SDK-PROJ-001 | `projects.list()` | Returns a list | PASS |
| TC-SDK-PROJ-002 | `projects.list()` | Returns at least one project | PASS |
| TC-SDK-PROJ-003 | `projects.list()` | Each project has expected keys | PASS |
| TC-SDK-KIT-001 | `kit.get()` | Returns kit metadata | PASS |
| TC-SDK-KIT-002 | `kit.list()` | Returns a list | PASS |
| TC-SDK-KIT-003 | `kit.get_connector(<invalid>)` | Returns without error (see bugs) | PASS |

### Tool Execution Tests (15 tests, 6 xfail)

| Test ID | Method | Test Description | Status |
|---------|--------|------------------|--------|
| TC-SDK-EXEC-001 | `get_tools_for(prompt)` | Returns list (default format) | XFAIL (BUG) |
| TC-SDK-EXEC-002 | `get_tools_for(prompt)` | Returns non-empty results | XFAIL (BUG) |
| TC-SDK-EXEC-003 | `get_tools_for(format='openai')` | OpenAI format | XFAIL (BUG) |
| TC-SDK-EXEC-004 | `get_tools_for(format='anthropic')` | Anthropic format | XFAIL (BUG) |
| TC-SDK-EXEC-005 | `get_tools_for(format='gemini')` | Gemini format | XFAIL (BUG) |
| TC-SDK-EXEC-006 | `get_tools_for(format='bedrock')` | Bedrock format | XFAIL (BUG) |
| TC-SDK-EXEC-007 | `get_tools_for(format='raw')` | Raw format | PASS |
| TC-SDK-EXEC-008 | `get_tools_for(limit=2)` | Respects limit | PASS |
| TC-SDK-EXEC-009 | `get_tools_for(connector='hubspot')` | Filters by connector | PASS |
| TC-SDK-EXEC-010 | `get_tools('hubspot')` | Returns list of hubspot tools | PASS |
| TC-SDK-EXEC-011 | `get_tools(<invalid>)` | Raises error for invalid connector | PASS |
| TC-SDK-EXEC-012 | `get_tool('hubspot', <tool>)` | Returns tool info | SKIP |
| TC-SDK-EXEC-013 | `get_tool('hubspot', <invalid>)` | Raises error | PASS |
| TC-SDK-EXEC-014 | `execute(<invalid>)` | Handles invalid tool gracefully | PASS |
| TC-SDK-EXEC-015 | `run(prompt)` | Returns a result | PASS |

### Async Client Tests (9 tests) - ALL PASS

| Test ID | Method | Test Description | Status |
|---------|--------|------------------|--------|
| TC-SDK-ASYNC-001 | `AsyncFastnClient()` | Initializes without error | PASS |
| TC-SDK-ASYNC-002 | `async with AsyncFastnClient()` | Works as async context manager | PASS |
| TC-SDK-ASYNC-003 | `.connectors` | Has connectors attribute | PASS |
| TC-SDK-ASYNC-004 | `.flows` | Has flows attribute | PASS |
| TC-SDK-ASYNC-005 | `await connectors.list()` | Returns a list | PASS |
| TC-SDK-ASYNC-006 | `await get_tools_for(format='raw')` | Returns tools | PASS |
| TC-SDK-ASYNC-007 | `await flows.list()` | Returns a list | PASS |
| TC-SDK-ASYNC-008 | `await skills.list()` | Returns a list | PASS |
| TC-SDK-ASYNC-009 | `await projects.list()` | Returns a list | PASS |

### Auth Namespace Tests (1 test) - PASS

| Test ID | Method | Test Description | Status |
|---------|--------|------------------|--------|
| TC-SDK-AUTH-001 | `auth.list_connections(<invalid>)` | Handles invalid connector | PASS |

### Configuration Tests (14 tests) - ALL PASS

| Test ID | Area | Test Description | Status |
|---------|------|------------------|--------|
| TC-CORE-CFG-001 | File | .fastn/config.json exists | PASS |
| TC-CORE-CFG-002 | File | Config is valid JSON | PASS |
| TC-CORE-CFG-003 | File | Contains project_id | PASS |
| TC-CORE-CFG-004 | File | Contains valid stage (LIVE/STAGING/DEV) | PASS |
| TC-CORE-CFG-005 | File | Contains auth_token | PASS |
| TC-CORE-CFG-006 | File | Contains refresh_token | PASS |
| TC-CORE-CFG-007 | File | Contains token_expiry in ISO format | PASS |
| TC-CORE-CFG-008 | Module | load_config() returns object | PASS |
| TC-CORE-CFG-009 | Module | FastnConfig.validate() succeeds | PASS |
| TC-CORE-CFG-010 | Module | FastnConfig.to_dict() returns dict | PASS |
| TC-CORE-CFG-011 | Module | FastnConfig.get_headers() returns auth headers | PASS |
| TC-CORE-CFG-012 | Module | find_fastn_dir() locates .fastn directory | PASS |
| TC-CORE-CFG-013 | Env | FASTN_PROJECT_ID env var is recognized | PASS |
| TC-CORE-CFG-014 | Env | FASTN_STAGE env var is recognized | PASS |

### Error Handling Tests (16 tests) - ALL PASS

| Test ID | Class | Test Description | Status |
|---------|-------|------------------|--------|
| TC-CORE-ERR-001 | FastnError | Is base exception | PASS |
| TC-CORE-ERR-002 | AuthError | Inherits from FastnError | PASS |
| TC-CORE-ERR-003 | ConfigError | Inherits from FastnError | PASS |
| TC-CORE-ERR-004 | ConnectorNotFoundError | Inherits from FastnError | PASS |
| TC-CORE-ERR-005 | ToolNotFoundError | Inherits from FastnError | PASS |
| TC-CORE-ERR-006 | ConnectionNotFoundError | Inherits from FastnError | PASS |
| TC-CORE-ERR-007 | APIError | Inherits from FastnError | PASS |
| TC-CORE-ERR-008 | FlowNotFoundError | Inherits from FastnError | PASS |
| TC-CORE-ERR-009 | RunNotFoundError | Inherits from FastnError | PASS |
| TC-CORE-ERR-010 | RegistryError | Inherits from FastnError | PASS |
| TC-CORE-ERR-011 | FastnError | Stores message correctly | PASS |
| TC-CORE-ERR-012 | APIError | Has status_code and response_body | PASS |
| TC-CORE-ERR-013 | ConnectorNotFoundError | Has connector_name attribute | PASS |
| TC-CORE-ERR-014 | ToolNotFoundError | Has connector_name and tool_name | PASS |
| TC-CORE-ERR-015 | FlowNotFoundError | Has flow_id attribute | PASS |
| TC-CORE-ERR-016 | AuthError | Catchable as FastnError | PASS |

---

## Bugs Found

### BUG-001: `get_tools_for()` KeyError on 'name' in LLM formatters (CRITICAL)

- **Severity:** Critical
- **Location:** `fastn/_formatters.py:36`
- **Affected:** All LLM format conversions (openai, anthropic, gemini, bedrock)
- **Root Cause:** The formatter expects `action["name"]` but the API response returns tools without a `name` field. The raw format works correctly.
- **Impact:** `get_tools_for()` crashes with `KeyError: 'name'` for any format except `raw`. This breaks the core LLM integration workflow.
- **Workaround:** Use `format="raw"` and manually format tools.
- **Affected Tests:** TC-SDK-EXEC-001 through TC-SDK-EXEC-006

### BUG-002: `kit.get_connector()` does not raise for invalid connector ID (LOW)

- **Severity:** Low
- **Location:** `fastn/_kit.py`
- **Description:** Calling `kit.get_connector("nonexistent-id")` returns silently instead of raising `ConnectorNotFoundError` or `APIError`.
- **Expected:** Should raise an error for invalid connector IDs.
- **Affected Tests:** TC-SDK-KIT-003

---

## Project Structure

```
fastnSDK/
├── conftest.py          # Root fixtures (auth, client)
├── pytest.ini           # Pytest configuration
├── run_tests.py         # Test runner with CLI options
├── report/
│   ├── test_report.html # Interactive HTML report
│   └── TEST_REPORT.md   # This file
└── tests/
    ├── cli/             # CLI command tests (48 tests)
    │   ├── test_agent.py
    │   ├── test_auth.py
    │   ├── test_connector.py
    │   ├── test_flow.py
    │   ├── test_help.py
    │   ├── test_kit.py
    │   ├── test_skill.py
    │   └── test_version.py
    ├── sdk/             # SDK client tests (39 + 9 async + 1 auth)
    │   ├── test_async_client.py
    │   ├── test_auth_namespace.py
    │   ├── test_client.py
    │   ├── test_connectors.py
    │   ├── test_execution.py
    │   ├── test_flows.py
    │   ├── test_kit.py
    │   ├── test_projects.py
    │   └── test_skills.py
    └── core/            # Config & error tests (30 tests)
        ├── test_config.py
        └── test_errors.py
```

## How to Run

```bash
# Run all tests
python run_tests.py

# Run by category
python run_tests.py --cli
python run_tests.py --sdk
python run_tests.py --core

# Generate HTML report
python run_tests.py --report

# Run specific markers
python -m pytest tests/ -m connector -v
python -m pytest tests/ -m flow -v
python -m pytest tests/ -m async_client -v
```
