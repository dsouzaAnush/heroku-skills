# Deployment workflows

## Inspection checklist

- `heroku auth:whoami`
- `git remote -v`
- `heroku apps:info -a <app> --json`
- `heroku buildpacks -a <app>`
- `heroku apps:stacks -a <app>`

## Buildpack-first workflow

Use this when the app already matches Heroku's standard slug-based deployment model.

Typical commands:

```bash
heroku auth:whoami
heroku apps:create <app>
heroku git:remote -a <app>
git push heroku main
heroku releases:info -a <app>
heroku logs -a <app> --num 200
```

If the local default branch is not `main`, push explicitly:

```bash
git push heroku HEAD:main
```

## Container workflow

Use this only when Docker or `heroku.yml` is the intended runtime contract.

Typical commands:

```bash
heroku container:login
heroku container:push web -a <app>
heroku container:release web -a <app>
heroku releases:info -a <app>
```

## Safety notes

- Do not create or destroy apps without explicit confirmation.
- Treat buildpack changes and stack changes as behavior-changing operations.
- Prefer bounded log reads such as `--num 200` over `--tail` unless the user explicitly wants live log streaming.

## Official docs

- <https://devcenter.heroku.com/articles/git>
- <https://devcenter.heroku.com/articles/container-registry-and-runtime>
- <https://devcenter.heroku.com/articles/buildpacks>
- <https://devcenter.heroku.com/articles/procfile>
