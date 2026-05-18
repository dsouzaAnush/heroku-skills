#!/usr/bin/env python3
"""Inspect local Heroku AI plugin availability without mutating state."""

from __future__ import annotations

import json
import shutil
import subprocess


def run(cmd: list[str]) -> dict:
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return {
        "command": cmd,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def summarize_plugins(result: dict, expected_plugins: list[str]) -> dict:
    summary = {
        "command": result["command"],
        "returncode": result["returncode"],
        "stderr": result["stderr"],
        "detected": {plugin: False for plugin in expected_plugins},
    }
    if result["returncode"] != 0:
        summary["stdout_preview"] = result["stdout"][:500]
        return summary

    try:
        plugins = json.loads(result["stdout"] or "[]")
    except json.JSONDecodeError:
        summary["stdout_preview"] = result["stdout"][:500]
        return summary

    names = {
        str(value)
        for plugin in plugins
        for value in (
            plugin.get("name"),
            plugin.get("pluginName"),
            plugin.get("alias"),
            plugin.get("pjson", {}).get("name") if isinstance(plugin.get("pjson"), dict) else None,
        )
        if value
    }
    summary["detected"] = {
        plugin: plugin in names
        for plugin in expected_plugins
    }
    summary["installed_plugin_count"] = len(names)
    return summary


def main() -> None:
    heroku_path = shutil.which("heroku")
    plugins = (
        summarize_plugins(
            run(["heroku", "plugins", "--json"]),
            ["@heroku/plugin-ai"],
        )
        if heroku_path
        else None
    )
    ai_help = run(["heroku", "help", "ai:models:list"]) if heroku_path else None
    payload = {
        "heroku_cli_installed": bool(heroku_path),
        "heroku_path": heroku_path,
        "plugins": plugins,
        "ai_models_help": ai_help,
        "notes": [
            "This helper is read-only.",
            "Install the AI plugin with `heroku plugins:install @heroku/plugin-ai` when AI commands are unavailable.",
        ],
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
