# Makefile for gwb2ged tests
# Tests for OCaml gwb2ged binary functionality

.PHONY: test test-ocaml test-basic test-indexes clean help

# Default target
all: test

# Run all gwb2ged tests
test: test-ocaml

# Run all OCaml binary tests
test-ocaml: test-basic test-indexes

# Test basic gwb2ged functionality
test-basic:
	@echo "$(BLUE)Testing gwb2ged basic export...$(NC)"
	@PYTHONPATH=.. python3 tests/ocaml/test_basic_export.py

# Test gwb2ged -indexes option
test-indexes:
	@echo "$(BLUE)Testing gwb2ged -indexes option...$(NC)"
	@PYTHONPATH=.. python3 tests/ocaml/test_indexes_option.py

# Clean temporary files
clean:
	@echo "$(BLUE)Cleaning gwb2ged test files...$(NC)"
	@rm -rf ../distribution/bases/test-*
	@rm -f /tmp/tmp*.ged
	@rm -f ../*.gwb ../*.msgpack

# Help
help:
	@echo "$(BLUE)gwb2ged Test Targets:$(NC)"
	@echo "  test          - Run all gwb2ged tests"
	@echo "  test-ocaml    - Run all OCaml binary tests"
	@echo "$(GREEN)  test-basic    - Test basic gwb2ged functionality$(NC)"
	@echo "$(GREEN)  test-indexes  - Test gwb2ged -indexes option$(NC)"
	@echo "$(GREEN)  clean         - Clean temporary test files$(NC)"
	@echo "$(GREEN)  help          - Show this help$(NC)"
