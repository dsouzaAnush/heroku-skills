# App operations reference

## Read-only inspection commands

```bash
heroku apps:info -a <app> --json
heroku ps -a <app>
heroku releases:info -a <app>
heroku maintenance -a <app>
heroku logs -a <app> --num 200
```

## Change commands that require confirmation

```bash
heroku ps:scale web=2 worker=1 -a <app>
heroku ps:restart -a <app>
heroku maintenance:on -a <app>
heroku maintenance:off -a <app>
heroku releases:rollback v123 -a <app>
```

## Operational guidance

- Prefer bounded log reads before live tails.
- Treat rollbacks as behavior changes, not harmless inspection.
- Explain the expected effect of `heroku run` before executing it.
- Re-check release status after every operational change.

## Official docs

- <https://devcenter.heroku.com/articles/logging>
- <https://devcenter.heroku.com/articles/dynos>
- <https://devcenter.heroku.com/articles/releases>
- <https://devcenter.heroku.com/articles/maintenance-mode>
