# Pipelines and review apps reference

## Inspection commands

```bash
heroku pipelines:info <pipeline>
heroku pipelines:diff -a <upstream-app>
heroku apps:info -a <app> --json
```

## Change commands that require confirmation

```bash
heroku pipelines:create <pipeline>
heroku pipelines:add <pipeline> -a <app> -s staging
heroku pipelines:promote -a <app>
heroku reviewapps:enable -p <pipeline> -a <app>
heroku reviewapps:disable -p <pipeline> -a <app>
```

## `app.json` review points

Check for:

- required add-ons
- environment variables
- scripts or postdeploy hooks
- review-app-specific assumptions

## Operational guidance

- Prefer promotion when the user wants to move the same tested slug between stages.
- Review `app.json` before enabling review apps.
- Keep stage names explicit in summaries and commands.

## Official docs

- <https://devcenter.heroku.com/articles/pipelines>
- <https://devcenter.heroku.com/articles/github-integration-review-apps>
- <https://devcenter.heroku.com/articles/app-json-schema>
