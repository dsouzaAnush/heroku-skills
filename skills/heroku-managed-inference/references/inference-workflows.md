# Managed Inference workflows

## Install and inspect

```bash
heroku plugins:install @heroku/plugin-ai
heroku ai:models:list
heroku ai:models:info -a <app>
```

## Provision model access

Use the current standard-plan add-on flow:

```bash
heroku addons:create heroku-inference:standard -a <app>
```

The standard plan is the recommended default because one add-on and one API key provide access to the supported catalog without reprovisioning for every model change.

Region-specific provisioning is supported through add-on arguments:

```bash
heroku addons:create heroku-inference:standard -a <app> -- --region=us
```

## Current catalog notes

Heroku announced these additions on February 19, 2026:

- Claude Opus 4.6
- Claude Sonnet 4.6
- DeepSeek v3.2
- Kimi K2.5
- MiniMax M2.1
- ZAI GLM 4.7
- ZAI GLM 4.7 Flash
- Cohere Embed v4

The live Elements listing also shows current standard-plan catalog entries such as Claude 4.5 and 4.6 variants, Cohere Embed v4, and the new open-weight models. Prefer checking `heroku ai:models:list` before making a final recommendation.

## Attach and call models

```bash
heroku ai:models:attach <MODEL_RESOURCE> --source-app <source-app> --target-app <target-app> --as <ALIAS>
heroku ai:models:call <MODEL_RESOURCE> -a <app> --prompt "What is 1+2?"
heroku ai:models:info <MODEL_RESOURCE> -a <app>
```

## Current deprecations

- `heroku ai:models:create` is being deprecated in favor of `heroku addons:create heroku-inference:standard -a <app>`
- `heroku ai:models:destroy` is being deprecated in favor of `heroku addons:destroy <MODEL_RESOURCE> -a <app>`
- Heroku's February 19, 2026 update says older Claude 3.5, Claude 3.7, and Claude 4 versions are entering deprecation and users should migrate toward Claude 4.5 or 4.6.

## Operational guidance

- Use safe prompts for smoke tests.
- Keep app region and model region aligned.
- Prefer inspecting aliases and resource IDs before cross-app attaches.

## Official docs

- <https://devcenter.heroku.com/articles/heroku-inference>
- <https://devcenter.heroku.com/articles/heroku-inference-api>
- <https://devcenter.heroku.com/articles/heroku-inference-cli-commands>
