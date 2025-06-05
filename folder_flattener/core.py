"""Core functionality for flattening folder structures."""

import os
import shutil
from pathlib import Path
from typing import List

__all__ = ["flatten_copy"]


def flatten_copy(sources: List[Path], destination: Path, sep: str = "__") -> None:
    """
    Flatten folder structures by copying files with path-encoded names.

    Args:
        sources: List of source paths (files or directories) to flatten
        destination: Destination directory where flattened files will be copied
        sep: Separator to use for encoding path components (default: '__')

    Raises:
        OSError: If there are issues accessing or creating files/directories
        ValueError: If sources or destination are invalid
    """
    if not sources:
        raise ValueError("No source paths provided")

    # Ensure destination exists
    destination.mkdir(parents=True, exist_ok=True)

    for source in sources:
        source = Path(source)

        if not source.exists():
            print(f"Warning: Source path '{source}' does not exist, skipping...")
            continue

        if source.is_file():
            # Handle single file
            _copy_single_file(source, destination, source.parent, sep)
        elif source.is_dir():
            # Handle directory recursively
            _copy_directory(source, destination, sep)
        else:
            print(f"Warning: '{source}' is neither a file nor directory, skipping...")


def _copy_directory(src_root: Path, destination: Path, sep: str) -> None:
    """Copy all files from a directory recursively with flattened names."""
    for root, dirs, files in os.walk(src_root):
        root_path = Path(root)

        for filename in files:
            file_path = root_path / filename
            _copy_single_file(file_path, destination, src_root, sep)


def _copy_single_file(file_path: Path, destination: Path, src_root: Path, sep: str) -> None:
    """Copy a single file with a flattened name."""
    try:
        # Calculate relative path from source root
        rel_path = file_path.relative_to(src_root)

        # Build flat filename by joining path parts with separator
        if len(rel_path.parts) == 1:
            # File is in root directory, use original name
            flat_name = rel_path.name
        else:
            # Join directory parts and filename with separator
            flat_name = sep.join(rel_path.parts)

        # Ensure destination file path
        dest_file = destination / flat_name

        # Handle name conflicts by adding a counter
        counter = 1
        original_flat_name = flat_name
        while dest_file.exists():
            name_parts = original_flat_name.rsplit(".", 1)
            if len(name_parts) == 2:
                flat_name = f"{name_parts[0]}_{counter}.{name_parts[1]}"
            else:
                flat_name = f"{original_flat_name}_{counter}"
            dest_file = destination / flat_name
            counter += 1

        # Copy the file
        shutil.copy2(file_path, dest_file)
        print(f"Copied: {file_path} -> {dest_file}")

    except Exception as e:
        print(f"Error copying {file_path}: {e}")
