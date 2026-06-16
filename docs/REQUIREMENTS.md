# Requirements — Windows Personal File Archive

**Project:** `windows_find_personal_files`  
**Version:** 0.1.0 (draft)  
**Status:** Requirements baseline — implementation not started  
**Goal:** Migrate away from Microsoft Windows by archiving all personal data from a PC into a portable archive with a sensible folder structure, so it can be restored on another Windows 10 machine without personal data loss.

---

## 1. Problem Statement

When leaving a Windows PC (upgrade, replacement, or migration to another OS), users risk losing personal files scattered across:

- User profile folders (`Documents`, `Pictures`, `Desktop`, etc.)
- Application data (`AppData`)
- Files stored outside standard profile paths (e.g. `D:\Projects`, downloads on secondary drives)
- Browser profiles, email client data, SSH keys, game saves, and similar artifacts

Manual copy-paste is error-prone. This project provides an **open-source, repeatable, auditable** tool to discover, catalog, and archive personal data with a structure that supports restoration on a fresh Windows 10 install.

---

## 2. Stakeholders & Users

| Role | Need |
|------|------|
| **End user (migrating PC)** | One-command (or guided) archive of personal data to external media |
| **Contributor / maintainer** | Clear spec, tests, CI, typed Python code |
| **Future self (restore)** | Predictable archive layout and manifest for selective or full restore |

---

## 3. Goals (Must Have)

| ID | Requirement | Priority |
|----|-------------|----------|
| G-01 | Scan **all local fixed drives** on the source PC for personal/user data | Must |
| G-02 | Copy discovered files into an archive with a **sensible, documented folder structure** | Must |
| G-03 | Produce a **manifest** (inventory: path, size, hash optional, category) for audit and restore | Must |
| G-04 | Support restoration guidance (and eventually automation) on **Windows 10** target | Must |
| G-05 | **Exclude** OS binaries, vendor caches, and known non-personal paths by default (configurable) | Must |
| G-06 | Run as a **local CLI tool** on Windows (no cloud dependency) | Must |
| G-07 | Scripts and core logic under **version control**; suitable for **open source** release | Must |
| G-08 | Follow project **engineering boilerplate** (uv, ruff, pyright, pyproject.toml, CI) | Must |

---

## 4. Non-Goals (Out of Scope for v1)

| ID | Item | Notes |
|----|------|-------|
| NG-01 | Full disk image / bare-metal clone | Use dedicated imaging tools |
| NG-02 | Migrating installed applications (installers, registry for app licensing) | v1 focuses on **data**; app reinstall is manual |
| NG-03 | Cross-platform restore to Linux/macOS | Archive may be readable elsewhere, but restore UX targets Win10 |
| NG-04 | Real-time sync or continuous backup | One-shot or explicit re-run archive |
| NG-05 | Containerized execution as primary delivery | See §10 (boilerplate adaptations) |

---

## 5. Functional Requirements

### 5.1 Discovery & Classification

| ID | Requirement |
|----|-------------|
| F-01 | Enumerate all **fixed local drives** (e.g. `C:`, `D:`) via Windows APIs |
| F-02 | Apply a **default exclusion set**: `Windows\`, `Program Files`, `Program Files (x86)`, `$Recycle.Bin`, `System Volume Information`, `WinSxS`, temp/cache patterns, pagefile, hibernation files |
| F-03 | Apply a **default inclusion set** for well-known personal locations (user profile trees, `AppData`, common document roots on all drives) |
| F-04 | Support **user-defined include/exclude** rules (glob or path prefixes) via config file |
| F-05 | Classify files into **categories** (documents, media, config, credentials-adjacent, unknown) for manifest and restore hints |
| F-06 | Detect **multiple user profiles** on the machine and include all non-system profiles (configurable) |

### 5.2 Copy & Archive

| ID | Requirement |
|----|-------------|
| F-07 | Write archive root layout documented in `SPEC.md` (§ Archive Layout) |
| F-08 | Preserve **relative path semantics** sufficient to restore to equivalent user paths on target |
| F-09 | Support archive formats: **ZIP** (default, portable) and optionally **tar** (for large archives / Unix tooling) |
| F-10 | Handle **long paths** (>260 chars) on Windows source |
| F-11 | **Skip or warn** on files that cannot be read (permissions, in-use); log all skips |
| F-12 | Optional **split archives** when output exceeds configurable size (e.g. 4 GB per part for FAT32 USB) |
| F-13 | **Dry-run mode**: list what would be copied without writing archive |
| F-14 | **Resume / incremental**: optional second run that only adds new/changed files (post-v1 nice-to-have; listed in backlog) |

### 5.3 Manifest & Reporting

| ID | Requirement |
|----|-------------|
| F-15 | Generate `manifest.json` (or JSONL) with: source path, archive path, size, modified time, category, status (copied/skipped/error) |
| F-16 | Generate human-readable **summary report** (counts, total bytes, errors, duration) |
| F-17 | Optional per-file **SHA-256** for integrity verification (configurable; may slow large media libraries) |

### 5.4 Restore (v1 = documented; v1.1 = scripted)

| ID | Requirement |
|----|-------------|
| F-18 | Document restore procedure for Windows 10 (extract + path mapping) |
| F-19 | Provide `restore` subcommand (backlog v1.1) reading manifest and copying back to target paths with user confirmation |

### 5.5 CLI & Configuration

| ID | Requirement |
|----|-------------|
| F-20 | CLI entry point: `wpa archive`, `wpa scan`, `wpa verify` (names per SPEC) |
| F-21 | Configuration via **environment variables** and optional `wpa.toml` / `wpa.yaml` |
| F-22 | **Verbose / quiet** logging; log file written to archive metadata folder |
| F-23 | Require explicit `--output` path; refuse to write to system directories without `--force` |

---

## 6. Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NF-01 | **Reliability** | No silent failures; errors logged with path and reason |
| NF-02 | **Performance** | Streaming copy; avoid loading entire files in memory |
| NF-03 | **Security** | Warn when archiving credentials; optional encryption backlog |
| NF-04 | **Privacy** | No network calls; no telemetry by default |
| NF-05 | **Maintainability** | 100% type hints; ruff + pyright strict in CI |
| NF-06 | **Testability** | Unit tests for rules, path logic, manifest; integration tests with fixture trees |
| NF-07 | **Portability** | Python 3.12+; runs on Windows 10/11 source PCs |

---

## 7. Assumptions

1. User has **administrator rights** or sufficient ACLs to read their own profile and chosen paths.
2. **Destination** is external USB, network share, or second internal drive with enough free space.
3. Target machine is **Windows 10** (64-bit) for restore UX.
4. User accepts that some **in-use** files (browser DBs, Outlook) may need a second run after closing apps.
5. Open-source license will be **MIT** unless stakeholder chooses otherwise (see open questions).

---

## 8. Success Criteria

- [ ] Dry-run on a typical home PC produces a manifest with expected folders (Documents, Pictures, AppData subsets, etc.).
- [ ] Full archive restores sample files to correct relative locations on a Win10 VM.
- [ ] CI passes: format, lint, typecheck, tests.
- [ ] README enables a contributor to clone, `uv sync`, and run tests without Windows (Linux CI uses fixtures; Windows job for integration).

---

## 9. Backlog (Post-v1)

| Item | Description |
|------|-------------|
| B-01 | Incremental / resume archive |
| B-02 | `restore` subcommand with interactive path mapping |
| B-03 | Optional AES archive encryption |
| B-04 | Export list of installed programs (winget/winget export) as metadata only |
| B-05 | Rust core for scan performance (optional hybrid) |

---

## 10. Boilerplate Adaptations

This project is a **local Windows CLI utility**, not a networked SaaS. The following boilerplate sections are **adapted or deferred**:

| Boilerplate section | Adaptation |
|---------------------|------------|
| Docker as primary deployment | **Deferred** — full-drive access on Windows is impractical in default containers; optional devcontainer for non-Windows contributors only |
| IaC / multi-tenant SaaS | **Not applicable** |
| Agentic / LLM patterns | **Not applicable** |
| CI | **Required** — GitHub Actions: lint, typecheck, tests on Ubuntu; optional `windows-latest` job |

All other applicable standards apply: `uv`, `ruff`, `pyright` strict, `pyproject.toml`, feature branches, atomic commits, TDD for business logic.

---

## 11. Open Questions (Stakeholder Input Needed)

Please confirm or adjust:

1. **Definition of "personal"** — Default = user profiles + AppData + non-system paths on all drives with exclusion list. Should we also include **entire drive scan** minus exclusions (broader), or **profile-only** (narrower)?
2. **Archive format** — ZIP default OK? Need 7z for better compression?
3. **Encryption** — Required for v1, or plaintext on encrypted USB is enough?
4. **License** — MIT (permissive) vs GPL (copyleft)?
5. **Language** — Python-only for v1 (recommended for OSS contributors), or Rust core from start?
6. **Browser/email** — Explicit modules for Chrome/Firefox/Thunderbird/Outlook paths, or generic AppData scan only?
7. **Multiple users** — Archive all local user profiles on the PC, or only the running user?
8. **Restore scope for v1** — Documentation only, or implement `restore` in first release?

---

## 12. Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1.0 | 2026-06-16 | Initial draft | Baseline requirements from stakeholder goal |
