from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def make_fake_heroku(tmp_path: Path) -> dict[str, str]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log_path = tmp_path / "heroku-commands.log"
    script_path = bin_dir / "heroku"
    script_path.write_text(
        """#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

log_path = Path(os.environ["FAKE_HEROKU_LOG"])
argv = sys.argv[1:]
with log_path.open("a", encoding="utf-8") as handle:
    handle.write(json.dumps(argv) + "\\n")

if argv == ["auth:whoami"]:
    print("fake@example.com")
elif argv == ["--version"]:
    print("heroku/9.0.0 fake")
elif argv[:2] == ["apps:info", "-a"] and "--json" in argv:
    print(json.dumps({"name": argv[2], "stack": {"name": "heroku-24"}}))
elif argv[:1] == ["releases:info"]:
    print("v123 fake release")
elif argv[:1] == ["maintenance"]:
    print("off")
elif argv[:1] == ["logs"]:
    print("2026-01-01T00:00:00 app[web.1]: hello")
elif argv[:1] == ["drains"]:
    print("[]")
elif argv[:1] == ["pg:info"]:
    print("=== DATABASE_URL")
elif argv[:1] == ["pg:backups"]:
    print("No backups captured")
elif argv[:1] == ["pg:credentials"]:
    print("Credential information")
elif argv[:1] == ["redis:info"]:
    print(json.dumps({"plan": "premium-0", "version": "7"}))
elif argv[:1] == ["redis:credentials"]:
    print("REDIS_URL=rediss://example")
elif argv[:1] == ["redis:wait"]:
    print("available")
elif argv == ["plugins", "--json"]:
    print(json.dumps([
        {"name": "@heroku-cli/heroku-connect-plugin", "pluginName": "@heroku-cli/heroku-connect-plugin"},
        {"name": "@heroku/plugin-ai", "pluginName": "@heroku/plugin-ai"},
        {"name": "@heroku-cli/plugin-applink", "pluginName": "@heroku-cli/plugin-applink"}
    ]))
elif argv[:1] == ["help"]:
    print("help for " + " ".join(argv[1:]))
else:
    print("fake heroku command", " ".join(argv))
"""
    )
    script_path.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}{os.pathsep}{env['PATH']}"
    env["FAKE_HEROKU_LOG"] = str(log_path)
    return {"env": env, "log_path": str(log_path)}


def run_script(script_relative_path: str, cwd: Path, env: dict[str, str], *args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / script_relative_path), *args],
        cwd=cwd,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def read_command_log(log_path: str) -> list[list[str]]:
    path = Path(log_path)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def test_preflight_detects_buildpack_repo_with_procfile(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "remote", "add", "heroku", "https://git.heroku.com/example.git"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    (tmp_path / "Procfile").write_text("web: node app.js\n")
    (tmp_path / "package.json").write_text('{"name":"fixture"}\n')
    (tmp_path / "Dockerfile").write_text("FROM node:20\n")

    fake = make_fake_heroku(tmp_path)
    payload = run_script("skills/deploy-to-heroku/scripts/preflight.py", tmp_path, fake["env"])

    assert payload["recommended_deploy_method"] == "buildpack"
    assert payload["files_present"]["Procfile"] is True
    assert payload["files_present"]["Dockerfile"] is True
    assert "git.heroku.com/example.git" in payload["git_remote"]["stdout"]


def test_preflight_detects_container_repo_from_heroku_yml(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    (tmp_path / "heroku.yml").write_text("build:\n  docker:\n    web: Dockerfile\n")

    fake = make_fake_heroku(tmp_path)
    payload = run_script("skills/deploy-to-heroku/scripts/preflight.py", tmp_path, fake["env"])

    assert payload["recommended_deploy_method"] == "container"
    assert payload["files_present"]["heroku.yml"] is True


def test_app_snapshot_collects_expected_app_commands(tmp_path: Path) -> None:
    fake = make_fake_heroku(tmp_path)
    payload = run_script(
        "skills/heroku-app-ops/scripts/app_snapshot.py",
        tmp_path,
        fake["env"],
        "--app",
        "demo-app",
    )

    assert payload["app"] == "demo-app"
    assert len(payload["inspections"]) == 3
    commands = read_command_log(fake["log_path"])
    assert ["auth:whoami"] in commands
    assert ["apps:info", "-a", "demo-app", "--json"] in commands
    assert ["releases:info", "-a", "demo-app"] in commands
    assert ["maintenance", "-a", "demo-app"] in commands


def test_key_value_store_snapshot_collects_database_specific_commands(tmp_path: Path) -> None:
    fake = make_fake_heroku(tmp_path)
    payload = run_script(
        "skills/heroku-key-value-store/scripts/store_snapshot.py",
        tmp_path,
        fake["env"],
        "--app",
        "demo-app",
        "--database",
        "REDIS_URL",
    )

    assert payload["app"] == "demo-app"
    assert payload["database"] == "REDIS_URL"
    commands = read_command_log(fake["log_path"])
    assert ["redis:info", "REDIS_URL", "-a", "demo-app", "--json"] in commands
    assert ["redis:credentials", "REDIS_URL", "-a", "demo-app"] in commands
    assert ["redis:wait", "REDIS_URL", "-a", "demo-app", "--wait-interval", "1"] in commands


def test_postgres_snapshot_collects_expected_commands(tmp_path: Path) -> None:
    fake = make_fake_heroku(tmp_path)
    payload = run_script(
        "skills/heroku-postgres/scripts/postgres_snapshot.py",
        tmp_path,
        fake["env"],
        "--app",
        "demo-app",
    )

    assert payload["app"] == "demo-app"
    commands = read_command_log(fake["log_path"])
    assert ["pg:info", "-a", "demo-app"] in commands
    assert ["pg:backups", "-a", "demo-app"] in commands
    assert ["pg:credentials", "-a", "demo-app"] in commands


def test_plugin_status_helpers_summarize_plugins_without_raw_manifest(tmp_path: Path) -> None:
    fake = make_fake_heroku(tmp_path)

    cases = (
        (
            "skills/heroku-connect/scripts/plugin_status.py",
            "connect_info_help",
            "@heroku-cli/heroku-connect-plugin",
        ),
        (
            "skills/heroku-managed-inference/scripts/plugin_status.py",
            "ai_models_help",
            "@heroku/plugin-ai",
        ),
        (
            "skills/heroku-applink-connections/scripts/plugin_status.py",
            "salesforce_connect_help",
            "@heroku-cli/plugin-applink",
        ),
    )

    for script_path, help_key, expected_plugin in cases:
        payload = run_script(script_path, tmp_path, fake["env"])
        assert payload[help_key]["returncode"] == 0
        assert payload["plugins"]["detected"][expected_plugin] is True
        assert "stdout" not in payload["plugins"]


def test_logging_snapshot_collects_runtime_selection_and_drain_commands(tmp_path: Path) -> None:
    fake = make_fake_heroku(tmp_path)
    payload = run_script(
        "skills/heroku-logging-drains/scripts/logging_snapshot.py",
        tmp_path,
        fake["env"],
        "--app",
        "demo-app",
    )

    assert payload["app"] == "demo-app"
    commands = read_command_log(fake["log_path"])
    assert ["apps:info", "-a", "demo-app", "--json"] in commands
    assert ["logs", "-a", "demo-app", "--num", "50"] in commands
    assert ["drains", "-a", "demo-app", "--json"] in commands
