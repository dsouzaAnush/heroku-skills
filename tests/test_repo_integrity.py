from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_REFERENCES = (
    "v" + "ercel-labs",
    "github.com/" + "v" + "ercel",
    "raw.githubusercontent.com/" + "v" + "ercel",
)


def iter_text_files() -> list[Path]:
    files: list[Path] = []
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {".git", "dist", ".pytest_cache", "__pycache__"} for part in path.parts):
            continue
        if path.suffix in {".md", ".py", ".json", ".yaml", ".yml", ".txt"}:
            files.append(path)
    return files


def test_repo_contains_no_forbidden_vendor_references() -> None:
    offenders: list[str] = []
    for path in iter_text_files():
        text = path.read_text(errors="ignore").lower()
        if any(token in text for token in FORBIDDEN_REFERENCES):
            offenders.append(str(path.relative_to(REPO_ROOT)))
    assert offenders == [], f"Found forbidden external references: {offenders}"


def test_build_adapter_creates_self_contained_bundle(tmp_path: Path) -> None:
    output_dir = tmp_path / "bundle"
    subprocess.run(
        [sys.executable, "scripts/build_codex_adapter.py", "--output", str(output_dir)],
        cwd=REPO_ROOT,
        check=True,
    )
    manifest = json.loads((output_dir / ".codex-plugin" / "plugin.json").read_text())
    assert manifest["skills"] == "./skills/"
    assert (output_dir / "skills" / "heroku-slack-agents" / "SKILL.md").exists()


def test_build_claude_adapter_creates_self_contained_bundle(tmp_path: Path) -> None:
    output_dir = tmp_path / "claude-bundle"
    subprocess.run(
        [sys.executable, "scripts/build_claude_adapter.py", "--output", str(output_dir)],
        cwd=REPO_ROOT,
        check=True,
    )
    manifest = json.loads((output_dir / ".claude-plugin" / "plugin.json").read_text())
    assert manifest["skills"] == "./skills/"
    assert manifest["mcpServers"] == "./.mcp.json"
    assert (output_dir / ".mcp.json").exists()
    assert (output_dir / "skills" / "heroku-slack-agents" / "SKILL.md").exists()


def test_build_cursor_adapter_creates_self_contained_bundle(tmp_path: Path) -> None:
    output_dir = tmp_path / "cursor-bundle"
    subprocess.run(
        [sys.executable, "scripts/build_cursor_adapter.py", "--output", str(output_dir)],
        cwd=REPO_ROOT,
        check=True,
    )
    rule_path = output_dir / ".cursor" / "rules" / "heroku-skills.mdc"
    rule_text = rule_path.read_text()
    assert "description:" in rule_text.split("---", 2)[1]
    assert "alwaysApply: false" in rule_text.split("---", 2)[1]
    assert (output_dir / "skills" / "heroku-slack-agents" / "SKILL.md").exists()
