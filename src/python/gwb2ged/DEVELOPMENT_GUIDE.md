# Development Guide for Python gwb2ged

This guide explains how to use existing OCaml tests to reimplement `gwb2ged` in Python.

## Development Strategy

### 1. Test-Driven Development (TDD)

OCaml tests serve as behavioral references (Golden Master):

```
1. Run OCaml test with OCaml binary → Expected result
2. Implement Python feature
3. Run same test with Python binary → Verify equivalence
4. Iterate until perfect match
```

### 2. Test Structure

Tests in `tests/ocaml/`:

- `test_basic_export.py` - Basic export (minimal reference)
- `test_indexes_option.py` - `-indexes` option
- `test_charset_options.py` - `-charset` option
- `test_notes_options.py` - `-nn`, `-nnn` options

### 3. Adapting Tests for Python

**Option A: Automatic Binary Detection**

```python
import os
import subprocess

def get_binary(binary_name="gwb2ged"):
    """Get the appropriate binary (OCaml or Python)"""
    # Check for Python version first
    python_bin = f"python -m gwb2ged"
    ocaml_bin = f"distribution/gw/{binary_name}"

    # Try Python first, fallback to OCaml
    if subprocess.run(["python", "-m", "gwb2ged", "--help"],
                     capture_output=True).returncode == 0:
        return ["python", "-m", "gwb2ged"]
    elif os.path.exists(ocaml_bin):
        return [ocaml_bin]
    else:
        raise FileNotFoundError(f"{binary_name} not found")
```

**Option B: Environment Variable**

```python
import os

USE_PYTHON = os.getenv("USE_PYTHON_GWB2GED", "false").lower() == "true"

def get_binary():
    if USE_PYTHON:
        return ["python", "-m", "gwb2ged"]
    return ["distribution/gw/gwb2ged"]
```

## Python Architecture

### Proposed Structure

```
gwb2ged/
├── __init__.py
├── __main__.py                    # Entry point
├── cli/
│   └── main.py                    # Command-line interface
├── core/
│   ├── exporter.py                # Main exporter
│   └── options.py                 # Options management
├── exporters/
│   ├── gedcom_exporter.py         # GEDCOM export
│   ├── header_exporter.py         # HEAD export
│   ├── individual_exporter.py     # INDI export
│   ├── family_exporter.py         # FAM export
│   └── note_exporter.py           # NOTE export
└── tests/
    ├── ocaml/                     # OCaml tests (reference)
    └── python/                    # Python unit tests
```

### Data Flow

```
MessagePack DB → Base (lib.db) → Exporter → GEDCOM File
```

1. Load MessagePack database: Use `lib.db.io.msgpack.MessagePackReader`
2. Convert to GEDCOM: Use `gedcom.exporter.GedcomExporter` (existing)
3. Apply options: Filtering, charset, notes, etc.
4. Write file: Final GEDCOM file write

## Step-by-Step Implementation

### Step 1: Basic Structure and CLI

```python
# gwb2ged/__main__.py
from .cli.main import main

if __name__ == "__main__":
    main()
```

```python
# gwb2ged/cli/main.py
import argparse
from pathlib import Path

class Gwb2GedCLI:
    def create_parser(self):
        parser = argparse.ArgumentParser(prog="gwb2ged")
        parser.add_argument("database", help="Database name or path")
        parser.add_argument("-o", "--output", help="Output GEDCOM file")
        parser.add_argument("-charset", choices=["UTF-8", "ASCII", "ANSEL", "ANSI"])
        parser.add_argument("-indexes", action="store_true")
        parser.add_argument("-nn", action="store_true", help="No database notes")
        parser.add_argument("-nnn", action="store_true", help="No notes at all")
        # ... other options
        return parser

    def run(self):
        parser = self.create_parser()
        args = parser.parse_args()
        # Implement export
        return 0
```

### Step 2: Basic Export

```python
# gwb2ged/core/exporter.py
from lib.db.io.msgpack import MessagePackReader
from lib.db.database.base import Base
from gedcom.exporter import GedcomExporter

class Gwb2GedExporter:
    def __init__(self, options):
        self.options = options

    def export(self, db_path: str, output_path: str):
        # 1. Load MessagePack database
        reader = MessagePackReader(db_path)
        data = reader.load_database(db_name)
        base = Base(data)

        # 2. Convert Base → GedcomDatabase
        gedcom_db = self._convert_base_to_gedcom(base)

        # 3. Apply options
        gedcom_db = self._apply_options(gedcom_db)

        # 4. Export to GEDCOM
        exporter = GedcomExporter()
        exporter.export_file(Path(output_path), gedcom_db)

    def _convert_base_to_gedcom(self, base):
        # Use gedcom.models to create GEDCOM structure
        pass

    def _apply_options(self, gedcom_db):
        # Filter notes, adjust charset, etc.
        pass
```

### Step 3: Comparative Tests

Modify `test_basic_export.py` to test both versions:

```python
def test_basic_export():
    # Create test database
    create_test_database()

    # Test OCaml (reference)
    ocaml_result = export_with_ocaml()

    # Test Python (new implementation)
    python_result = export_with_python()

    # Compare results
    assert compare_gedcom_files(ocaml_result, python_result)
```

## Using Existing Tests

### 1. Run OCaml Tests (Reference)

```bash
cd src/python/gwb2ged
make test-ocaml
```

This runs all tests with the OCaml binary and generates reference results.

### 2. Adapt Tests for Python

Copy tests to `tests/python/` and modify to test Python version:

```python
# tests/python/test_basic_export.py
def test_basic_export_python():
    """Test Python implementation"""
    from gwb2ged.core.exporter import Gwb2GedExporter

    # Use the same test database
    exporter = Gwb2GedExporter(options)
    exporter.export(db_path, output_path)

    # Verify result
    assert is_valid_gedcom(output_path)
```

### 3. Golden Master Comparison Tests

Create tests that directly compare outputs:

```python
def test_golden_master():
    """Compare Python output with OCaml output"""
    ocaml_ged = export_with_ocaml()
    python_ged = export_with_python()

    # Normalize both files (dates, IDs, etc.)
    ocaml_normalized = normalize_gedcom(ocaml_ged)
    python_normalized = normalize_gedcom(python_ged)

    # Compare line by line (with tolerance)
    assert compare_with_tolerance(ocaml_normalized, python_normalized)
```

## Options to Implement

Based on tests, here are priority options:

### Priority 1 (already tested)

- `-indexes` - Add indexes to IDs
- `-charset` - Handle encodings (UTF-8, ASCII, ANSEL, ANSI)
- `-nn` - Exclude base notes
- `-nnn` - Exclude all notes

### Priority 2 (to test)

- `-s <string>` - Filter by name
- `-c` - Censor certain information
- `-key` - Generate a key
- `-mem` - Memory mode
- `-source` - Source management
- `-nopicture` - Exclude images

## Important Considerations

### 1. OCaml Compatibility

- IDs: OCaml IDs start at 1, Python at 0 (adjust)
- Dates: GEDCOM date format (OCaml vs Python parser)
- Charset: Special character encoding
- Notes: Format and indentation level

### 2. Performance

- Loading large databases
- Exporting large GEDCOM files
- Memory: databases with thousands of persons

### 3. Regression Tests

- Create test suite with real databases
- Compare with GEDCOM diff tools
- Validate with external GEDCOM validators

## Useful Commands

```bash
# Run all OCaml tests (reference)
cd src/python/gwb2ged && make test-ocaml

# Run Python tests (new implementation)
cd src/python/gwb2ged && python -m pytest tests/python/

# Compare two exports
python tools/compare_gedcom.py ocaml_output.ged python_output.ged

# Validate a GEDCOM file
python -m gedcom.validate output.ged
```
