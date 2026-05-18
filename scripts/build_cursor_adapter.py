#!/usr/bin/env python3
"""Build a self-contained Cursor rules bundle from the portable skills repo."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


RULE_BODY = """---
description: Heroku platform workflows for deployment, app operations, config vars, Postgres, Key-Value Store, domains/TLS, logging, add-ons, pipelines, Managed Inference, AppLink, Heroku Connect, and Slack agents.
globs:
alwaysApply: false
---

# Heroku Skills

Use this rule when a Cursor task involves Heroku apps, deployments, runtime operations, data services, networking, Salesforce integrations, Managed Inference, or Slack agents on Heroku.

Start read-only. Prefer `heroku apps:info`, `heroku releases:info`, bounded logs, and service inspection before changing apps, add-ons, config vars, domains, drains, credentials, or data.

Ask before production-changing actions: app creation, deploys, rollbacks, add-on provisioning or destruction, database restores, credential rotation, DNS/TLS cutovers, buildpack or stack changes, pipeline promotions, and Slack app token changes.

Use the bundled skill source in `skills/<skill-name>/SKILL.md` as the detailed workflow reference:

- `deploy-to-heroku`: deployment readiness, Heroku Git, container deploys, app creation, and remotes.
- `heroku-app-ops`: dynos, releases, maintenance, logs, rollbacks, and incident inspection.
- `heroku-config-vars`: config inspection, diffing, setting, unsetting, and secret-safe handling.
- `heroku-postgres`: Postgres inspection, backups, credentials, promote, restore, and data movement.
- `heroku-key-value-store`: Heroku Key-Value Store and Redis-compatible workflows.
- `heroku-domains-tls`: custom domains, DNS, ACM, certs, and TLS cutovers.
- `heroku-logging-drains`: bounded logs, drains, observability handoff, and log forwarding.
- `heroku-addons`: add-on lifecycle, attachments, upgrades, plans, and destructive-operation guardrails.
- `heroku-pipelines-review-apps`: pipelines, stages, review apps, promotion, and app.json.
- `heroku-managed-inference`: Heroku Managed Inference and Agents workflows.
- `heroku-applink-connections`: AppLink org connections and Salesforce/Data Cloud auth.
- `heroku-applink-publications`: publishing Heroku apps into Salesforce and Agentforce.
- `heroku-connect`: Heroku Connect sync, mappings, Postgres/Salesforce inspection, and plugin checks.
- `heroku-slack-agents`: Slack Bolt JS/TS agents deployed on Heroku.

Load only the relevant skill and its directly linked `references/` files. Run bundled helper scripts from that skill's `scripts/` directory when a deterministic read-only snapshot is useful.
"""


def copy_tree(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def sync_source_adapter(repo_root: Path) -> Path:
    adapter_root = repo_root / "adapters" / "cursor" / "heroku"
    rules_dir = adapter_root / ".cursor" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    (rules_dir / "heroku-skills.mdc").write_text(RULE_BODY)

    copy_tree(repo_root / "skills", adapter_root / "skills")
    copy_tree(repo_root / "assets", adapter_root / "assets")
    return adapter_root


def build_bundle(repo_root: Path, output_dir: Path) -> Path:
    adapter_root = sync_source_adapter(repo_root)

    if output_dir.exists():
        shutil.rmtree(output_dir)

    shutil.copytree(adapter_root, output_dir)

    license_path = repo_root / "LICENSE"
    if license_path.exists():
        shutil.copy2(license_path, output_dir / "LICENSE")

    return output_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=None,
        help="Output directory for the Cursor adapter bundle",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    output_dir = (
        Path(args.output).expanduser().resolve()
        if args.output
        else repo_root / "dist" / "cursor" / "heroku"
    )
    bundle_path = build_bundle(repo_root, output_dir)
    print(bundle_path)


if __name__ == "__main__":
    main()
