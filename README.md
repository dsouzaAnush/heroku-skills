# Heroku Skills

![Heroku logo](assets/heroku-logo-dark-rgb.svg)

Portable Heroku-focused skills for AI agents.

This repository is organized as an agent-neutral `skills/` collection first. The core skills avoid platform-specific assumptions so they can be packaged for Codex, Claude, or other agents that understand the Agent Skills pattern. Agent-specific packaging lives under `adapters/`.

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
skills/            Portable skills
adapters/codex/    Codex packaging inputs
scripts/           Repo-level build and validation scripts
tests/             Unit and structure tests
evals/             Prompt-routing and coverage evals
assets/            Shared adapter assets
dist/              Generated adapter bundles
```

The canonical Codex source plugin lives at `adapters/codex/heroku/.codex-plugin/plugin.json`. It is self-contained and includes a plugin-local `skills/` mirror so it can be packaged or installed on its own. The build step refreshes that mirror from the portable root `skills/` tree and writes the distributable bundle under `dist/codex/heroku/`.

## Validation

Run the full repo validation:

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate_repo.py
```

This validates each skill with the local `quick_validate.py` helper, executes bundled helper scripts in safe default mode, verifies that the Codex source plugin mirrors the portable root skills, and builds the Codex adapter into `dist/codex/heroku`.

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

## Sources and conventions

The repo structure and authoring style are based on:

- Agent Skills conventions: <https://agentskills.io/>
- Heroku Dev Center documentation: <https://devcenter.heroku.com/>

## License

MIT
