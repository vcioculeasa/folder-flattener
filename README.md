# Folder Flattener

A Python tool to flatten folder structures by copying files with path-encoded names. This tool provides both command-line and graphical interfaces for flattening nested directory structures into a single directory.

## Features

- **Flatten nested directories**: Copy all files from nested folders into a single destination directory
- **Path encoding**: Preserve directory structure information by encoding paths in filenames
- **Multiple interfaces**: Command-line tool and user-friendly GUI
- **Conflict resolution**: Automatically handle filename conflicts
- **Customizable separator**: Choose your own path separator (default: `__`)
- **Multiple sources**: Process multiple files and directories at once

## Installation

### From Source

```bash
git clone <repository-url>
cd folder-flattener
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Usage

### Command Line Interface

```bash
# Flatten a single directory
folder-flattener flatten /path/to/source --dest /path/to/destination

# Flatten multiple sources
folder-flattener flatten /path/to/source1 /path/to/source2 --dest /path/to/destination

# Use custom separator
folder-flattener flatten /path/to/source --dest /path/to/destination --sep "--"

# Get help
folder-flattener flatten --help
```

### Graphical User Interface

```bash
folder-flattener-gui
```

Or run directly:

```bash
python -m folder_flattener.gui
```

### Python API

```python
from folder_flattener import flatten_copy
from pathlib import Path

# Flatten directories
sources = [Path("source1"), Path("source2")]
destination = Path("flattened_output")
flatten_copy(sources, destination, sep="__")
```

## How It Works

The tool walks through all source directories recursively and copies files to the destination with flattened names:

**Original structure:**
```
source/
├── file1.txt
├── subdir1/
│   ├── file2.txt
│   └── nested/
│       └── file3.txt
└── subdir2/
    └── file4.txt
```

**Flattened result:**
```
destination/
├── file1.txt
├── subdir1__file2.txt
├── subdir1__nested__file3.txt
└── subdir2__file4.txt
```

## Features in Detail

### Conflict Resolution
If multiple files would result in the same flattened name, the tool automatically adds a counter suffix:
- `document.txt`
- `document_1.txt`
- `document_2.txt`

### Path Encoding
Directory paths are encoded into filenames using a configurable separator:
- Default separator: `__`
- Custom separator: `folder-flattener flatten source --dest destination --sep "--"`

### GUI Features
- **Browse Files/Folders**: Select individual files or entire directories
- **Multiple Sources**: Add multiple source locations
- **Progress Tracking**: Visual progress bar during flattening
- **Background Processing**: Non-blocking operation with threading


## Running Tests

```bash
pytest
```


## Requirements

- Python 3.12+
- click (for CLI)
- tkinter (for GUI, usually included with Python)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## Changelog

### v0.1.0
- Initial release
- Core flattening functionality
- CLI interface with Click
- GUI interface with Tkinter
- Comprehensive test suite
- Conflict resolution
- Multiple source support
