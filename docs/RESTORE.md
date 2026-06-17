# Restore Guide — Windows 10

## Automated restore (`wpa restore`)

From the project folder on Windows:

```powershell
cd C:\Users\thoma\Documents\windows_find_personal_files

# Preview what would be restored
.\wpa.cmd restore -o migration_file.zip --dry-run

# Restore to same username
.\wpa.cmd restore -o migration_file.zip --yes

# Restore with username mapping (source PC user → target PC user)
.\wpa.cmd restore -o migration_file.zip --user-map thoma:newusername --yes

# Custom target drive
.\wpa.cmd restore -o migration_file.zip --target-drive D: --yes
```

Without `wpa.cmd`, use `uv run wpa restore ...` with the same flags.

Manifest and metadata for ZIP archives live beside the archive: `migration_file_meta/META/`.

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
