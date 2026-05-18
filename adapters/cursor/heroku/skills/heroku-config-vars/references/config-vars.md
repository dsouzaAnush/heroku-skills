# Config vars reference

## Inspection commands

```bash
heroku config -s -a <app>
heroku config:get <KEY> -a <app>
```

## Change commands

```bash
heroku config:set KEY=value -a <app>
heroku config:unset KEY -a <app>
```

## Working rules

- Inspect before editing.
- Prefer `config:get` when checking one or two variables instead of dumping the full config set into the transcript.
- Batch related keys into one approval step.
- Avoid echoing secret values back into summaries.
- Re-check release state after changes, because config updates can trigger a new release.

## Cross-environment checks

Compare:

- `.env.example`
- deployment docs
- app-specific runbooks
- existing Heroku config

## Official docs

- <https://devcenter.heroku.com/articles/config-vars>
- <https://devcenter.heroku.com/articles/heroku-local>
