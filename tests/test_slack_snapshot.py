from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_SCRIPT = REPO_ROOT / "skills" / "heroku-slack-agents" / "scripts" / "project_snapshot.py"


def run_snapshot(cwd: Path) -> dict:
    result = subprocess.run(
        [sys.executable, str(SNAPSHOT_SCRIPT)],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_snapshot_detects_typescript_bolt_http_project(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text(
        json.dumps(
            {
                "dependencies": {
                    "@slack/bolt": "^4.0.0",
                    "typescript": "^5.0.0",
                }
            }
        )
    )
    (tmp_path / "Procfile").write_text("web: node app.js\n")
    (tmp_path / ".slack").mkdir()
    (tmp_path / ".slack" / "manifest.ts").write_text("export default {};\n")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.ts").write_text(
        "import { App } from '@slack/bolt';\n"
        "const app = new App({ signingSecret: process.env.SLACK_SIGNING_SECRET });\n"
        "app.command('/hello', async ({ ack }) => { await ack(); });\n"
        "app.start(process.env.PORT);\n"
        "// /slack/events\n"
    )

    payload = run_snapshot(tmp_path)

    assert payload["package_json"]["bolt_detected"] is True
    assert payload["package_json"]["typescript_detected"] is True
    assert ".slack/manifest.ts" in payload["repo_hints"]["manifest_files"]
    assert payload["repo_hints"]["mentions_slack_events_path"] is True
    assert payload["deployment_mode_guess"] == "http"


def test_snapshot_detects_socket_mode_project(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text(
        json.dumps({"dependencies": {"@slack/bolt": "^4.0.0"}})
    )
    (tmp_path / "Procfile").write_text("worker: node app.js\n")
    (tmp_path / "app.js").write_text(
        "import { App } from '@slack/bolt';\n"
        "const app = new App({ socketMode: true, appToken: process.env.SLACK_APP_TOKEN });\n"
    )

    payload = run_snapshot(tmp_path)

    assert payload["deployment_mode_guess"] == "socket-mode"
    assert payload["repo_hints"]["mentions_socket_mode"] is True
