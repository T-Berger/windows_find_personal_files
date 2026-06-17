@echo off
REM Launcher: run wpa from repo root without activating .venv
setlocal
cd /d "%~dp0"
uv run wpa %*
