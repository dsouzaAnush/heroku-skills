# Heroku Cursor Source Bundle

This is the canonical Cursor source bundle for the portable Heroku skills repo.

- `.cursor/rules/heroku-skills.mdc` contains the Cursor Project Rule.
- `assets/` contains bundle-local Heroku and Claude brand assets.
- `skills/` contains the bundle-local mirror of the portable root skill set.

Refresh the bundle-local skill mirror and build a distributable bundle with:

```bash
python3 scripts/build_cursor_adapter.py
```

To use in Cursor, copy or symlink the generated `.cursor/rules/heroku-skills.mdc` file into the target project and keep the `skills/` directory available beside it when you want detailed workflow references.
