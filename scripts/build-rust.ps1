# Build the Rust wpa-scan binary (release).
# Run from repository root: .\scripts\build-rust.ps1

$ErrorActionPreference = "Stop"

if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
    Write-Error "cargo not found. Install Rust from https://rustup.rs/"
}

cargo build --release -p wpa-scan
Write-Host "Built: target\release\wpa-scan.exe"
