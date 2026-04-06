# Domains and TLS reference

## Common inspection commands

```bash
heroku domains:info <hostname> -a <app>
heroku domains:wait <hostname> -a <app>
heroku certs:info -a <app> --show-domains
```

## ACM-first workflow

```bash
heroku domains:add <hostname> -a <app>
heroku certs:auto:enable -a <app> --wait
heroku certs:auto:refresh -a <app>
```

## Manual certificate workflow

```bash
heroku certs:add <crt> <key> -a <app>
heroku certs:update <crt> <key> -a <app> --name <name>
heroku domains:update <hostname> -a <app> --cert <name>
heroku certs:remove -a <app> --name <name>
```

## Operational guidance

- Prefer ACM unless the user explicitly needs manual certificate control.
- Validate DNS targets before expecting ACM to succeed.
- For apex or root domains, avoid A records that point directly at Heroku because endpoint IPs are not stable. Prefer DNS providers that support ALIAS, ANAME, CNAME flattening, or an equivalent apex-safe alias mechanism.
- For subdomains, use the DNS target returned by `heroku domains:info` and keep the provider record aligned with that hostname while waiting for ACM or manual certificate activation.
- Treat domain removal, certificate replacement, and hostname cutover as confirm-first changes.
- Use `domains:wait` after DNS or cert changes to confirm activation.

## Official docs

- <https://devcenter.heroku.com/articles/custom-domains>
- <https://devcenter.heroku.com/articles/automated-certificate-management>
- <https://devcenter.heroku.com/articles/ssl>
- <https://devcenter.heroku.com/articles/apex-domains>
