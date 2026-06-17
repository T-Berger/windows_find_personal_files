# Windows Personal Archive (`wpa`)

Open-source CLI tool to **find and archive personal files** across all local drives on a Windows PC, producing a structured archive and manifest so you can restore on another **Windows 10** machine without losing personal data.

**Status:** v0.1.0 — scan, archive, verify, and restore implemented.

## Security

Archives can contain passwords, browser profiles, keys, and other personal data. Store migration output only on trusted media, restrict access to the files, and encrypt external drives or cloud copies yourself — `wpa` does not encrypt archives in v1. Treat any archive like a full backup of your private data.

## Why this exists

Migrating away from Windows (or to a new Windows PC) means tracking down files in user profiles, `AppData`, secondary drives, and ad-hoc folders. Manual copy-paste misses things. `wpa` automates discovery, documents what was copied, and uses a predictable archive layout.

## Documentation

| Document | Purpose |
|----------|---------|
| [docs/DECISIONS.md](docs/DECISIONS.md) | Locked stakeholder decisions |
| [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) | Goals and requirements |
| [docs/SPEC.md](docs/SPEC.md) | Architecture, archive layout, CLI |
| [docs/RESTORE.md](docs/RESTORE.md) | Windows 10 restore guide |

## Quick start

Requires [uv](https://docs.astral.sh/uv/), Python 3.12+, and [Rust](https://rustup.rs/) (for fast scanning).

```powershell
# Windows — from repo root
.\scripts\bootstrap.ps1
.\wpa.cmd scan -o E:\migration_preview
.\wpa.cmd archive -o E:\migration.zip
.\wpa.cmd verify -o E:\migration.zip
.\wpa.cmd restore -o E:\migration.zip --user-map olduser:newuser -y
```

See [docs/RESTORE.md](docs/RESTORE.md) for full restore steps.

```bash
# Linux/macOS — tests use fixture tree (Python walker fallback)
uv sync --group dev
cargo test
uv run pytest
```

## CLI

| Command | Description |
|---------|-------------|
| `wpa scan` | Dry-run inventory + manifest (no file copy) |
| `wpa archive` | Full-drive scan → single ZIP (or folder) |
| `wpa verify` | Check archive against manifest |
| `wpa restore` | Copy files back to Windows user paths |

Scan uses the Rust `wpa-scan` binary when built (`target/release/wpa-scan.exe`); falls back to Python on Linux CI.

## Engineering standards

- **uv** + **ruff** + **pyright** strict + **pytest**
- **Rust** (`crates/wpa_scan`) for filesystem walk performance
- CI on every PR (Rust + Python)

## License

GPL-3.0-or-later — see [LICENSE](LICENSE).
