# Cursor adapter

This directory contains Cursor Project Rules packaging inputs for the portable Heroku skills repo.

The canonical Cursor source bundle lives at `adapters/cursor/heroku/` and follows Cursor's `.cursor/rules/*.mdc` project-rule layout.

Build the self-contained Cursor bundle with:

```bash
python3 scripts/build_cursor_adapter.py
```

The generated bundle is written to `dist/cursor/heroku/`.
