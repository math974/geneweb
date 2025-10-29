# Makefile for gwb2ged tests
# Tests for OCaml gwb2ged binary functionality

# Colors for output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[0;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

.PHONY: test test-ocaml test-basic test-indexes test-charset clean help

# Default target
all: test

# Run all gwb2ged tests
test: test-ocaml

# Run all OCaml binary tests (automatically discovers all test files)
test-ocaml:
	@echo "$(BLUE)Testing gwb2ged OCaml binary...$(NC)"
	@if [ ! -x ../../../distribution/gw/gwb2ged ]; then \
		echo "$(YELLOW)SKIP: gwb2ged binary not found$(NC)"; \
		exit 0; \
	else \
		cd .. && bash gwb2ged/tests/ocaml/run_all_tests.sh; \
	fi

# Test basic gwb2ged functionality
test-basic:
	@echo "$(BLUE)Testing gwb2ged basic export...$(NC)"
	@if [ ! -x ../../../distribution/gw/gwb2ged ]; then \
		echo "$(YELLOW)SKIP: gwb2ged binary not found$(NC)"; \
		exit 0; \
	else \
		cd .. && PYTHONPATH=. python3 gwb2ged/tests/ocaml/test_basic_export.py >/dev/null 2>&1; \
	fi

# Test gwb2ged -indexes option
test-indexes:
	@echo "$(BLUE)Testing gwb2ged -indexes option...$(NC)"
	@if [ ! -x ../../../distribution/gw/gwb2ged ]; then \
		echo "$(YELLOW)SKIP: gwb2ged binary not found$(NC)"; \
		exit 0; \
	else \
		cd .. && PYTHONPATH=. python3 gwb2ged/tests/ocaml/test_indexes_option.py >/dev/null 2>&1; \
	fi

# Test gwb2ged -charset option
test-charset:
	@echo "$(BLUE)Testing gwb2ged -charset option...$(NC)"
	@if [ ! -x ../../../distribution/gw/gwb2ged ]; then \
		echo "$(YELLOW)SKIP: gwb2ged binary not found$(NC)"; \
		exit 0; \
	else \
		cd .. && PYTHONPATH=. python3 gwb2ged/tests/ocaml/test_charset_options.py >/dev/null 2>&1; \
	fi

# Clean temporary files
clean:
	@echo "$(BLUE)Cleaning gwb2ged test files...$(NC)"
	@rm -rf ../../../distribution/bases/test-* 2>/dev/null || true
	@rm -f /tmp/tmp*.ged 2>/dev/null || true
	@rm -f ../*.gwb ../*.msgpack 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup completed$(NC)"

# Help
help:
	@echo "gwb2ged Test Targets:"
	@echo "  test          - Run all gwb2ged tests"
	@echo "  test-ocaml    - Run all OCaml binary tests"
	@echo "  test-basic    - Test basic gwb2ged functionality"
	@echo "  test-indexes  - Test gwb2ged -indexes option"
	@echo "  test-charset  - Test gwb2ged -charset option"
	@echo "  clean         - Clean temporary test files"
	@echo "  help          - Show this help"
