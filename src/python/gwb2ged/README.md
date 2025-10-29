# gwb2ged - GeneWeb Database to GEDCOM Converter

## Overview

`gwb2ged` converts a GeneWeb database (`.gwb` or `.msgpack` format) to a GEDCOM file.

This module provides a complete Python implementation with full feature parity with the OCaml version.

## Installation

The module is part of the GeneWeb Python project. Make sure you have the dependencies installed:

```bash
cd src/python
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
# Export database to stdout
python -m gwb2ged database-name

# Export to file
python -m gwb2ged database-name -o output.ged

# With options
python -m gwb2ged database-name -o output.ged -charset UTF-8 -indexes -nn
```

### Command-Line Options

All options from the OCaml version are supported:

**Output Options:**

- `-o FILE`: Output GEDCOM file (default: stdout)
- `-charset {ASCII|ANSEL|ANSI|UTF-8}`: Set charset (default: UTF-8)
- `-v, --verbose`: Verbose output

**Selection Options:**

- `-a N`: Maximum generation of the root's ascendants
- `-ad N`: Maximum generation of the root's ascendants descendants
- `-d N`: Maximum generation of the root's descendants
- `-key KEY`: Key reference of root person (can be used multiple times)
- `-s SN`: Select this surname (can be used multiple times)
- `-parentship`: Select individuals involved in parentship computation

**Content Filtering:**

- `-c NUM`: Censor persons born less than NUM years ago
- `-nn`: No (database) notes
- `-nnn`: No notes (implies -nn)
- `-nopicture`: Don't extract individual picture
- `-picture-path`: Extract pictures path
- `-source SRC`: Replace individuals and families sources

**Special Options:**

- `-indexes`: Export indexes in GEDCOM
- `-mem`: Save memory space (slower)

## Using Tests for Development

### Test-Driven Development Strategy

Existing OCaml tests serve as behavioral references (Golden Master):

1. OCaml Tests (reference): `tests/ocaml/` - Test the original OCaml binary
2. Python Tests: `tests/python/` - Test the Python implementation
3. Golden Master: `tests/golden_master.py` - Compare both versions

### Using Tests for Development

```bash
# 1. Run OCaml tests to generate reference
cd src/python/gwb2ged
make test-ocaml

# 2. Develop your Python implementation
# ... code in cli/, core/, exporters/ ...

# 3. Test your implementation
USE_PYTHON_GWB2GED=true make test-python

# 4. Compare with OCaml reference
make test-golden
```

### Test Structure

```
tests/
├── ocaml/              # Reference tests (OCaml binary)
│   ├── test_basic_export.py
│   ├── test_indexes_option.py
│   ├── test_charset_options.py
│   ├── test_notes_options.py
│   └── test_helper.py
├── python/             # Python tests (implementation)
│   └── test_basic_export_python.py
└── golden_master.py    # Python vs OCaml comparison
```

### Adapting an OCaml Test for Python

Tests can be automatically adapted via environment variable:

```python
# In your test
from ocaml.test_helper import detect_binary, run_gwb2ged

# Automatically detects OCaml or Python
cmd_base, binary_type = detect_binary()
# If USE_PYTHON_GWB2GED=true, uses Python
# Otherwise, uses OCaml

# Use the function
returncode, stdout, stderr = run_gwb2ged(
    cmd_base, database_name, output_file="output.ged"
)
```

## Proposed Architecture

```
gwb2ged/
├── __init__.py
├── __main__.py              # Entry point: python -m gwb2ged
├── cli/
│   └── main.py              # Command-line interface
├── core/
│   ├── exporter.py          # Main exporter
│   └── options.py           # Options management
└── exporters/               # Specific exporters
    ├── gedcom_exporter.py
    ├── header_exporter.py
    ├── individual_exporter.py
    ├── family_exporter.py
    └── note_exporter.py
```

## Data Flow

```
MessagePack DB (.msgpack)
    ↓
lib.db.io.msgpack.MessagePackReader
    ↓
lib.db.database.Base
    ↓
gwb2ged.core.exporter.Gwb2GedExporter
    ↓
gedcom.models.GedcomDatabase
    ↓
gedcom.exporter.GedcomExporter
    ↓
GEDCOM File (.ged)
```

## Options to Implement

Based on existing OCaml tests:

### Priority 1 (tests available)

- `-indexes`: Add indexes to IDs (@I1@, @I2@, etc.)
- `-charset <encoding>`: Handle encodings (UTF-8, ASCII, ANSEL, ANSI)
- `-nn`: Exclude database notes
- `-nnn`: Exclude all notes

### Priority 2 (to test)

- `-s <surname>`: Filter by surname
- `-c`: Censor certain information
- `-source`: Handle sources
- `-nopicture`: Exclude images
- `-o <file>`: Output file

## Quick Start

### 1. Basic Structure

```python
# gwb2ged/__main__.py
from .cli.main import main

if __name__ == "__main__":
    main()
```

### 2. Minimal CLI

```python
# gwb2ged/cli/main.py
import argparse

class Gwb2GedCLI:
    def create_parser(self):
        parser = argparse.ArgumentParser(prog="gwb2ged")
        parser.add_argument("database", help="Database name")
        parser.add_argument("-o", "--output", help="Output GEDCOM file")
        return parser

    def run(self):
        parser = self.create_parser()
        args = parser.parse_args()
        # TODO: Implement export
        return 0

def main():
    cli = Gwb2GedCLI()
    import sys
    sys.exit(cli.run())
```

### 3. Basic Exporter

```python
# gwb2ged/core/exporter.py
from lib.db.io.msgpack import MessagePackReader
from lib.db.database.base import Base
from gedcom.exporter import GedcomExporter

class Gwb2GedExporter:
    def export(self, db_path: str, output_path: str):
        # 1. Load database
        reader = MessagePackReader(db_path)
        data = reader.load_database(db_name)
        base = Base(data)

        # 2. Convert to GEDCOM
        gedcom_db = self._convert_to_gedcom(base)

        # 3. Export
        exporter = GedcomExporter()
        exporter.export_file(output_path, gedcom_db)
```
