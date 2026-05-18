# Heroku Key-Value Store reference

## Read-only inspection

```bash
heroku redis:info [DATABASE] -a <app> --json
heroku redis:credentials [DATABASE] -a <app>
heroku redis:wait [DATABASE] -a <app>
```

## Confirm-first operations

```bash
heroku redis:promote [DATABASE] -a <app>
heroku redis:credentials [DATABASE] -a <app> --reset
heroku redis:maxmemory [DATABASE] -a <app> --policy allkeys-lru
heroku redis:timeout [DATABASE] -a <app> --seconds 60
heroku redis:keyspace-notifications [DATABASE] -a <app> --config AKE
heroku redis:upgrade [DATABASE] -a <app> --version 7
```

## Connection and TLS guidance

- `REDIS_URL` is the current TLS connection var to use.
- Older references to `REDIS_TLS_URL` and `REDIS_TEMPORARY_URL` are obsolete for current common-runtime setups.
- Heroku Key-Value Store uses TLS and may require client SSL configuration that accepts the platform's certificate model.

## Operational guidance

- Promotion changes which store backs `REDIS_URL`; treat it as application-impacting.
- Credential resets invalidate existing clients.
- Memory policy, timeout, and keyspace notification changes alter runtime behavior and should be approved explicitly.
- Private and Shield deployment nuances belong in separate bounded investigation unless the user is clearly operating there.

## Official docs

- <https://devcenter.heroku.com/articles/heroku-redis>
- <https://devcenter.heroku.com/articles/connecting-heroku-redis>
- <https://devcenter.heroku.com/articles/heroku-redis-cli-commands>
- <https://devcenter.heroku.com/articles/heroku-redis-maintenance>
