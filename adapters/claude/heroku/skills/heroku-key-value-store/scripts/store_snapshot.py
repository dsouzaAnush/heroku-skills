#!/usr/bin/env python3
"""Read-only Heroku Key-Value Store snapshot helper."""

from __future__ import annotations

import argparse
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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", help="Heroku app name", default=None)
    parser.add_argument("--database", help="Optional Key-Value Store add-on name", default=None)
    args = parser.parse_args()

    heroku_path = shutil.which("heroku")
    payload = {
        "heroku_cli_installed": bool(heroku_path),
        "auth_check": run(["heroku", "auth:whoami"]) if heroku_path else None,
        "app": args.app,
        "database": args.database,
        "inspections": [],
        "notes": [
            "This helper is read-only.",
            "Pass --app to collect Key-Value Store output when authentication is available.",
        ],
    }

    if heroku_path and args.app:
        base = ["-a", args.app]
        database = [args.database] if args.database else []
        payload["inspections"].extend(
            [
                run(["heroku", "redis:info", *database, *base, "--json"]),
                run(["heroku", "redis:credentials", *database, *base]),
                run(["heroku", "redis:wait", *database, *base, "--wait-interval", "1"]),
            ]
        )

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
