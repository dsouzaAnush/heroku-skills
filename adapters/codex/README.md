# Codex adapter

This directory contains the Codex-specific packaging inputs for the portable Heroku skills repo.

The canonical source plugin lives at `adapters/codex/heroku/` and follows the standard Codex plugin layout with `.codex-plugin/plugin.json`.

Build the self-contained plugin bundle with:

```bash
python3 scripts/build_codex_adapter.py
```

The generated bundle is written to `dist/codex/heroku/`.
