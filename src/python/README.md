# GeneWeb Python Tools

Python tools for GeneWeb genealogy software, including GEDCOM parsing, database utilities, and conversion tools.

## 🚀 Quick Start

```bash
# Install in development mode
cd src/python
pip install -e .

# Run tests
make test

# Run all checks
make check
```

## 📦 Components

- **ged2gwb**: GEDCOM to GeneWeb converter (MessagePack format)
- **gedcom**: GEDCOM file parser with full note/source support
- **lib.db**: MessagePack database utilities for GeneWeb

## 🛠️ Development

### Prerequisites

- Python 3.8+
- pip
- make (optional, for using Makefile)

### Setup

```bash
# Clone repository
git clone https://github.com/geneweb/geneweb.git
cd geneweb/src/python

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development tools
make install-tools
```

### Available Commands

```bash
# Setup
make setup          # Complete development setup
make venv           # Create virtual environment
make install        # Install package
make install-tools  # Install dev tools

# Testing
make test           # Run all tests
make test-ged2gwb   # Run ged2gwb tests
make test-gedcom    # Run GEDCOM tests
make test-lib       # Run lib tests
make test-coverage  # Run with coverage

# Development
make format         # Format code with ruff
make lint           # Run linting (ruff + mypy)
make fix            # Auto-fix linting issues
make check          # Format + lint + test

# Utilities
make clean          # Clean temporary files
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test categories
make test-ged2gwb
make test-gedcom
make test-lib

# Run with coverage
make test-coverage
```

## 📋 CI/CD

### GitHub Actions Workflows

1. **geneweb-python.yml**: Full Integration Pipeline

   - Runs on master/dev branches
   - Full GeneWeb OCaml build + Python tests
   - Code quality checks (ruff, mypy)
   - Comprehensive testing with Makefile
   - Demo runs with sample GEDCOM files

2. **python-deploy.yml**: Deployment (optional)
   - Runs on tags `python-v*` (e.g., `python-v1.0.0`)
   - Builds Python package
   - Publishes to PyPI
   - Creates GitHub release

### Deployment

To deploy a new version:

```bash
# Create and push a tag
git tag python-v1.0.0
git push origin python-v1.0.0

# This will trigger the deployment workflow
```

## 🔧 Configuration

### pyproject.toml

The project uses `pyproject.toml` for configuration:

- **Build system**: setuptools
- **Code formatting**: ruff
- **Type checking**: mypy
- **Testing**: pytest
- **Coverage**: pytest-cov

### Makefile

The Makefile provides convenient commands for development:

- Uses virtual environment (`.venv/`)
- Consistent command interface
- Colorized output
- Error handling

## 🏗️ Database Architecture

The database uses **MessagePack** format with a modular directory structure similar to OCaml `.gwb`:

```
bases/
└── database_name.msgpack/
    ├── base                    # Main data file (MessagePack)
    ├── access                  # Access permissions
    ├── persons                 # Person index
    ├── families                # Family index
    ├── strings                 # String index
    ├── notes_d/                # Notes directory
    ├── wiznotes/               # Wizard notes directory
    └── metadata.json           # Database metadata
```

### Key Features

- **Modular**: Separate files for different data types
- **Indexed**: Fast search by name, date, relation
- **Compatible**: Similar to OCaml `.gwb` format
- **Secure**: MessagePack format (safer than Pickle)
- **Portable**: Cross-language compatibility

### Migration from Pickle

The new MessagePack format replaces the old Pickle format:

- **Before**: Single `.pkl` file with all data
- **After**: Directory structure with specialized files
- **Benefits**: Better security, performance, and maintainability

## 📚 Usage Examples

### GEDCOM to GeneWeb Conversion

```python
from ged2gwb import Ged2GwbConverter, ConversionOptions

# Convert GEDCOM file to MessagePack database
options = ConversionOptions(
    input_file='family.ged',
    output_file='output.msgpack'
)
converter = Ged2GwbConverter(options)
result = converter.convert()
print(f"Converted {result['individuals_count']} individuals and {result['families_count']} families")
```

### GEDCOM Parsing

```python
from gedcom import GedcomParser

# Parse GEDCOM file with full note/source support
parser = GedcomParser('family.ged')
individuals = parser.get_individuals()
families = parser.get_families()

# Access notes and sources
for individual in individuals:
    print(f"Notes: {individual.notes}")
    print(f"Sources: {individual.sources}")
```

### Database Operations

```python
from lib.db import MessagePackReader, MessagePackWriter
from lib.db.database.base_data import BaseData

# Create and save database
data = BaseData()
# ... add persons, families, etc.
writer = MessagePackWriter("bases")
db_path = writer.write_database(data, "my_database")

# Load database
reader = MessagePackReader("bases")
db = reader.load_database("my_database")
persons = db.persons
families = db.families
```
