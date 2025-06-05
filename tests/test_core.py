"""Tests for the core flattening functionality."""

import pytest
import tempfile
import shutil
from pathlib import Path

from folder_flattener.core import flatten_copy


class TestFlattenCopy:
    """Test cases for the flatten_copy function."""

    def setup_method(self):
        """Set up test directories and files."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.source_dir = self.temp_dir / "source"
        self.dest_dir = self.temp_dir / "destination"

        # Create test directory structure
        self.source_dir.mkdir(parents=True)
        self.dest_dir.mkdir(parents=True)

        # Create test files
        (self.source_dir / "root_file.txt").write_text("Root file content")

        subdir1 = self.source_dir / "subdir1"
        subdir1.mkdir()
        (subdir1 / "file1.txt").write_text("File 1 content")
        (subdir1 / "file2.txt").write_text("File 2 content")

        subdir2 = self.source_dir / "subdir1" / "nested"
        subdir2.mkdir()
        (subdir2 / "deep_file.txt").write_text("Deep file content")

        another_dir = self.source_dir / "another"
        another_dir.mkdir()
        (another_dir / "another_file.txt").write_text("Another file content")

    def teardown_method(self):
        """Clean up test directories."""
        shutil.rmtree(self.temp_dir)

    def test_flatten_directory(self):
        """Test flattening a directory structure."""
        flatten_copy([self.source_dir], self.dest_dir)

        # Check that files were flattened correctly
        expected_files = [
            "root_file.txt",
            "subdir1__file1.txt",
            "subdir1__file2.txt",
            "subdir1__nested__deep_file.txt",
            "another__another_file.txt",
        ]

        dest_files = [f.name for f in self.dest_dir.iterdir() if f.is_file()]
        assert set(dest_files) == set(expected_files)

        # Check file contents
        assert (self.dest_dir / "root_file.txt").read_text() == "Root file content"
        assert (self.dest_dir / "subdir1__file1.txt").read_text() == "File 1 content"
        assert (self.dest_dir / "subdir1__nested__deep_file.txt").read_text() == "Deep file content"

    def test_flatten_with_custom_separator(self):
        """Test flattening with a custom separator."""
        flatten_copy([self.source_dir], self.dest_dir, sep="--")

        expected_files = [
            "root_file.txt",
            "subdir1--file1.txt",
            "subdir1--file2.txt",
            "subdir1--nested--deep_file.txt",
            "another--another_file.txt",
        ]

        dest_files = [f.name for f in self.dest_dir.iterdir() if f.is_file()]
        assert set(dest_files) == set(expected_files)

    def test_flatten_single_file(self):
        """Test flattening a single file."""
        single_file = self.source_dir / "root_file.txt"
        flatten_copy([single_file], self.dest_dir)

        dest_files = [f.name for f in self.dest_dir.iterdir() if f.is_file()]
        assert dest_files == ["root_file.txt"]
        assert (self.dest_dir / "root_file.txt").read_text() == "Root file content"

    def test_flatten_multiple_sources(self):
        """Test flattening multiple source paths."""
        # Create another source directory
        source2 = self.temp_dir / "source2"
        source2.mkdir()
        (source2 / "file_from_source2.txt").write_text("Source 2 content")

        subdir = source2 / "sub"
        subdir.mkdir()
        (subdir / "nested_file.txt").write_text("Nested in source 2")

        flatten_copy([self.source_dir, source2], self.dest_dir)

        # Should have files from both sources
        dest_files = [f.name for f in self.dest_dir.iterdir() if f.is_file()]

        expected_from_source1 = [
            "root_file.txt",
            "subdir1__file1.txt",
            "subdir1__file2.txt",
            "subdir1__nested__deep_file.txt",
            "another__another_file.txt",
        ]
        expected_from_source2 = ["file_from_source2.txt", "sub__nested_file.txt"]

        expected_all = expected_from_source1 + expected_from_source2
        assert set(dest_files) == set(expected_all)

    def test_name_conflict_resolution(self):
        """Test handling of filename conflicts."""
        # Create files that would have the same flattened name
        (self.source_dir / "conflict.txt").write_text("Original")

        subdir = self.source_dir / "conflict.txt"  # This will cause a conflict
        # Can't create dir with same name as file, so create different structure
        conflict_dir = self.source_dir / "some_dir"
        conflict_dir.mkdir()
        (conflict_dir / "conflict.txt").write_text("From subdir")

        flatten_copy([self.source_dir], self.dest_dir)

        dest_files = sorted([f.name for f in self.dest_dir.iterdir() if f.is_file()])

        # Should have both files with conflict resolution
        assert "conflict.txt" in dest_files
        assert any("conflict" in name and name != "conflict.txt" for name in dest_files)

    def test_empty_sources_raises_error(self):
        """Test that empty sources list raises ValueError."""
        with pytest.raises(ValueError, match="No source paths provided"):
            flatten_copy([], self.dest_dir)

    def test_nonexistent_source_warning(self, capsys):
        """Test that nonexistent sources produce warnings but don't crash."""
        nonexistent = self.temp_dir / "does_not_exist"
        flatten_copy([nonexistent], self.dest_dir)

        captured = capsys.readouterr()
        assert "does not exist" in captured.out

        # Destination should still be created even if no files copied
        assert self.dest_dir.exists()

    def test_destination_created_if_not_exists(self):
        """Test that destination directory is created if it doesn't exist."""
        new_dest = self.temp_dir / "new_destination"
        assert not new_dest.exists()

        flatten_copy([self.source_dir], new_dest)

        assert new_dest.exists()
        assert new_dest.is_dir()

        # Should have flattened files
        dest_files = [f.name for f in new_dest.iterdir() if f.is_file()]
        assert len(dest_files) > 0
