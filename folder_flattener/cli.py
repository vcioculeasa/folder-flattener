"""CLI interface for folder flattener using Click."""

import click
from pathlib import Path
from typing import List

from .core import flatten_copy


@click.group()
def main():
    """Folder Flattener - Flatten folder structures by copying files with path-encoded names."""
    pass


@main.command()
@click.argument("sources", nargs=-1, required=True, type=click.Path(exists=True, path_type=Path))
@click.option(
    "--dest",
    "-d",
    required=True,
    type=click.Path(path_type=Path),
    help="Destination directory for flattened files",
)
@click.option(
    "--sep", default="__", show_default=True, help="Separator to use for encoding path components"
)
def flatten(sources: List[Path], dest: Path, sep: str):
    """
    Flatten folder structures by copying files with path-encoded names.

    SOURCES: One or more source files or directories to flatten
    """
    try:
        flatten_copy(list(sources), dest, sep)
        click.echo(f"✓ Successfully flattened {len(sources)} source(s) to {dest}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
