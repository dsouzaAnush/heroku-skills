---
name: heroku-managed-inference
description: Use Heroku Managed Inference and Agents with the current Heroku AI workflow. Use when the agent needs to install or inspect the Heroku AI CLI plugin, provision Heroku inference model access, attach model resources, make test inference calls, or review Heroku-managed AI model operations.
---

# Heroku Managed Inference

Work with Heroku Managed Inference and Agents using the current add-on and CLI plugin model.

## Start with plugin and add-on inspection

Resolve this installed skill's directory first. Do not assume the current workspace contains the skill source repository.

Run the bundled inspection helper from this skill's `scripts/` directory:

```bash
python3 /path/to/heroku-managed-inference/scripts/plugin_status.py
```

Use the output to determine:

- whether the Heroku CLI is installed
- whether the Heroku AI plugin is already installed
- whether AI subcommands are available in the current shell

## Preferred workflow

Follow the current documented flow:

1. install the AI plugin if needed with `heroku plugins:install @heroku/plugin-ai`
2. create or identify the target app
3. provision model access with `heroku addons:create heroku-inference:standard -a <app>`
4. inspect available models with `heroku ai:models:list`
5. inspect attached resources with `heroku ai:models:info -a <app>`
6. make bounded test calls with `heroku ai:models:call <MODEL_RESOURCE> -a <app> --prompt '...'`

Prefer the add-on workflow over deprecated creation and destroy commands.

## Resource handling

- Use aliases intentionally when attaching multiple model resources to one app.
- Keep region alignment in mind when provisioning resources.
- Treat image, embedding, and chat model resources as separate operational concerns even when they live on one app.

## Guardrails

Ask for confirmation before:

- installing the Heroku AI plugin into a shared shell environment
- provisioning or destroying inference resources
- attaching a model resource from one app to another
- running test prompts that may expose sensitive data

Prefer harmless sample prompts when validating access.

## References

- Read `references/inference-workflows.md` for current commands, deprecations, and source links.
