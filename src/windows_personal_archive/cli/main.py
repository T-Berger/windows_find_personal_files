"""Typer CLI — scan, archive, verify (stubs until implementation)."""

import typer

from windows_personal_archive import __version__

app = typer.Typer(
    name="wpa",
    help="Windows Personal Archive — migrate personal files off a Windows PC.",
    no_args_is_help=True,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"wpa {__version__}")
        raise typer.Exit()


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
    output: str = typer.Option(..., "--output", "-o", help="Archive output directory."),
    dry_run: bool = typer.Option(True, "--dry-run/--no-dry-run", help="Inventory only."),
) -> None:
    """Enumerate personal files and write manifest (dry-run by default)."""
    typer.echo(f"scan: not implemented yet (output={output}, dry_run={dry_run})")
    raise typer.Exit(code=1)


@app.command()
def archive(
    output: str = typer.Option(..., "--output", "-o", help="Archive output directory."),
) -> None:
    """Scan and copy personal files into archive layout."""
    typer.echo(f"archive: not implemented yet (output={output})")
    raise typer.Exit(code=1)


@app.command()
def verify(
    output: str = typer.Option(..., "--output", "-o", help="Archive directory to verify."),
) -> None:
    """Verify archive against manifest."""
    typer.echo(f"verify: not implemented yet (output={output})")
    raise typer.Exit(code=1)


def main() -> None:
    app()
