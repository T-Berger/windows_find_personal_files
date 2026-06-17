# Publish master to GitHub: push, wait for CI, tag release, set topics.
# Prerequisites: gh auth login, git remote origin configured.
# Run from repo root: .\scripts\publish-github.ps1

$ErrorActionPreference = "Stop"

$Version = "v0.1.0"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

function Find-Gh {
    if (Get-Command gh -ErrorAction SilentlyContinue) { return (Get-Command gh).Source }
    $tempGh = Get-ChildItem -Path $env:TEMP -Recurse -Filter gh.exe -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($tempGh) { return $tempGh.FullName }
    throw "GitHub CLI (gh) not found. Install: winget install GitHub.cli"
}

$gh = Find-Gh
& $gh auth status

Write-Host "Pushing master..."
& git push origin master

Write-Host "Waiting for CI on master..."
$runId = & $gh run list --branch master --workflow CI --limit 1 --json databaseId --jq ".[0].databaseId"
& $gh run watch $runId --exit-status

Write-Host "Creating tag and release $Version..."
& git tag -a $Version -m "Windows Personal Archive $Version" -f
& git push origin $Version -f

$releaseBody = @"
## Windows Personal Archive $Version

First public release.

- Scan, archive, verify, and restore personal files across Windows drives
- Rust fast walker (`wpa-scan`) with Python CLI (`wpa`)
- Structured archive layout with manifest for audit and restore
- GPL-3.0-or-later

See [README](https://github.com/T-Berger/windows_find_personal_files/blob/master/README.md) for quick start.
"@

& $gh release create $Version --title "Windows Personal Archive $Version" --notes $releaseBody

Write-Host "Setting repository topics and description..."
& $gh repo edit `
    --description "CLI to find and archive personal files on Windows for PC migration (scan, archive, verify, restore)" `
    --add-topic windows `
    --add-topic backup `
    --add-topic migration `
    --add-topic python `
    --add-topic rust

Write-Host "Done. Release: https://github.com/T-Berger/windows_find_personal_files/releases/tag/$Version"
