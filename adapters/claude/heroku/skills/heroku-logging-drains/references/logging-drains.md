# Logging and drains reference

## Choose the workflow by app generation

- Common Runtime apps use classic `heroku logs` history plus `drains:*` for persistent forwarding.
- Fir apps do not use classic log drains. `heroku logs` behaves like a live stream, and persistent forwarding should use telemetry drains such as `heroku telemetry:add`.
- If app generation is unclear, check `heroku apps:info -a <app> --json` and confirm before proposing any forwarding change.

## Common inspection commands

```bash
heroku logs -a <app> --num 200
heroku logs -a <app> --process-type web --num 200
heroku drains -a <app> --json
```

For Fir apps, use:

```bash
heroku logs -a <app>
heroku telemetry:add <endpoint> --app <app> --signals logs
```

## Confirm-first drain changes

```bash
heroku drains:add <url> -a <app>
heroku drains:remove <url> -a <app>
```

## Space-specific references

```bash
heroku drains:get -s <space> --json
heroku spaces:drains:set <url> -s <space>
```

## Operational guidance

- Application logs and space-level logging are related but not the same workflow.
- For Common Runtime apps, Heroku logs are best for bounded inspection and drains are for persistent forwarding.
- For Fir apps, telemetry drains replace the classic drain workflow and historical log reads are not available through `heroku logs --num`.
- Be cautious about forwarding credentials, request payloads, or personal data to drain targets.
- Prefer explicit app-scoped drain reviews before adding or removing destinations.

## Official docs

- <https://devcenter.heroku.com/articles/logging>
- <https://devcenter.heroku.com/articles/log-drains>
- <https://devcenter.heroku.com/articles/heroku-telemetry>
- <https://devcenter.heroku.com/articles/log-runtime-metrics>
