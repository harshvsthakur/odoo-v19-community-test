# Odoo v19 Community Test

A personal Docker-based dev environment for Odoo 19.0 (Community edition) — used to build and
test custom Odoo modules end-to-end with an agentic Claude Code pipeline (ticket → PRD → code →
tests → PR → release notes).

## Stack

- **Odoo**: 19.0 (Community), official `odoo:19.0` image
- **Database**: Postgres 16
- Custom modules live under `addons/` and are mounted into the container automatically.

## Running it

```bash
docker compose up -d
```

Odoo is reachable at `http://localhost:8069`. First run prompts for database creation through
the web UI.

```bash
# Follow logs
docker compose logs -f odoo

# Stop the stack
docker compose down

# Shell inside the Odoo container
docker compose exec odoo bash
```

## Adding a custom module

Drop it under `addons/<module_name>/` with a standard Odoo module layout
(`__manifest__.py`, `models/`, `views/`, etc.) — no changes to `odoo.conf` or
`docker-compose.yml` are needed. Then install/upgrade it:

```bash
docker compose exec odoo odoo -u <module_name> -d harsh-test-v19 --stop-after-init
docker compose restart odoo
```
