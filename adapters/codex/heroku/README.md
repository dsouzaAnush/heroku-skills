# Heroku Codex Source Plugin

This is the canonical Codex source plugin for the portable Heroku skills repo.

- `.codex-plugin/plugin.json` contains the source manifest.
- `assets/` contains plugin-local assets for direct consumption.
- `skills/` contains the plugin-local mirror of the portable root skill set.

Refresh the plugin-local skill mirror and build a distributable bundle with:

```bash
python3 scripts/build_codex_adapter.py
```
