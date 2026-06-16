# Install uv (if missing) and sync project dependencies.
# Run from repository root: .\scripts\bootstrap.ps1

$ErrorActionPreference = "Stop"

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "Installing uv..."
    irm https://astral.sh/uv/install.ps1 | iex
}

uv python install 3.12
uv sync --group dev
if (Get-Command cargo -ErrorAction SilentlyContinue) {
    cargo build --release -p wpa-scan
}

Write-Host "Done. Try: uv run wpa --help"
