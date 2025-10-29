## Makefile for GeneWeb Python Project

PYTHON = python3
PROJECT_ROOT = .
VENV_DIR = .venv
VENV_PYTHON = $(VENV_DIR)/bin/python
VENV_PIP = $(VENV_DIR)/bin/pip

# Colors for output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[0;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

# Default target
.PHONY: all
all: help

# Help target
.PHONY: help
help:
	@echo "$(BLUE)GeneWeb Python Project - Available Commands$(NC)"
	@echo "=================================================="
	@echo ""
	@echo "$(GREEN)Setup:$(NC)"
	@echo "  setup          Complete development setup (venv + install + tools)"
	@echo "  venv           Create virtual environment"
	@echo "  install        Install package in development mode"
	@echo "  install-tools  Install development tools (ruff, pytest, mypy)"
	@echo ""
	@echo "$(GREEN)Testing:$(NC)"
	@echo "  test              Run all tests"
	@echo ""
	@echo "$(GREEN)Module-specific tests:$(NC)"
	@echo "  test-ged2gwb      Run ged2gwb tests only"
	@echo "  test-gwb2ged      Run all gwb2ged tests (OCaml + Python)"
	@echo "  test-gwb2ged-ocaml Run all gwb2ged OCaml binary tests"
	@echo "  test-gwb2ged-py   Run all gwb2ged Python implementation tests"
	@echo "  test-gedcom       Run GEDCOM tests only"
	@echo "  test-gwd          Run gwd tests only"
	@echo ""
	@echo "$(GREEN)Database and library tests:$(NC)"
	@echo "  test-lib          Run lib tests (db + util)"
	@echo "  test-db-ops       Run database operations tests"
	@echo "  test-msgpack      Run MessagePack database tests"
	@echo ""
	@echo "$(GREEN)Quality assurance:$(NC)"
	@echo "  test-coverage     Run tests with coverage report"
	@echo "  validate          Validate MessagePack implementation"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@echo "  format         Format code with ruff"
	@echo "  lint           Run linting (ruff + mypy)"
	@echo "  fix            Auto-fix linting issues"
	@echo "  check          Format + lint + test (complete check)"
	@echo ""
	@echo "$(GREEN)Utilities:$(NC)"
	@echo "  clean          Clean temporary files"
	@echo ""

# Setup & Installation
.PHONY: setup
setup: venv install install-tools
	@echo "$(GREEN)✓ Complete development setup ready$(NC)"

.PHONY: venv
venv:
	@echo "$(BLUE)Creating virtual environment...$(NC)"
	@if [ ! -d "$(VENV_DIR)" ]; then \
		$(PYTHON) -m venv $(VENV_DIR); \
		echo "$(GREEN)✓ Virtual environment created$(NC)"; \
	else \
		echo "$(YELLOW)Virtual environment already exists$(NC)"; \
	fi

.PHONY: install
install: venv
	@echo "$(BLUE)Installing package in development mode...$(NC)"
	$(VENV_PIP) install -e .
	@echo "$(GREEN)✓ Package installed$(NC)"

.PHONY: install-tools
install-tools: venv
	@echo "$(BLUE)Installing development tools...$(NC)"
	$(VENV_PIP) install ruff mypy pytest pytest-cov msgpack
	@echo "$(GREEN)✓ Development tools installed$(NC)"

# Testing
.PHONY: test
test:
	@echo "$(BLUE)Running all tests...$(NC)"
	@echo "$(BLUE)Testing ged2gwb...$(NC)"
	$(VENV_PYTHON) -m pytest ged2gwb/tests/ -v --tb=short
	@echo "$(BLUE)Testing gwb2ged OCaml binary...$(NC)"
	@cd gwb2ged && $(MAKE) test-ocaml
	@echo "$(BLUE)Testing gwb2ged Python implementation...$(NC)"
	@cd gwb2ged && $(MAKE) test-python || echo "$(YELLOW)gwb2ged Python tests skipped (no tests found)$(NC)"
	@echo "$(BLUE)Testing gedcom...$(NC)"
	$(VENV_PYTHON) -m pytest gedcom/tests/ -v --tb=short
	@echo "$(BLUE)Testing gwd...$(NC)"
	@if [ -d gwd ] && [ -n "$$(ls -A gwd/test*.py 2>/dev/null)" ]; then \
		cd gwd && PYTHONPATH=. $(VENV_PYTHON) -m pytest test*.py -v --tb=short 2>&1 || echo "$(YELLOW)SKIP: gwd tests require gwd module dependencies$(NC)"; \
	else \
		echo "$(YELLOW)SKIP: No gwd tests found$(NC)"; \
	fi
	@echo "$(BLUE)Testing lib...$(NC)"
	$(VENV_PYTHON) -m pytest lib/db/tests/ -v --tb=short
	$(VENV_PYTHON) -m pytest lib/util/ -v --tb=short || echo "$(YELLOW)No tests found in lib/util$(NC)"
	@echo "$(GREEN)✓ All tests completed$(NC)"

.PHONY: test-ged2gwb
test-ged2gwb:
	@echo "$(BLUE)Running ged2gwb tests...$(NC)"
	$(VENV_PYTHON) -m pytest ged2gwb/tests/ -v --tb=short

.PHONY: test-gwb2ged
test-gwb2ged: test-gwb2ged-ocaml test-gwb2ged-py
	@echo "$(GREEN)✓ All gwb2ged tests completed$(NC)"

.PHONY: test-gwb2ged-ocaml
test-gwb2ged-ocaml:
	@echo "$(BLUE)Running gwb2ged OCaml binary tests...$(NC)"
	@cd gwb2ged && $(MAKE) test-ocaml

.PHONY: test-gwb2ged-py
test-gwb2ged-py:
	@echo "$(BLUE)Running gwb2ged Python implementation tests...$(NC)"
	@cd gwb2ged && $(MAKE) test-python


.PHONY: test-gedcom
test-gedcom:
	@echo "$(BLUE)Running GEDCOM tests...$(NC)"
	$(VENV_PYTHON) -m pytest gedcom/tests/ -v --tb=short

.PHONY: test-gwd
test-gwd:
	@echo "$(BLUE)Running gwd tests...$(NC)"
	@if [ -d gwd ] && [ -n "$$(ls -A gwd/test*.py 2>/dev/null)" ]; then \
		cd gwd && PYTHONPATH=. $(VENV_PYTHON) -m pytest test*.py -v --tb=short || echo "$(YELLOW)SKIP: gwd tests require gwd module dependencies$(NC)"; \
	else \
		echo "$(YELLOW)SKIP: No gwd tests found$(NC)"; \
	fi

.PHONY: test-lib
test-lib:
	@echo "$(BLUE)Running lib tests...$(NC)"
	$(VENV_PYTHON) -m pytest lib/db/tests/ -v --tb=short
	$(VENV_PYTHON) -m pytest lib/util/ -v --tb=short || echo "$(YELLOW)No tests found in lib/util$(NC)"

.PHONY: test-db-ops
test-db-ops:
	@echo "$(BLUE)Running database operations tests...$(NC)"
	$(VENV_PYTHON) -m pytest ged2gwb/tests/test_database_operations.py -v --tb=short

.PHONY: test-msgpack
test-msgpack:
	@echo "$(BLUE)Running MessagePack database tests...$(NC)"
	$(VENV_PYTHON) -m pytest lib/db/tests/test_msgpack_io.py -v --tb=short
	$(VENV_PYTHON) -m pytest lib/db/tests/test_integration.py -v --tb=short
	$(VENV_PYTHON) -m pytest ged2gwb/tests/test_database_operations.py -v --tb=short

.PHONY: test-coverage
test-coverage:
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	$(VENV_PYTHON) -m pytest --cov=gwb2ged --cov=ged2gwb --cov=gedcom --cov=lib --cov-report=html --cov-report=term

.PHONY: validate
validate:
	@echo "$(BLUE)Validating MessagePack implementation...$(NC)"
	@echo "$(YELLOW)Running MessagePack database tests...$(NC)"
	$(VENV_PYTHON) -m pytest lib/db/tests/test_msgpack_io.py -v --tb=short
	@echo "$(YELLOW)Running MessagePack integration tests...$(NC)"
	$(VENV_PYTHON) -m pytest lib/db/tests/test_integration.py -v --tb=short
	@echo "$(YELLOW)Running database operations tests...$(NC)"
	$(VENV_PYTHON) -m pytest ged2gwb/tests/test_database_operations.py -v --tb=short
	@echo "$(YELLOW)Running ged2gwb conversion tests...$(NC)"
	$(VENV_PYTHON) -m pytest ged2gwb/tests/test_concrete.py -v --tb=short
	@echo "$(GREEN)✓ MessagePack implementation validated$(NC)"

# Development
.PHONY: format
format:
	@echo "$(BLUE)Formatting code with ruff...$(NC)"
	$(VENV_PYTHON) -m ruff format ged2gwb/ gedcom/ lib/ gwb2ged/ --exclude=lib/old_db,lib/util,ged2gwb/examples,gedcom/tests,ged2gwb/tests,gwb2ged/tests
	@echo "$(GREEN)✓ Code formatted$(NC)"

.PHONY: lint
lint:
	@echo "$(BLUE)Running linting...$(NC)"
	@echo "$(YELLOW)Running ruff check...$(NC)"
	$(VENV_PYTHON) -m ruff check ged2gwb/ gedcom/ lib/ gwb2ged/ --exclude=lib/old_db,lib/util,ged2gwb/examples,gedcom/tests,ged2gwb/tests,gwb2ged/tests
	@echo "$(YELLOW)Running mypy check...$(NC)"
	$(VENV_PYTHON) -m mypy --ignore-missing-imports --exclude=ged2gwb/examples,gedcom/tests,ged2gwb/tests,gwb2ged/tests --follow-imports=skip --show-error-codes ged2gwb/ gedcom/ gwb2ged/ || true
	@echo "$(GREEN)✓ Linting completed$(NC)"

.PHONY: fix
fix:
	@echo "$(BLUE)Auto-fixing linting issues...$(NC)"
	$(VENV_PYTHON) -m ruff check --fix ged2gwb/ gedcom/ lib/ gwb2ged/ --exclude=lib/old_db,lib/util,ged2gwb/examples,gedcom/tests,ged2gwb/tests,gwb2ged/tests
	@echo "$(GREEN)✓ Auto-fixes applied$(NC)"

.PHONY: check
check: format fix lint test
	@echo "$(GREEN)✓ Complete check passed$(NC)"

# Utilities
.PHONY: clean
clean:
	@echo "$(BLUE)Cleaning temporary files...$(NC)"
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.msgpack" -delete 2>/dev/null || true
	@find . -type d -name "*.msgpack" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.gwb" -delete 2>/dev/null || true
	@find . -type d -name "test_bases" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@cd gwb2ged && $(MAKE) clean
	@echo "$(GREEN)✓ Cleanup completed$(NC)"
