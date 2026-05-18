#!/usr/bin/env python3
"""Build a self-contained Claude Code plugin bundle from the portable skills repo."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


REQUIRED_TEMPLATE_FIELDS = {
    "name": "heroku",
}


def load_template(template_path: Path) -> dict:
    payload = json.loads(template_path.read_text())
    for key, expected in REQUIRED_TEMPLATE_FIELDS.items():
        actual = payload.get(key)
        if actual != expected:
            raise ValueError(
                f"Template field {key!r} must be {expected!r}, found {actual!r}"
            )
    return payload


def copy_required_tree(source: Path, destination: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(f"Required source path not found: {source}")
    shutil.copytree(source, destination)


def sync_source_plugin_assets(repo_root: Path) -> None:
    plugin_root = repo_root / "adapters" / "claude" / "heroku"
    plugin_assets = plugin_root / "assets"
    if plugin_assets.exists():
        shutil.rmtree(plugin_assets)
    shutil.copytree(repo_root / "assets", plugin_assets)


def sync_source_plugin_skills(repo_root: Path) -> Path:
    plugin_root = repo_root / "adapters" / "claude" / "heroku"
    source_skills = repo_root / "skills"
    plugin_skills = plugin_root / "skills"

    if plugin_skills.exists():
        shutil.rmtree(plugin_skills)
    shutil.copytree(source_skills, plugin_skills)
    return plugin_skills


def build_bundle(repo_root: Path, output_dir: Path) -> Path:
    plugin_root = repo_root / "adapters" / "claude" / "heroku"
    sync_source_plugin_assets(repo_root)
    sync_source_plugin_skills(repo_root)
    template_path = plugin_root / ".claude-plugin" / "plugin.json"
    plugin_manifest = load_template(template_path)

    if output_dir.exists():
        shutil.rmtree(output_dir)

    copy_required_tree(plugin_root, output_dir)

    license_path = repo_root / "LICENSE"
    if license_path.exists():
        shutil.copy2(license_path, output_dir / "LICENSE")

    plugin_manifest["skills"] = "./skills/"
    plugin_manifest["mcpServers"] = "./.mcp.json"
    plugin_dir = output_dir / ".claude-plugin"
    (plugin_dir / "plugin.json").write_text(json.dumps(plugin_manifest, indent=2) + "\n")
    return output_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=None,
        help="Output directory for the Claude adapter bundle",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    output_dir = (
        Path(args.output).expanduser().resolve()
        if args.output
        else repo_root / "dist" / "claude" / "heroku"
    )
    bundle_path = build_bundle(repo_root, output_dir)
    print(bundle_path)


if __name__ == "__main__":
    main()
