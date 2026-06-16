# Restore Guide — Windows 10 (Draft)

This document will describe how to restore personal data from a `wpa` archive onto a fresh Windows 10 machine.

## Planned Steps (v1 — manual)

1. Copy archive folder or extract ZIP to local disk on target PC.
2. Review `META/summary.txt` and `META/manifest.json` for completeness.
3. Create target user account if it does not match source username.
4. Copy contents of `USERS/<username>/PROFILE/*` to `C:\Users\<username>\` preserving subfolders.
5. Copy `USERS/<username>/APPDATA/*` into `C:\Users\<username>\AppData\`.
6. Copy `DRIVE_ROOTS/*` to corresponding drive letters (see path mapping in manifest).
7. Re-run any installers for applications (browsers, Office, etc.) — data files may activate after app install.

## Automated Restore

The `wpa restore` command is **backlog v1.1** — see `docs/REQUIREMENTS.md` §9.
