# Restore Guide — Windows 10

## Automated restore (`wpa restore`)

```powershell
# Preview what would be restored
uv run wpa restore -o E:\migration.zip --dry-run

# Restore with username mapping (source PC user → target PC user)
uv run wpa restore -o E:\migration.zip --user-map olduser:newuser --yes

# Custom target drive
uv run wpa restore -o E:\migration.zip --target-drive D: --yes
```

Manifest and metadata for ZIP archives live beside the archive: `migration_meta/META/`.

## Manual restore (if needed)

1. Extract `migration.zip` or use the folder archive directly.
2. Review `META/summary.txt` and `META/manifest.json`.
3. Copy `USERS/<user>/PROFILE/*` → `C:\Users\<user>\`
4. Copy `USERS/<user>/APPDATA/*` → `C:\Users\<user>\AppData\`
5. Copy `DRIVE_ROOTS/<drive>_/*` → corresponding drive letter.
6. Reinstall browsers, Office, Thunderbird, etc. — data files often activate after app install.

## Notes

- Close browsers and Outlook before archiving for best results; re-run archive if files were in use.
- Archives contain sensitive data — store on trusted media only (no encryption in v1).
