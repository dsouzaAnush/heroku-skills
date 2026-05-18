# Add-ons lifecycle reference

## Inspection commands

```bash
heroku addons:info <addon>
heroku addons:plans <service>
heroku addons:wait <addon> -a <app>
heroku addons:open <addon>
```

## Confirm-first lifecycle commands

```bash
heroku addons:create <service:plan> -a <app> --as <attachment>
heroku addons:attach <addon> -a <app> --as <attachment>
heroku addons:detach <attachment> -a <app>
heroku addons:upgrade <addon> <plan> -a <app>
heroku addons:destroy <addon> -a <app>
```

## Operational guidance

- Distinguish resource destruction from attachment removal.
- Attachment aliases can change which config vars an app sees.
- Many service-specific details belong in specialized skills such as Postgres, Key-Value Store, Connect, or AppLink.
- Call out any config-var overwrites or sharing implications before changing attachments.

## Official docs

- <https://devcenter.heroku.com/articles/managing-add-ons>
- <https://devcenter.heroku.com/articles/add-ons>
