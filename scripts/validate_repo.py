#!/usr/bin/env python3
"""Validate portable skills and the generated Codex, Claude, and Cursor adapters."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from os import environ
from hashlib import sha256
from pathlib import Path


REQUIRED_SKILLS = {
    "deploy-to-heroku",
    "heroku-addons",
    "heroku-app-ops",
    "heroku-applink-connections",
    "heroku-applink-publications",
    "heroku-config-vars",
    "heroku-connect",
    "heroku-domains-tls",
    "heroku-key-value-store",
    "heroku-logging-drains",
    "heroku-managed-inference",
    "heroku-postgres",
    "heroku-pipelines-review-apps",
    "heroku-slack-agents",
}


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)


def assert_ok(result: subprocess.CompletedProcess[str], context: str) -> None:
    if result.returncode != 0:
        message = result.stdout.strip() or result.stderr.strip()
        raise RuntimeError(f"{context} failed: {message}")


def load_frontmatter(skill_dir: Path) -> dict:
    content = (skill_dir / "SKILL.md").read_text()
    if not content.startswith("---\n"):
        raise RuntimeError(f"{skill_dir.name}: SKILL.md is missing frontmatter")
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        raise RuntimeError(f"{skill_dir.name}: SKILL.md frontmatter is invalid")

    frontmatter: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            raise RuntimeError(f"{skill_dir.name}: invalid frontmatter line {line!r}")
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip()
    return frontmatter


def validate_descriptions(skills_root: Path) -> None:
    names = {path.name for path in skills_root.iterdir() if path.is_dir()}
    if names != REQUIRED_SKILLS:
        raise RuntimeError(f"Unexpected skill set: {sorted(names)}")

    for skill_dir in sorted(skills_root.iterdir()):
        if not skill_dir.is_dir():
            continue
        frontmatter = load_frontmatter(skill_dir)
        description = frontmatter["description"].lower()
        if "use when" not in description:
            raise RuntimeError(
                f"{skill_dir.name}: description should include explicit trigger guidance"
            )
        if "heroku" not in description:
            raise RuntimeError(f"{skill_dir.name}: description should mention Heroku")
        content = (skill_dir / "SKILL.md").read_text()
        if re.search(r"\bpython3 skills/[^ ]+/scripts/", content):
            raise RuntimeError(
                f"{skill_dir.name}: SKILL.md should not hard-code repo-relative script paths"
            )


def validate_agents_metadata(repo_root: Path) -> None:
    for skill_dir in sorted((repo_root / "skills").iterdir()):
        if not skill_dir.is_dir():
            continue

        metadata_path = skill_dir / "agents" / "openai.yaml"
        if not metadata_path.exists():
            raise RuntimeError(f"{skill_dir.name}: missing agents/openai.yaml")

        content = metadata_path.read_text()
        for required_key in (
            "display_name",
            "short_description",
            "icon_small",
            "icon_large",
            "brand_color",
            "default_prompt",
        ):
            if f"{required_key}:" not in content:
                raise RuntimeError(f"{skill_dir.name}: agents/openai.yaml missing {required_key}")
        if f"Use ${skill_dir.name}" not in content:
            raise RuntimeError(
                f"{skill_dir.name}: default_prompt should explicitly mention ${skill_dir.name}"
            )

        for asset_name in ("heroku-mark-dark-rgb.svg", "heroku-logo-dark-rgb.svg"):
            asset_path = skill_dir / "assets" / asset_name
            if not asset_path.exists():
                raise RuntimeError(f"{skill_dir.name}: missing brand asset {asset_name}")


def validate_skills(repo_root: Path) -> None:
    validator = resolve_quick_validator()
    skills_root = repo_root / "skills"
    validate_descriptions(skills_root)
    validate_agents_metadata(repo_root)

    yaml_check = run(["python3", "-c", "import yaml"], cwd=repo_root)
    assert_ok(
        yaml_check,
        "PyYAML availability check (install with `python3 -m pip install -r requirements-dev.txt`)",
    )

    for skill_dir in sorted(skills_root.iterdir()):
        if not skill_dir.is_dir():
            continue
        result = run(["python3", str(validator), str(skill_dir)], cwd=repo_root)
        assert_ok(result, f"quick_validate for {skill_dir.name}")


def resolve_quick_validator() -> Path:
    candidates = [
        environ.get("QUICK_VALIDATE_PATH"),
        str(Path.home() / ".codex" / "skills" / ".system" / "skill-creator" / "scripts" / "quick_validate.py"),
    ]

    for candidate in candidates:
        if not candidate:
            continue
        validator = Path(candidate).expanduser()
        if validator.exists():
            return validator

    raise RuntimeError(
        "Could not find quick_validate.py. Set QUICK_VALIDATE_PATH or install the Codex skill-creator system skill."
    )


def validate_helper_scripts(repo_root: Path) -> None:
    for script_path in sorted((repo_root / "skills").glob("*/scripts/*.py")):
        result = run(["python3", str(script_path)], cwd=repo_root)
        assert_ok(result, f"helper script {script_path.relative_to(repo_root)}")
        try:
            json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"{script_path.relative_to(repo_root)} did not emit JSON"
            ) from exc


def directory_fingerprint(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def validate_adapter(repo_root: Path) -> None:
    validate_codex_adapter(repo_root)
    validate_claude_adapter(repo_root)
    validate_cursor_adapter(repo_root)


def validate_codex_adapter(repo_root: Path) -> None:
    plugin_root = repo_root / "adapters" / "codex" / "heroku"
    source_manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
    if not source_manifest_path.exists():
        raise RuntimeError("Source Codex plugin manifest is missing")

    source_manifest = json.loads(source_manifest_path.read_text())
    if source_manifest.get("name") != "heroku":
        raise RuntimeError("Source plugin name must be 'heroku'")
    if source_manifest.get("skills") != "./skills/":
        raise RuntimeError("Source plugin skills path must be './skills/'")
    interface = source_manifest.get("interface", {})
    if interface.get("composerIcon") != "./assets/heroku-mark-dark-rgb.svg":
        raise RuntimeError("Source plugin composerIcon must use the official Heroku mark")
    if interface.get("logo") != "./assets/heroku-logo-dark-rgb.svg":
        raise RuntimeError("Source plugin logo must use the official Heroku wordmark")
    if interface.get("brandColor") != "#D7BFF2":
        raise RuntimeError("Source plugin brandColor must match the official Heroku brand color")

    for asset_name in ("heroku-mark-dark-rgb.svg", "heroku-logo-dark-rgb.svg"):
        asset_path = plugin_root / "assets" / asset_name
        if not asset_path.exists():
            raise RuntimeError(f"Source plugin missing brand asset {asset_name}")

    source_manifest_text = source_manifest_path.read_text()
    if "[TODO:" in source_manifest_text:
        raise RuntimeError("Source plugin manifest still contains TODO placeholders")

    source_plugin_skills = plugin_root / "skills"
    if not source_plugin_skills.exists():
        raise RuntimeError("Source plugin is missing its bundled skills directory")

    root_fingerprint = directory_fingerprint(repo_root / "skills")
    plugin_fingerprint = directory_fingerprint(source_plugin_skills)
    if plugin_fingerprint != root_fingerprint:
        raise RuntimeError(
            "Source plugin skills do not match the portable root skills. "
            "Run `python3 scripts/build_codex_adapter.py` to resync them."
        )

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "heroku"
        build_script = repo_root / "scripts" / "build_codex_adapter.py"
        result = run(["python3", str(build_script), "--output", str(output_dir)], cwd=repo_root)
        assert_ok(result, "Codex adapter build")

        manifest_path = output_dir / ".codex-plugin" / "plugin.json"
        if not manifest_path.exists():
            raise RuntimeError("Built plugin.json was not created")

        manifest = json.loads(manifest_path.read_text())
        if manifest.get("name") != "heroku":
            raise RuntimeError("Built plugin name must be 'heroku'")
        if manifest.get("skills") != "./skills/":
            raise RuntimeError("Built plugin skills path must be './skills/'")

        built_skills = {path.name for path in (output_dir / "skills").iterdir() if path.is_dir()}
        if built_skills != REQUIRED_SKILLS:
            raise RuntimeError(f"Built bundle has unexpected skills: {sorted(built_skills)}")


def validate_claude_adapter(repo_root: Path) -> None:
    plugin_root = repo_root / "adapters" / "claude" / "heroku"
    source_manifest_path = plugin_root / ".claude-plugin" / "plugin.json"
    if not source_manifest_path.exists():
        raise RuntimeError("Source Claude plugin manifest is missing")

    source_manifest = json.loads(source_manifest_path.read_text())
    if source_manifest.get("name") != "heroku":
        raise RuntimeError("Source Claude plugin name must be 'heroku'")
    if source_manifest.get("skills") != "./skills/":
        raise RuntimeError("Source Claude plugin skills path must be './skills/'")
    if source_manifest.get("mcpServers") != "./.mcp.json":
        raise RuntimeError("Source Claude plugin mcpServers path must be './.mcp.json'")
    forbidden_keys = {"interface"}
    unexpected = forbidden_keys.intersection(source_manifest)
    if unexpected:
        raise RuntimeError(f"Source Claude plugin contains Claude-incompatible keys: {sorted(unexpected)}")

    mcp_path = plugin_root / ".mcp.json"
    if not mcp_path.exists():
        raise RuntimeError("Source Claude plugin is missing .mcp.json")
    mcp_config = json.loads(mcp_path.read_text())
    server = mcp_config.get("mcpServers", {}).get("heroku-code-mcp")
    if not server:
        raise RuntimeError("Source Claude plugin .mcp.json must define heroku-code-mcp")
    if server.get("type") != "http":
        raise RuntimeError("heroku-code-mcp must use HTTP transport for Claude")
    if server.get("url") != "http://127.0.0.1:3333/mcp":
        raise RuntimeError("heroku-code-mcp must point at http://127.0.0.1:3333/mcp")
    if server.get("headers", {}).get("x-user-id") != "default":
        raise RuntimeError("heroku-code-mcp must set x-user-id: default")

    for asset_name in ("heroku-mark-dark-rgb.svg", "heroku-logo-dark-rgb.svg", "claude-ai-logo.svg"):
        asset_path = plugin_root / "assets" / asset_name
        if not asset_path.exists():
            raise RuntimeError(f"Source Claude plugin missing brand asset {asset_name}")

    source_plugin_skills = plugin_root / "skills"
    if not source_plugin_skills.exists():
        raise RuntimeError("Source Claude plugin is missing its bundled skills directory")

    root_fingerprint = directory_fingerprint(repo_root / "skills")
    plugin_fingerprint = directory_fingerprint(source_plugin_skills)
    if plugin_fingerprint != root_fingerprint:
        raise RuntimeError(
            "Source Claude plugin skills do not match the portable root skills. "
            "Run `python3 scripts/build_claude_adapter.py` to resync them."
        )

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "heroku"
        build_script = repo_root / "scripts" / "build_claude_adapter.py"
        result = run(["python3", str(build_script), "--output", str(output_dir)], cwd=repo_root)
        assert_ok(result, "Claude adapter build")

        manifest_path = output_dir / ".claude-plugin" / "plugin.json"
        if not manifest_path.exists():
            raise RuntimeError("Built Claude plugin.json was not created")

        manifest = json.loads(manifest_path.read_text())
        if manifest.get("name") != "heroku":
            raise RuntimeError("Built Claude plugin name must be 'heroku'")
        if manifest.get("skills") != "./skills/":
            raise RuntimeError("Built Claude plugin skills path must be './skills/'")
        if manifest.get("mcpServers") != "./.mcp.json":
            raise RuntimeError("Built Claude plugin mcpServers path must be './.mcp.json'")

        built_skills = {path.name for path in (output_dir / "skills").iterdir() if path.is_dir()}
        if built_skills != REQUIRED_SKILLS:
            raise RuntimeError(f"Built Claude bundle has unexpected skills: {sorted(built_skills)}")


def validate_cursor_adapter(repo_root: Path) -> None:
    adapter_root = repo_root / "adapters" / "cursor" / "heroku"
    rule_path = adapter_root / ".cursor" / "rules" / "heroku-skills.mdc"
    if not rule_path.exists():
        raise RuntimeError("Source Cursor adapter is missing .cursor/rules/heroku-skills.mdc")

    rule_text = rule_path.read_text()
    if not rule_text.startswith("---\n"):
        raise RuntimeError("Cursor rule is missing MDC frontmatter")
    if "description:" not in rule_text.split("---", 2)[1]:
        raise RuntimeError("Cursor rule frontmatter must include description")
    if "alwaysApply: false" not in rule_text.split("---", 2)[1]:
        raise RuntimeError("Cursor rule should be agent-requested rather than always-on")
    if "skills/<skill-name>/SKILL.md" not in rule_text:
        raise RuntimeError("Cursor rule must point agents at the bundled skill references")

    for skill_name in REQUIRED_SKILLS:
        if f"`{skill_name}`" not in rule_text:
            raise RuntimeError(f"Cursor rule does not mention {skill_name}")

    for asset_name in ("heroku-mark-dark-rgb.svg", "heroku-logo-dark-rgb.svg"):
        asset_path = adapter_root / "assets" / asset_name
        if not asset_path.exists():
            raise RuntimeError(f"Source Cursor adapter missing brand asset {asset_name}")

    source_adapter_skills = adapter_root / "skills"
    if not source_adapter_skills.exists():
        raise RuntimeError("Source Cursor adapter is missing its bundled skills directory")

    root_fingerprint = directory_fingerprint(repo_root / "skills")
    adapter_fingerprint = directory_fingerprint(source_adapter_skills)
    if adapter_fingerprint != root_fingerprint:
        raise RuntimeError(
            "Source Cursor adapter skills do not match the portable root skills. "
            "Run `python3 scripts/build_cursor_adapter.py` to resync them."
        )

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "heroku"
        build_script = repo_root / "scripts" / "build_cursor_adapter.py"
        result = run(["python3", str(build_script), "--output", str(output_dir)], cwd=repo_root)
        assert_ok(result, "Cursor adapter build")

        built_rule = output_dir / ".cursor" / "rules" / "heroku-skills.mdc"
        if not built_rule.exists():
            raise RuntimeError("Built Cursor rule was not created")

        built_skills = {path.name for path in (output_dir / "skills").iterdir() if path.is_dir()}
        if built_skills != REQUIRED_SKILLS:
            raise RuntimeError(f"Built Cursor bundle has unexpected skills: {sorted(built_skills)}")


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    validate_skills(repo_root)
    validate_helper_scripts(repo_root)
    validate_adapter(repo_root)
    print("Repository validation passed.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        sys.exit(1)
