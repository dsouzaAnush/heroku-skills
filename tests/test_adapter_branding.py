from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_codex_source_plugin_uses_official_heroku_assets() -> None:
    manifest_path = ROOT / "adapters" / "codex" / "heroku" / ".codex-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text())
    interface = manifest["interface"]

    assert interface["composerIcon"] == "./assets/heroku-mark-dark-rgb.svg"
    assert interface["logo"] == "./assets/heroku-logo-dark-rgb.svg"
    assert interface["brandColor"] == "#D7BFF2"

    assert (ROOT / "adapters" / "codex" / "heroku" / "assets" / "heroku-mark-dark-rgb.svg").exists()
    assert (ROOT / "adapters" / "codex" / "heroku" / "assets" / "heroku-logo-dark-rgb.svg").exists()
