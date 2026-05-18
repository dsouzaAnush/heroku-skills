# Heroku Postgres reference

## Read-only commands

```bash
heroku pg:info -a <app>
heroku pg:backups -a <app>
heroku pg:credentials -a <app>
heroku pg:psql -a <app>
heroku pg:diagnose -a <app>
```

## Confirm-first commands

```bash
heroku addons:create heroku-postgresql:<plan> -a <app>
heroku pg:promote <database> -a <app>
heroku pg:backups:restore <backup-url-or-id> DATABASE_URL -a <app>
heroku pg:credentials:rotate <database> -a <app>
heroku pg:reset <database> -a <app>
```

## Operational guidance

- Identify the current primary attachment before proposing promotions.
- Check backup status before any risky database change.
- Use `pg:psql` only when the user wants direct SQL inspection and keep that inspection bounded.
- Treat `pg:push`, `pg:pull`, `pg:reset`, and restore commands as explicit approval points.
- Avoid exposing raw credentials in summaries.

## Official docs

- <https://devcenter.heroku.com/articles/heroku-postgres>
- <https://devcenter.heroku.com/articles/heroku-postgres-backups>
- <https://devcenter.heroku.com/articles/heroku-postgres-credentials>
