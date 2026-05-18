#!/usr/bin/env python3
"""Read-only Heroku deployment preflight for the current repository."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


def run(cmd: list[str]) -> dict:
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return {
        "command": cmd,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def main() -> None:
    repo_root = Path.cwd()
    interesting_files = [
        "Procfile",
        "app.json",
        "heroku.yml",
        "Dockerfile",
        "package.json",
        "requirements.txt",
        "Gemfile",
        "pom.xml",
        "composer.json",
    ]
    files_present = {name: (repo_root / name).exists() for name in interesting_files}

    git_remote = run(["git", "remote", "-v"])
    heroku_path = shutil.which("heroku")
    heroku_version = run(["heroku", "--version"]) if heroku_path else None
    auth_check = run(["heroku", "auth:whoami"]) if heroku_path else None

    deploy_method = "buildpack"
    if files_present["heroku.yml"] or files_present["Dockerfile"]:
        deploy_method = "container"
    if files_present["Procfile"]:
        deploy_method = "buildpack"

    payload = {
        "repo_root": str(repo_root),
        "files_present": files_present,
        "git_remote": git_remote,
        "heroku_cli": {
            "installed": bool(heroku_path),
            "path": heroku_path,
            "version_check": heroku_version,
            "auth_check": auth_check,
        },
        "recommended_deploy_method": deploy_method,
        "notes": [
            "This script is read-only and does not contact a specific app.",
            "Authentication may fail safely when the shell is not logged in to Heroku.",
        ],
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
