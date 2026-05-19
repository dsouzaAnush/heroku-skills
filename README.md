<p align="center">
  <img src="assets/heroku-logo-dark-rgb.svg" alt="Heroku" height="44" />
</p>

# Heroku Skills

Portable Heroku workflows for AI coding agents.

This repo is the agent-neutral source of truth for Heroku skills. The core `skills/` tree avoids client-specific assumptions; `adapters/` packages the same content for Claude Code, Codex, Cursor, and other skill-aware clients. Pair these skills with [Heroku Code MCP](https://github.com/dsouzaAnush/heroku-code-mcp) when an agent needs live Heroku API tools.

## Install

For most users, install the packaged [Heroku Plugin](https://github.com/dsouzaAnush/heroku-plugin). It vendors this skills tree and includes client-specific manifests.

### <img src="https://claude.com/favicon.ico" alt="Claude Code" height="22" /> Claude Code

```bash
claude plugin marketplace add dsouzaAnush/heroku-plugin
claude plugin install heroku@heroku-plugin
claude plugin enable heroku@heroku-plugin
```

Source-built adapter:

```bash
git clone https://github.com/dsouzaAnush/heroku-skills.git
cd heroku-skills
python3 scripts/build_claude_adapter.py
claude plugin validate dist/claude/heroku
claude --plugin-dir dist/claude/heroku
```

### <img src="https://upload.wikimedia.org/wikipedia/commons/9/97/OpenAI_logo_2025.svg" alt="OpenAI Codex" height="22" /> Codex

```bash
codex plugin marketplace add dsouzaAnush/heroku-plugin --ref main
```

Enable `heroku-plugin@heroku-plugin` in the Codex Plugins tab, or add:

```toml
[plugins."heroku-plugin@heroku-plugin"]
enabled = true
```

Source-built adapter:

```bash
git clone https://github.com/dsouzaAnush/heroku-skills.git
cd heroku-skills
python3 scripts/build_codex_adapter.py
```

The generated Codex bundle is `dist/codex/heroku`.

### <img src="https://cursor.com/favicon.ico" alt="Cursor" height="22" /> Cursor

```bash
git clone https://github.com/dsouzaAnush/heroku-plugin.git
cursor agent --plugin-dir heroku-plugin
```

Source-built adapter:

```bash
git clone https://github.com/dsouzaAnush/heroku-skills.git
cd heroku-skills
python3 scripts/build_cursor_adapter.py
```

The generated Cursor bundle is `dist/cursor/heroku`.

## Skill Catalog

| Skill | Use when the task involves |
| --- | --- |
| `deploy-to-heroku` | Deployment readiness, app creation, Heroku Git, buildpacks, containers, and Procfiles |
| `heroku-app-ops` | App info, dynos, releases, logs, restarts, maintenance, and rollbacks |
| `heroku-config-vars` | Config inspection, diffing, setting, unsetting, and secret-safe handling |
| `heroku-postgres` | Postgres inspection, backups, credentials, promote, restore, and data movement |
| `heroku-key-value-store` | Heroku Key-Value Store and Redis-compatible state |
| `heroku-domains-tls` | Custom domains, DNS, ACM, certificates, and TLS cutovers |
| `heroku-logging-drains` | Logs, drains, telemetry handoff, and forwarding safety |
| `heroku-addons` | Add-on lifecycle, attachments, plans, upgrades, and destructive-operation guardrails |
| `heroku-pipelines-review-apps` | Pipelines, stages, review apps, app.json, and promotion flow |
| `heroku-managed-inference` | Heroku Managed Inference and Agents |
| `heroku-applink-connections` | AppLink org connections and Salesforce/Data Cloud authorization |
| `heroku-applink-publications` | Publishing Heroku apps into Salesforce and Agentforce |
| `heroku-connect` | Heroku Connect setup, mappings, sync health, and Salesforce auth |
| `heroku-slack-agents` | Slack Bolt apps, Request URLs, Socket Mode, and Heroku runtime setup |

Each skill keeps `SKILL.md` concise and moves longer command catalogs, safety notes, and helper scripts into `references/` and `scripts/`.

## Build Adapters

Build all client bundles:

```bash
python3 scripts/build_claude_adapter.py
python3 scripts/build_codex_adapter.py
python3 scripts/build_cursor_adapter.py
```

Outputs:
- `dist/claude/heroku`: Claude Code plugin bundle with `.mcp.json` wiring for `heroku-code-mcp`
- `dist/codex/heroku`: Codex plugin bundle with a local `skills/` mirror
- `dist/cursor/heroku`: Cursor rules bundle with `mcp.json` and a local `skills/` mirror

The source adapters live under `adapters/claude/heroku`, `adapters/codex/heroku`, and `adapters/cursor/heroku`.

## Validate and Evaluate

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pytest -q
python3 scripts/validate_repo.py
python3 scripts/evaluate_skills.py --json
```

Validation checks skill structure, helper scripts, adapter mirrors, generated bundles, and brand metadata. The usefulness eval checks prompt-to-skill routing, contrast prompts, and required content coverage across the catalog.

Current eval coverage:
- 56 positive routing prompts
- 15 contrast prompts for confusing skill boundaries
- per-skill top-1 thresholds plus global top-1 and top-3 thresholds

## CI/CD and Release

This repo uses free GitHub Actions:
- `validate.yml` runs tests, structure validation, adapter validation, and usefulness evals on PRs and pushes to `main`.
- `release.yml` runs on `v*` tags, builds Claude Code, Codex, and Cursor adapter zips, and creates or updates the GitHub Release.
- Dependabot checks Python and GitHub Actions dependencies weekly.

Release a new skills/adapters package:

```bash
git tag v0.2.1
git push origin v0.2.1
```

The packaged [Heroku Plugin](https://github.com/dsouzaAnush/heroku-plugin) remains the easiest install path; this repo remains the canonical skill source.

## Repository Layout

```text
skills/             Portable Heroku skills
adapters/           Claude Code, Codex, and Cursor packaging inputs
scripts/            Build, validation, and eval tooling
tests/              Unit and structure tests
evals/              Prompt-routing and coverage evals
assets/             Shared Heroku brand assets
dist/               Generated adapter bundles
```

## Brand and Sources

This repo vendors official Heroku logo assets under [`assets`](assets) and per-skill `assets/` folders so clients can render Heroku branding from packaged skills. Use them according to the [Heroku Brand Guidelines](https://devcenter.heroku.com/articles/heroku-brand-guidelines).

Conventions and references:
- Agent Skills: <https://agentskills.io/>
- Heroku Dev Center: <https://devcenter.heroku.com/>

## License

MIT
