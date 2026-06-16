# Windows Personal Archive (`wpa`)

Open-source CLI tool to **find and archive personal files** across all local drives on a Windows PC, producing a structured archive and manifest so you can restore on another **Windows 10** machine without losing personal data.

**Status:** Requirements and specification complete — implementation in progress (v0.1.0).

## Why this exists

Migrating away from Windows (or to a new Windows PC) means tracking down files in user profiles, `AppData`, secondary drives, and ad-hoc folders. Manual copy-paste misses things. `wpa` automates discovery, documents what was copied, and uses a predictable archive layout.

## Documentation

| Document | Purpose |
|----------|---------|
| [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) | Goals, functional/non-functional requirements, open questions |
| [docs/SPEC.md](docs/SPEC.md) | Architecture, archive layout, CLI, manifest schema |
| [docs/RESTORE.md](docs/RESTORE.md) | Windows 10 restore guide (draft) |

## Quick start (developers)

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12+.

```powershell
# Windows — from repo root
.\scripts\bootstrap.ps1
uv run wpa --help
```

```bash
# Linux/macOS — run tests only (Windows APIs stubbed in CI)
uv sync
uv run pytest
```

## Planned CLI

```powershell
wpa scan --output E:\migration --dry-run      # inventory only
wpa archive --output E:\migration             # copy + manifest
wpa verify --output E:\migration              # integrity check
```

## Engineering standards

This repo follows the project boilerplate spec:

- **uv** for dependencies (no global pip installs)
- **ruff** for lint + format
- **pyright** strict mode
- **pytest** for tests
- CI on every PR

Docker/IaC sections of the boilerplate are **not applicable** for this local Windows CLI — see `docs/REQUIREMENTS.md` §10.

## License

MIT (pending stakeholder confirmation — see open questions in REQUIREMENTS.md).

## Contributing

Implementation has not started yet. See `docs/SPEC.md` for module layout and `docs/REQUIREMENTS.md` §11 for decisions still needed from the project owner.
