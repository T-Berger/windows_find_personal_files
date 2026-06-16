"""Typer CLI — scan, archive, verify, restore."""

import os
from pathlib import Path

import typer
from rich.console import Console

from windows_personal_archive import __version__
from windows_personal_archive.archive.writer import create_archive_writer
from windows_personal_archive.config.loader import infer_output_format, load_config
from windows_personal_archive.config.models import ArchiveConfig, OutputFormat
from windows_personal_archive.restore.restorer import restore_archive
from windows_personal_archive.scan.planner import run_scan
from windows_personal_archive.verify.checksum import verify_archive

app = typer.Typer(
    name="wpa",
    help="Windows Personal Archive — migrate personal files off a Windows PC.",
    no_args_is_help=True,
)
console = Console()


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"wpa {__version__}")
        raise typer.Exit()


def _resolve_config(config: Path | None) -> ArchiveConfig:
    config_path = config or (
        Path(os.environ.get("WPA_CONFIG", "")) if os.environ.get("WPA_CONFIG") else None
    )
    if config_path and not config_path.is_file():
        raise typer.BadParameter(f"config not found: {config_path}")
    return load_config(config_path if config_path and config_path.is_file() else None)


def _parse_user_map(raw: str | None) -> dict[str, str]:
    if not raw:
        return {}
    mapping: dict[str, str] = {}
    for pair in raw.split(","):
        if ":" not in pair:
            continue
        source, target = pair.split(":", 1)
        mapping[source.strip()] = target.strip()
    return mapping


@app.callback()
def cli(
    version: bool = typer.Option(
        False,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """Windows Personal Archive CLI."""


@app.command()
def scan(
    output: Path = typer.Option(..., "--output", "-o", help="Output path (folder or .zip)."),
    config: Path | None = typer.Option(None, "--config", help="Optional wpa.toml path."),
    hash_files: bool = typer.Option(False, "--hash", help="Compute SHA-256 hashes."),
) -> None:
    """Enumerate files (dry-run) and write manifest without copying data."""
    archive_config = _resolve_config(config)
    if hash_files:
        archive_config = ArchiveConfig(
            output_format=archive_config.output_format,
            hash_files=True,
            scan=archive_config.scan,
            exclude_prefixes=archive_config.exclude_prefixes,
            include_rules=archive_config.include_rules,
            verbose=archive_config.verbose,
        )
    fmt = infer_output_format(output)
    if fmt == OutputFormat.ZIP and archive_config.output_format != OutputFormat.ZIP:
        archive_config = ArchiveConfig(
            output_format=OutputFormat.ZIP,
            hash_files=archive_config.hash_files,
            scan=archive_config.scan,
            exclude_prefixes=archive_config.exclude_prefixes,
            include_rules=archive_config.include_rules,
            verbose=archive_config.verbose,
        )

    result = run_scan(archive_config, output, copy_files=False)
    console.print(
        f"[green]Scan complete[/green]: {result.manifest.stats.files_planned} files planned"
    )
    console.print(f"Manifest: {result.meta_dir / 'manifest.json'}")


@app.command()
def archive(
    output: Path = typer.Option(..., "--output", "-o", help="Archive path (.zip or folder)."),
    config: Path | None = typer.Option(None, "--config", help="Optional wpa.toml path."),
    hash_files: bool = typer.Option(False, "--hash", help="Compute SHA-256 hashes."),
) -> None:
    """Scan and copy personal files into a single archive."""
    archive_config = _resolve_config(config)
    fmt = infer_output_format(output)
    archive_config = ArchiveConfig(
        output_format=fmt,
        hash_files=hash_files or archive_config.hash_files,
        scan=archive_config.scan,
        exclude_prefixes=archive_config.exclude_prefixes,
        include_rules=archive_config.include_rules,
        verbose=archive_config.verbose,
    )

    writer = create_archive_writer(output, archive_config.output_format.value)
    try:
        result = run_scan(archive_config, output, copy_files=True, archive_writer=writer)
    finally:
        writer.close()

    console.print(
        f"[green]Archive complete[/green]: {result.manifest.stats.files_copied} files, "
        f"{result.manifest.stats.bytes_copied} bytes"
    )
    if archive_config.output_format == OutputFormat.ZIP:
        console.print(f"Archive: {output}")
    console.print(f"Manifest: {result.meta_dir / 'manifest.json'}")


@app.command()
def verify(
    output: Path = typer.Option(..., "--output", "-o", help="Archive path to verify."),
) -> None:
    """Verify archive files against manifest."""
    ok, failed = verify_archive(output)
    if failed:
        console.print(f"[yellow]Verify[/yellow]: {ok} ok, {failed} failed")
        raise typer.Exit(code=2)
    console.print(f"[green]Verify OK[/green]: {ok} files")


@app.command()
def restore(
    output: Path = typer.Option(..., "--output", "-o", help="Archive path to restore from."),
    target_drive: str = typer.Option("C:", "--target-drive", help="Target drive letter."),
    user_map: str | None = typer.Option(
        None,
        "--user-map",
        help="Comma-separated source:target users (e.g. alice:bob).",
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show restore plan only."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
) -> None:
    """Restore archived files to target Windows user paths."""
    mapping = _parse_user_map(user_map)
    if not yes and not dry_run:
        typer.confirm(
            f"Restore from {output} to {target_drive}? This will overwrite existing files.",
            abort=True,
        )
    restored, errors = restore_archive(output, mapping, target_drive, dry_run=dry_run)
    if errors:
        console.print(f"[yellow]Restore[/yellow]: {restored} restored, {errors} errors")
        raise typer.Exit(code=2)
    label = "[green]Dry-run[/green]" if dry_run else "[green]Restore complete[/green]"
    console.print(f"{label}: {restored} files")


def main() -> None:
    app()
