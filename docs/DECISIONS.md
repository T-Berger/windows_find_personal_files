# Stakeholder Decisions (Locked)

**Date:** 2026-06-16  
**Status:** Approved — drives implementation for v1.

| Topic | Decision |
|-------|----------|
| Scan scope | **Entire drive** on all fixed local drives, minus default exclusion list |
| Archive format | **Single ZIP file** (one archive, not split) |
| Encryption | **None** in v1 |
| License | **GPL-3.0-or-later** |
| Languages | **Python** (CLI, orchestration, restore) + **Rust** (performance-critical filesystem walk) |
| Browsers / email | **Explicit** known-app paths (Chrome, Firefox, Thunderbird, Outlook) **plus** full AppData scan |
| User profiles | **All** local user profiles |
| Restore | **Implement `wpa restore` in v1** (not documentation-only) |

## Implementation notes

- Full-drive scan roots each fixed drive at its volume root (e.g. `C:\`, `D:\`).
- Known-app paths improve **classification** and manifest tags; they do not replace AppData scanning.
- Rust binary `wpa-scan` is invoked by Python when available; Python `walkdir` fallback for CI on Linux.
