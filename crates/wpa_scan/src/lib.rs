//! Fast filesystem walker with prefix-based exclusions.

use std::fs;
use std::io::{self, Write};
use std::path::{Path, PathBuf};

use serde::Serialize;
use walkdir::WalkDir;

#[derive(Debug, Serialize)]
pub struct ScanEntry {
    pub path: String,
    pub size_bytes: u64,
    pub modified_secs: i64,
}

/// Returns true when `path` matches any exclusion prefix (case-insensitive on Windows).
pub fn is_excluded(path: &Path, exclusions: &[String]) -> bool {
    let path_str = path.to_string_lossy();
    let lower = path_str.to_lowercase();
    exclusions
        .iter()
        .any(|ex| lower.contains(&ex.to_lowercase()))
}

/// Walk `roots`, skipping excluded directories and emitting file entries.
pub fn walk_roots(roots: &[PathBuf], exclusions: &[String]) -> Vec<ScanEntry> {
    let mut entries = Vec::new();
    for root in roots {
        if !root.exists() {
            continue;
        }
        for result in WalkDir::new(root)
            .follow_links(false)
            .into_iter()
            .filter_entry(|e| !is_excluded(e.path(), exclusions))
        {
            let entry = match result {
                Ok(e) => e,
                Err(_) => continue,
            };
            if !entry.file_type().is_file() {
                continue;
            }
            let path = entry.path();
            let metadata = match fs::metadata(path) {
                Ok(m) => m,
                Err(_) => continue,
            };
            let modified_secs = metadata
                .modified()
                .ok()
                .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
                .map(|d| d.as_secs() as i64)
                .unwrap_or(0);
            entries.push(ScanEntry {
                path: path.to_string_lossy().to_string(),
                size_bytes: metadata.len(),
                modified_secs,
            });
        }
    }
    entries
}

/// Stream JSONL scan results to `writer`.
pub fn walk_roots_jsonl(
    roots: &[PathBuf],
    exclusions: &[String],
    writer: &mut impl Write,
) -> Result<u64, io::Error> {
    let mut count = 0u64;
    for root in roots {
        if !root.exists() {
            continue;
        }
        for result in WalkDir::new(root)
            .follow_links(false)
            .into_iter()
            .filter_entry(|e| !is_excluded(e.path(), exclusions))
        {
            let entry = match result {
                Ok(e) => e,
                Err(_) => continue,
            };
            if !entry.file_type().is_file() {
                continue;
            }
            let path = entry.path();
            let metadata = match fs::metadata(path) {
                Ok(m) => m,
                Err(_) => continue,
            };
            let modified_secs = metadata
                .modified()
                .ok()
                .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
                .map(|d| d.as_secs() as i64)
                .unwrap_or(0);
            let scan_entry = ScanEntry {
                path: path.to_string_lossy().to_string(),
                size_bytes: metadata.len(),
                modified_secs,
            };
            let line = serde_json::to_string(&scan_entry).map_err(|e| io::Error::other(e))?;
            writeln!(writer, "{line}")?;
            count += 1;
        }
    }
    Ok(count)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn excludes_windows_directory() {
        let tmp = TempDir::new().expect("tempdir");
        let root = tmp.path();
        let windows = root.join("Windows");
        fs::create_dir_all(windows.join("System32")).expect("mkdir");
        fs::write(windows.join("System32").join("kernel.dll"), b"x").expect("write");
        fs::create_dir_all(root.join("Users").join("alice")).expect("mkdir alice");
        fs::write(root.join("Users").join("alice").join("doc.txt"), b"hi").expect("write");

        let exclusions = vec![root.join("Windows").to_string_lossy().to_string()];
        let entries = walk_roots(&[root.to_path_buf()], &exclusions);
        assert_eq!(entries.len(), 1);
        assert!(entries[0].path.contains("doc.txt"));
    }
}
