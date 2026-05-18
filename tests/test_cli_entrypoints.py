from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_command(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )


def test_evaluate_skills_json_report_shape() -> None:
    result = run_command("scripts/evaluate_skills.py", "--json")
    payload = json.loads(result.stdout)

    assert payload["summary"]["prompt_count"] > 0
    assert payload["summary"]["contrast_count"] > 0
    assert payload["summary"]["coverage_failure_count"] == 0
    assert isinstance(payload["routing_results"], list)
    assert isinstance(payload["contrast_results"], list)
    assert isinstance(payload["per_skill_summary"], dict)


def test_build_codex_adapter_outputs_bundle_with_manifest(tmp_path: Path) -> None:
    output_dir = tmp_path / "codex-bundle"
    result = run_command("scripts/build_codex_adapter.py", "--output", str(output_dir))

    assert str(output_dir) in result.stdout
    manifest = json.loads((output_dir / ".codex-plugin" / "plugin.json").read_text())
    assert manifest["name"] == "heroku"
    assert manifest["skills"] == "./skills/"


def test_build_claude_adapter_outputs_bundle_with_manifest(tmp_path: Path) -> None:
    output_dir = tmp_path / "claude-bundle"
    result = run_command("scripts/build_claude_adapter.py", "--output", str(output_dir))

    assert str(output_dir) in result.stdout
    manifest = json.loads((output_dir / ".claude-plugin" / "plugin.json").read_text())
    assert manifest["name"] == "heroku"
    assert manifest["skills"] == "./skills/"
    assert manifest["mcpServers"] == "./.mcp.json"


def test_build_cursor_adapter_outputs_bundle_with_rule(tmp_path: Path) -> None:
    output_dir = tmp_path / "cursor-bundle"
    result = run_command("scripts/build_cursor_adapter.py", "--output", str(output_dir))

    assert str(output_dir) in result.stdout
    rule_path = output_dir / ".cursor" / "rules" / "heroku-skills.mdc"
    assert rule_path.exists()
    assert "Heroku Skills" in rule_path.read_text()


def test_validate_repo_script_passes() -> None:
    result = run_command("scripts/validate_repo.py")
    assert "Repository validation passed." in result.stdout
