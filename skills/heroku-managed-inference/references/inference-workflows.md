# Managed Inference workflows

## Install and inspect

```bash
heroku plugins:install @heroku/plugin-ai
heroku ai:models:list
heroku ai:models:info -a <app>
```

## Provision model access

Use the current add-on flow:

```bash
heroku addons:create heroku-inference:standard -a <app>
```

Region-specific provisioning is supported through add-on arguments:

```bash
heroku addons:create heroku-inference:<model-or-plan> -a <app> -- --region=us
```

## Attach and call models

```bash
heroku ai:models:attach <MODEL_RESOURCE> --source-app <source-app> --target-app <target-app> --as <ALIAS>
heroku ai:models:call <MODEL_RESOURCE> -a <app> --prompt "What is 1+2?"
heroku ai:models:info <MODEL_RESOURCE> -a <app>
```

## Current deprecations

- `heroku ai:models:create` is being deprecated in favor of `heroku addons:create heroku-inference:standard -a <app>`
- `heroku ai:models:destroy` is being deprecated in favor of `heroku addons:destroy <MODEL_RESOURCE> -a <app>`

## Operational guidance

- Use safe prompts for smoke tests.
- Keep app region and model region aligned.
- Prefer inspecting aliases and resource IDs before cross-app attaches.

## Official docs

- <https://devcenter.heroku.com/articles/heroku-inference>
- <https://devcenter.heroku.com/articles/heroku-inference-api>
- <https://devcenter.heroku.com/articles/heroku-inference-cli-commands>
