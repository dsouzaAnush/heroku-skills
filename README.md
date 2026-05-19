<p align="center">
  <img src="assets/heroku-logo-dark-rgb.svg" alt="Heroku" height="44" />
</p>

# Heroku Skills

Portable Heroku-focused skills for AI agents.

This repository is organized as an agent-neutral `skills/` collection first. The core skills avoid platform-specific assumptions so they can be packaged for Codex, Claude Code, Cursor, or other agents that understand reusable rules and skill-style workflows. Agent-specific packaging lives under `adapters/`.

Pair these skills with [Heroku Code MCP](https://github.com/dsouzaAnush/heroku-code-mcp) when an agent needs a live Heroku API tool surface in addition to workflow guidance.

## Install

For most users, install the packaged [Heroku Plugin](https://github.com/dsouzaAnush/heroku-plugin). It vendors this skills tree and includes platform-specific manifests for Claude Code, Codex, and Cursor.

### <img src="https://claude.com/favicon.ico" alt="Claude Code" height="22" /> Claude Code

```bash
claude plugin marketplace add dsouzaAnush/heroku-plugin
claude plugin install heroku@heroku-plugin
claude plugin enable heroku@heroku-plugin
```

For a source-built Claude adapter:

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

Enable `heroku-plugin@heroku-plugin` in the Codex Plugins tab, or add this to `~/.codex/config.toml`:

```toml
[plugins."heroku-plugin@heroku-plugin"]
enabled = true
```

For a source-built Codex adapter:

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

For a source-built Cursor adapter:

```bash
git clone https://github.com/dsouzaAnush/heroku-skills.git
cd heroku-skills
python3 scripts/build_cursor_adapter.py
```

The generated Cursor bundle is `dist/cursor/heroku`. It includes `.cursor/rules/heroku-skills.mdc`, `mcp.json`, and a plugin-local `skills/` mirror.

## Included skills

- `deploy-to-heroku`
- `heroku-app-ops`
- `heroku-config-vars`
- `heroku-key-value-store`
- `heroku-domains-tls`
- `heroku-logging-drains`
- `heroku-addons`
- `heroku-managed-inference`
- `heroku-applink-connections`
- `heroku-applink-publications`
- `heroku-connect`
- `heroku-postgres`
- `heroku-pipelines-review-apps`
- `heroku-slack-agents`

Each skill keeps its `SKILL.md` concise and moves longer command catalogs and safety notes into `references/`. Deterministic, read-only helper scripts live in `scripts/` inside the relevant skill.

## Brand assets

This repo vendors the official Heroku logo assets from Heroku's January 2025 logo kit and keeps them in two places:

- repo-level copies under [`assets`](assets)
- per-skill copies under each skill's `assets/` directory so client UIs can render icons directly from an individual skill folder

Each skill's [`agents/openai.yaml`](skills/deploy-to-heroku/agents/openai.yaml) now includes:

- `icon_small`
- `icon_large`
- `brand_color`

The Codex source plugin manifest at [`adapters/codex/heroku/.codex-plugin/plugin.json`](adapters/codex/heroku/.codex-plugin/plugin.json) also points at the official repo-level wordmark and mark so plugin-aware clients can render Heroku branding directly from the packaged adapter.

Use the assets according to Heroku's official brand guidance:

- [Heroku Brand Guidelines](https://devcenter.heroku.com/articles/heroku-brand-guidelines)

## Repository layout

```text
skills/             Portable skills
adapters/codex/     Codex packaging inputs
adapters/claude/    Claude Code plugin inputs
adapters/cursor/    Cursor Project Rules inputs
scripts/            Repo-level build and validation scripts
tests/              Unit and structure tests
evals/              Prompt-routing and coverage evals
assets/             Shared adapter assets
dist/               Generated adapter bundles
```

The canonical Codex source plugin lives at `adapters/codex/heroku/.codex-plugin/plugin.json`. It is self-contained and includes a plugin-local `skills/` mirror so it can be packaged or installed on its own. The build step refreshes that mirror from the portable root `skills/` tree and writes the distributable bundle under `dist/codex/heroku/`.

The canonical Claude source plugin lives at `adapters/claude/heroku/.claude-plugin/plugin.json`. It includes the same plugin-local `skills/` mirror plus `.mcp.json` wiring for a local `heroku-code-mcp` HTTP server at `http://127.0.0.1:3333/mcp`.

The canonical Cursor source bundle lives at `adapters/cursor/heroku/.cursor/rules/heroku-skills.mdc`. It includes an agent-requested Cursor Project Rule plus the same plugin-local `skills/` mirror so Cursor can load the rule and then consult the detailed Heroku skill references on demand.

## MCP Integration

The Claude Code setup has three layers:

| Layer | Repository | What the client gets |
| --- | --- | --- |
| Heroku Code MCP | [`heroku-code-mcp`](https://github.com/dsouzaAnush/heroku-code-mcp) | Three live tools: `auth_status`, `search`, and `execute` |
| Heroku Skills | this repo | Safe Heroku workflows for deploys, app ops, config vars, Postgres, domains, add-ons, AppLink, Connect, Slack agents, and Managed Inference |
| Claude plugin | `dist/claude/heroku` | Claude Code plugin packaging that exposes the skills and wires the MCP server through `.mcp.json` |

Claude Code MCP setup follows Anthropic's [Claude Code MCP documentation](https://docs.anthropic.com/en/docs/claude-code/mcp).

### <img src="https://claude.com/favicon.ico" alt="Claude Code" height="22" /> Claude Code

Build and validate the plugin:

```bash
python3 scripts/build_claude_adapter.py
claude plugin validate dist/claude/heroku
```

Start the companion MCP server in the `heroku-code-mcp` repo:

```bash
heroku auth:whoami
npm run seed:token
TOKEN_STORE_PATH=./data/tokens.integration.json \
TOKEN_ENCRYPTION_KEY_BASE64='<seed-output-key>' \
PORT=3333 HOST=127.0.0.1 npm run dev
```

Load the plugin for a Claude Code session:

```bash
claude --plugin-dir dist/claude/heroku
```

Claude Code should show:

- plugin `heroku`
- namespaced skills such as `heroku:deploy-to-heroku` and `heroku:heroku-app-ops`
- MCP server `plugin:heroku:heroku-code-mcp`
- MCP tools `auth_status`, `search`, and `execute`

### <img src="https://claude.com/favicon.ico" alt="Claude Desktop" height="22" /> Claude Desktop

Claude Desktop can use the MCP server directly for live Heroku API access. Add this to `~/Library/Application Support/Claude/claude_desktop_config.json` when HTTP MCP is supported:

```json
{
  "mcpServers": {
    "heroku-code-mcp": {
      "type": "http",
      "url": "http://127.0.0.1:3333/mcp",
      "headers": {
        "x-user-id": "default"
      }
    }
  }
}
```

If your Claude Desktop build expects stdio servers, bridge to the local HTTP endpoint:

```json
{
  "mcpServers": {
    "heroku-code-mcp": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://127.0.0.1:3333/mcp", "--allow-http", "--header", "x-user-id:default"]
    }
  }
}
```

Restart Claude Desktop after changing the config. The classic Desktop chat surface uses MCP tools; the skills and plugin packaging are for Claude Code-style coding sessions.

### Remote code sessions

Use the Claude Code plugin path for cowork when the cowork runtime can load local plugins:

```bash
claude --plugin-dir dist/claude/heroku
```

For remote cowork sessions, run `heroku-code-mcp` where the cowork runtime can reach it, then update `adapters/claude/heroku/.mcp.json` or the generated `dist/claude/heroku/.mcp.json` to point at that endpoint. Keep token stores and seeded Heroku credentials private to the runtime; do not expose the local development token store on a public network.

## Validation

Run the full repo validation:

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate_repo.py
```

This validates each skill with the local `quick_validate.py` helper, executes bundled helper scripts in safe default mode, verifies that the Codex, Claude, and Cursor source adapters mirror the portable root skills, and builds the generated adapters into `dist/codex/heroku`, `dist/claude/heroku`, and `dist/cursor/heroku`.
CI uses the repo-local `scripts/quick_validate_skill.py` fallback so validation does not depend on Codex system skills being installed on the runner.

## Tests

Run the repo tests:

```bash
python3 -m pytest
```

The test suite checks repo integrity, self-contained adapter packaging, and helper-script behavior for representative skill workflows.
It also includes eval regression tests for historically ambiguous prompts so routing quality stays stable as skill metadata evolves.

## Usefulness eval

Run the usefulness eval to check whether realistic prompts route to the intended skill and whether each skill covers the concepts it promises:

```bash
python3 scripts/evaluate_skills.py
```

For a machine-readable report:

```bash
python3 scripts/evaluate_skills.py --json
```

This is a repo-local eval rather than an official Agent Skills standard. It audits:

- prompt-to-skill routing against a golden prompt set
- contrast prompts that force one skill to beat nearby alternatives
- content coverage for required commands and concepts per skill
- regressions where a skill becomes hard to trigger or no longer documents its core workflow

The current spec is intentionally broader than a smoke test:

- 56 positive routing prompts across the skill catalog
- 15 contrast prompts for high-confusion skill boundaries
- per-skill top-1 thresholds in addition to global top-1 and top-3 thresholds

## Build the Codex adapter

Create a self-contained Codex plugin bundle:

```bash
python3 scripts/build_codex_adapter.py
```

The generated bundle is written to:

```text
dist/codex/heroku
```

## Build the Code Plugin Adapter

Create a self-contained Claude Code plugin bundle:

```bash
python3 scripts/build_claude_adapter.py
```

The generated bundle is written to:

```text
dist/claude/heroku
```

Validate it with Claude Code:

```bash
claude plugin validate dist/claude/heroku
```

The plugin exposes the Heroku skills and an optional MCP server entry named `heroku-code-mcp`.
Start `heroku-code-mcp` separately before using those MCP tools.

## Build the Cursor adapter

Create a self-contained Cursor Project Rules bundle:

```bash
python3 scripts/build_cursor_adapter.py
```

The generated bundle is written to:

```text
dist/cursor/heroku
```

To use it in Cursor, copy or symlink `dist/cursor/heroku/.cursor/rules/heroku-skills.mdc` into the target project. Keep the generated `skills/` directory available beside it when you want Cursor to consult the detailed Heroku workflows, and copy `dist/cursor/heroku/mcp.json` into `~/.cursor/mcp.json` or project-local `.cursor/mcp.json` when `heroku-code-mcp` should expose live tools.

## CI/CD and Publish

This repo uses free GitHub Actions for public repositories:

- `validate.yml` runs tests, structure validation, adapter validation, and usefulness evals on PRs and pushes to `main`.
- `release.yml` runs on `v*` tags, builds Claude, Codex, and Cursor adapters, packages zip artifacts, and creates or updates the GitHub Release.
- Dependabot checks Python and GitHub Actions dependencies weekly.

This repo is the canonical portable skill source. Publishable artifacts are:

- GitHub source: `https://github.com/dsouzaAnush/heroku-skills`
- Claude adapter: `dist/claude/heroku`
- Codex adapter: `dist/codex/heroku`
- Cursor adapter: `dist/cursor/heroku`
- Packaged cross-agent plugin: `https://github.com/dsouzaAnush/heroku-plugin`

Before publishing or syncing into `heroku-plugin`:

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate_repo.py
python3 -m pytest -q
python3 scripts/evaluate_skills.py --json
```

Release a new skills/adapters package:

```bash
git tag v0.2.1
git push origin v0.2.1
```

The release workflow publishes downloadable adapter zips for Claude Code, Codex, and Cursor. The companion `heroku-plugin` repo remains the easiest install path for most users.

## Sources and conventions

The repo structure and authoring style are based on:

- Agent Skills conventions: <https://agentskills.io/>
- Heroku Dev Center documentation: <https://devcenter.heroku.com/>

## License

MIT
