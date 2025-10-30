# GeneWeb Python Binaries

This directory contains bash wrapper scripts for all Python modules in the GeneWeb project.

## Available Binaries

### `ged2gwb`

GEDCOM to GeneWeb converter - the main binary for converting GEDCOM files to MessagePack databases.

```bash
# Convert a GEDCOM file
./bin/ged2gwb input.ged --output database.msgpack

# Load a database
./bin/ged2gwb --load database.msgpack

# Show help
./bin/ged2gwb --help
```

### `gwb2ged`

GeneWeb Database to GEDCOM converter - converts MessagePack databases to GEDCOM files.

```bash
# Export database to stdout
./bin/gwb2ged database-name

# Export to file
./bin/gwb2ged database-name -o output.ged

# With options
./bin/gwb2ged database-name -o output.ged -charset UTF-8 -indexes -nn

# Show help
./bin/gwb2ged --help
```

### `gedcom`

GEDCOM parser and utilities - for parsing and validating GEDCOM files.

```bash
# Parse a GEDCOM file
./bin/gedcom input.ged

# Show help
./bin/gedcom --help
```

### `gwd`

GeneWeb Web Daemon - starts the GeneWeb web server for browsing MessagePack databases.

```bash
# Start server on default port (2317)
./bin/gwd

# Start server on custom port
./bin/gwd --port 8080

# Specify bases directory
./bin/gwd --bases-dir /path/to/bases

# Start with debug mode
./bin/gwd --debug

# Show help
./bin/gwd --help
```

### `geneweb-python`

Generic runner for any Python module in the project.

```bash
# Run any module
./bin/geneweb-python ged2gwb --help
./bin/geneweb-python gedcom --version
./bin/geneweb-python lib.db
```

## Database Format

The binaries now use **MessagePack** format for database storage, replacing the old Pickle format:

### MessagePack Benefits

- **Security**: Safer than Pickle format
- **Portability**: Cross-language compatibility
- **Performance**: Faster serialization/deserialization
- **Structure**: Modular directory layout similar to OCaml `.gwb`

### Database Structure

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

## Installation

### Automatic Installation

Run the installation script to add all binaries to your PATH:

```bash
cd src/python
./bin/install-binaries.sh
```

This will:

- Add the `bin` directory to your shell's PATH
- Create symlinks in `/usr/local/bin` (requires sudo)
- Test the installation

### Manual Installation

Add the bin directory to your PATH manually:

```bash
# Add to your shell config file (~/.bashrc, ~/.zshrc, etc.)
export PATH="/path/to/geneweb/src/python/bin:$PATH"
```

## Usage

After installation, you can use the binaries from anywhere:

```bash
# Convert GEDCOM to MessagePack
ged2gwb sample.ged --output sample.msgpack

# Load database
ged2gwb --load sample.msgpack

# Use other modules
gedcom --help
```

## Uninstallation

To remove the binaries from your system:

```bash
cd src/python
./bin/uninstall-binaries.sh
```

This will:

- Remove the bin directory from your shell's PATH
- Remove symlinks from `/usr/local/bin`
- Create backups of your shell config files

## Features

- **MessagePack Database Format**: Modern, secure, and portable database storage
- **Full GEDCOM Support**: Complete parsing with notes, sources, and multimedia
- **Automatic virtual environment activation**: Scripts automatically activate the project's virtual environment
- **Cross-platform compatibility**: Works on Linux, macOS, and Windows (with bash)
- **Error handling**: Graceful fallback to system Python if virtual environment is not found
- **Easy installation**: One-command setup for all binaries
- **Clean uninstallation**: Complete removal of all traces

## Migration from Pickle

If you have existing `.pkl` databases, you can migrate them to the new MessagePack format:

### Manual Migration

1. **Export from Pickle**: Use the old Python tools to export data
2. **Import to MessagePack**: Use the new `ged2gwb` binary to create MessagePack databases

### Benefits of Migration

- **Better Security**: MessagePack is safer than Pickle
- **Cross-platform**: Works with other languages and tools
- **Future-proof**: Active development and maintenance
- **Performance**: Faster I/O operations

## Troubleshooting

### Virtual Environment Not Found

If you see "Virtual environment not found" warnings, make sure to create the virtual environment first:

```bash
cd src/python
make venv
make install-dev
```

### Permission Denied

If you get permission denied errors, make sure the scripts are executable:

```bash
chmod +x bin/*
```

### Command Not Found

If commands are not found after installation, restart your terminal or run:

```bash
source ~/.bashrc  # or ~/.zshrc
```

## Development

These scripts are designed to work with the project's development workflow:

- They automatically set up the Python path
- They activate the virtual environment if available
- They pass all arguments to the underlying Python modules
- They maintain compatibility with the project's Makefile targets
