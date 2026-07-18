"""CLI entry point — wires ``engine render`` and ``engine refresh``.

Thin command layer: it resolves paths and prints clear success/error lines, then
delegates to :func:`engine.render_workbook` and :func:`engine.refresh_workbook`.
"""

from __future__ import annotations

from pathlib import Path

import click

from engine import refresh_workbook, render_workbook

DEFAULT_OUTPUT = "build/wrangler.xlsx"


@click.group()
def main() -> None:
    """Wrangler decision-engine report builder."""


@main.command()
@click.option(
    "--output",
    "-o",
    "output",
    default=DEFAULT_OUTPUT,
    show_default=True,
    type=click.Path(dir_okay=False, path_type=Path),
    help="Where to write the rendered .xlsx.",
)
def render(output: Path) -> None:
    """Render a fresh report workbook from scratch."""
    written = render_workbook(output)
    click.echo(f"Rendered report -> {written}")


@main.command()
@click.argument(
    "path",
    default=DEFAULT_OUTPUT,
    type=click.Path(dir_okay=False, path_type=Path),
)
def refresh(path: Path) -> None:
    """Rewrite the Data_* tabs of an existing report from fresh source data."""
    try:
        written = refresh_workbook(path)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Refreshed data tabs -> {written}")


if __name__ == "__main__":
    main()
