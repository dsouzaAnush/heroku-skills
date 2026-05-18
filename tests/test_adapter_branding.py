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


def test_claude_source_plugin_uses_official_heroku_assets_and_mcp() -> None:
    manifest_path = ROOT / "adapters" / "claude" / "heroku" / ".claude-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text())

    assert manifest["skills"] == "./skills/"
    assert manifest["mcpServers"] == "./.mcp.json"
    assert "interface" not in manifest

    mcp = json.loads((ROOT / "adapters" / "claude" / "heroku" / ".mcp.json").read_text())
    server = mcp["mcpServers"]["heroku-code-mcp"]
    assert server["type"] == "http"
    assert server["url"] == "http://127.0.0.1:3333/mcp"
    assert server["headers"]["x-user-id"] == "default"

    assert (ROOT / "adapters" / "claude" / "heroku" / "assets" / "heroku-mark-dark-rgb.svg").exists()
    assert (ROOT / "adapters" / "claude" / "heroku" / "assets" / "heroku-logo-dark-rgb.svg").exists()
    assert (ROOT / "adapters" / "claude" / "heroku" / "assets" / "claude-ai-logo.svg").exists()


def test_cursor_source_bundle_uses_project_rule_and_official_heroku_assets() -> None:
    rule_path = ROOT / "adapters" / "cursor" / "heroku" / ".cursor" / "rules" / "heroku-skills.mdc"
    rule_text = rule_path.read_text()
    frontmatter = rule_text.split("---", 2)[1]

    assert "description:" in frontmatter
    assert "alwaysApply: false" in frontmatter
    assert "skills/<skill-name>/SKILL.md" in rule_text

    assert (ROOT / "adapters" / "cursor" / "heroku" / "assets" / "heroku-mark-dark-rgb.svg").exists()
    assert (ROOT / "adapters" / "cursor" / "heroku" / "assets" / "heroku-logo-dark-rgb.svg").exists()
