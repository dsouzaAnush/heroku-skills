from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]

SCRIPT_EXPECTATIONS = {
    "skills/deploy-to-heroku/scripts/preflight.py": {
        "keys": {"repo_root", "files_present", "git_remote", "heroku_cli", "recommended_deploy_method", "notes"},
    },
    "skills/heroku-app-ops/scripts/app_snapshot.py": {
        "keys": {"heroku_cli_installed", "auth_check", "app", "inspections", "notes"},
    },
    "skills/heroku-applink-connections/scripts/plugin_status.py": {
        "keys": {"heroku_cli_installed", "heroku_path", "plugins", "salesforce_connect_help", "notes"},
    },
    "skills/heroku-connect/scripts/plugin_status.py": {
        "keys": {"heroku_cli_installed", "heroku_path", "plugins", "connect_info_help", "notes"},
    },
    "skills/heroku-key-value-store/scripts/store_snapshot.py": {
        "keys": {"heroku_cli_installed", "auth_check", "app", "database", "inspections", "notes"},
    },
    "skills/heroku-logging-drains/scripts/logging_snapshot.py": {
        "keys": {"heroku_cli_installed", "auth_check", "app", "inspections", "notes"},
    },
    "skills/heroku-managed-inference/scripts/plugin_status.py": {
        "keys": {"heroku_cli_installed", "heroku_path", "plugins", "ai_models_help", "notes"},
    },
    "skills/heroku-postgres/scripts/postgres_snapshot.py": {
        "keys": {"heroku_cli_installed", "auth_check", "app", "inspections", "notes"},
    },
    "skills/heroku-slack-agents/scripts/project_snapshot.py": {
        "keys": {"cwd", "heroku_cli_installed", "auth_check", "package_json", "procfile", "repo_hints", "deployment_mode_guess", "recommendations", "notes"},
    },
}


@pytest.mark.parametrize("relative_path,expectation", sorted(SCRIPT_EXPECTATIONS.items()))
def test_helper_scripts_emit_json_without_arguments(relative_path: str, expectation: dict) -> None:
    script_path = REPO_ROOT / relative_path
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert expectation["keys"].issubset(payload.keys())
    assert isinstance(payload["notes"], list)
    assert any("read-only" in note.lower() for note in payload["notes"])
