# GeneWeb Python - Modern Implementation

**Python implementation of GeneWeb Web Daemon (gwd) with Clean Architecture**

## 📋 About

This is a modern Python rewrite of the GeneWeb Web Daemon, originally written in OCaml. The goal is to produce **identical behavior** while using modern Python patterns and architecture.

### Key Principles

- ✅ **Result-focused**: Same output as OCaml version (validated by 44 automated tests)
- ✅ **Clean Architecture**: Domain → Use Cases → Adapters
- ✅ **Type Safety**: Full type hints with mypy
- ✅ **Testable**: Dependency injection throughout
- ✅ **Modern Python**: async/await, Pydantic, FastAPI

## 🚀 Quick Start

### Installation

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Run the server

```bash
# Basic usage
gwd -p 2317 -bd ../distribution/bases -hd ../distribution/gw

# With options
gwd -p 8080 -bd /path/to/bases -hd /path/to/html -debug
```

### Test with existing tests

```bash
# The 44 existing tests validate compatibility with OCaml version
cd ..
./test/run_all_tests.sh
```

## 🏗️ Architecture

```
geneweb-python/
├── src/geneweb/
│   ├── domain/          # Business entities (Person, Family, etc.)
│   ├── use_cases/       # Business logic (GetPerson, Search, etc.)
│   ├── adapters/        # External interfaces
│   │   ├── web/         # FastAPI routes
│   │   ├── database/    # GeneWeb database reader
│   │   └── config/      # Settings
│   ├── infrastructure/  # Technical services
│   │   ├── server/      # FastAPI server
│   │   └── auth/        # Authentication
│   └── cli/             # Command-line interface
└── tests/               # Tests (reusing ../test/)
```

## 📝 Command-Line Options

All original `gwd` options are supported:

### Basic Options
- `-p <PORT>` : Server port (default: 2317)
- `-bd <DIR>` : Bases directory
- `-hd <DIR>` : HTML/templates directory

### Network Options
- `-a <ADDRESS>` : Bind to specific address
- `-only <ADDRESS>` : Only accept from address
- `-no_host_address` : Disable reverse DNS

### Authentication
- `-auth <FILE>` : Authorization file
- `-friend <PASSWD>` : Friend password
- `-wizard <PASSWD>` : Wizard password
- `-digest` : Use Digest auth
- `-wjf` : Wizard just friend

### See all options
```bash
gwd --help
```

## 🧪 Development

### Run tests

```bash
# Run unit tests
pytest

# Run with coverage
pytest --cov=geneweb --cov-report=html

# Run integration tests (from parent dir)
cd .. && ./test/run_all_tests.sh
```

### Code quality

```bash
# Format code
black src/

# Lint code
ruff src/

# Type check
mypy src/
```

## 📊 Progress

### Phase 0: Setup ✅ (Current)
- [x] Project structure
- [x] FastAPI application
- [x] CLI with all options
- [x] Configuration management

### Phase 1: HTTP Server (Next)
- [ ] Proper routing
- [ ] Error handling
- [ ] Middleware (auth, logging)

### Phase 2: Database Reading
- [ ] Read GeneWeb binary format
- [ ] Person entities
- [ ] Family entities

### Phase 3: Templates & Rendering
- [ ] HTML templates (Jinja2)
- [ ] Match golden masters

### Phase 4: Authentication
- [ ] Basic auth
- [ ] Digest auth

### Phase 5: Advanced Features
- [ ] Trees, search, stats
- [ ] All 44 tests passing

## 🎯 Validation

Success is measured by the **44 existing automated tests**:

| Test Type | Count | Status |
|-----------|-------|--------|
| Golden Master | 25 | ⏳ Pending |
| Integration | 19 | ⏳ Pending |
| **Total** | **44** | **0/44** |

## 🤝 Comparison with OCaml

| Aspect | OCaml | Python |
|--------|-------|--------|
| Lines of code | ~2500 | ~1500 (estimated) |
| Architecture | Monolithic | Clean/Hexagonal |
| Testability | Difficult | Easy (DI) |
| Deployment | Complex | Simple (pip) |

## 📚 Documentation

- [Architecture Analysis](../ARCHITECTURE_ANALYSIS.md)
- [Rewrite Strategy](../REWRITE_STRATEGY.md)
- [Test Coverage](../test/TEST_COVERAGE_SUMMARY.md)

## 🔧 Tech Stack

- **FastAPI** - Modern async web framework
- **Pydantic** - Data validation and settings
- **uvicorn** - ASGI server
- **Jinja2** - Template engine
- **structlog** - Structured logging
- **pytest** - Testing framework

## 📄 License

Same as original GeneWeb project.

---

**Status**: Phase 0 - Infrastructure ✅  
**Next**: Implement HTTP routing and basic responses
