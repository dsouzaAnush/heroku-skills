# Code Plugin Adapter

This directory contains Claude Code packaging inputs for the portable Heroku skills repo.

The canonical Claude source plugin lives at `adapters/claude/heroku/` and follows the
Claude Code plugin layout with `.claude-plugin/plugin.json`.

Build the self-contained plugin bundle with:

```bash
python3 scripts/build_claude_adapter.py
```

The generated bundle is written to `dist/claude/heroku/`.
