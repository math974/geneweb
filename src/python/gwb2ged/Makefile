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
	@echo "=== Testing gwb2ged basic export ==="
	@cd .. && PYTHONPATH=. python3 gwb2ged/tests/ocaml/test_basic_export.py

# Test gwb2ged -indexes option
test-indexes:
	@echo "=== Testing gwb2ged -indexes option ==="
	@cd .. && PYTHONPATH=. python3 gwb2ged/tests/ocaml/test_indexes_option.py

# Clean temporary files
clean:
	@echo "Cleaning gwb2ged test files..."
	@rm -rf ../../distribution/bases/test-*
	@rm -f /tmp/tmp*.ged
	@rm -f ../*.gwb ../*.msgpack

# Help
help:
	@echo "gwb2ged Test Targets:"
	@echo "  test          - Run all gwb2ged tests"
	@echo "  test-ocaml    - Run all OCaml binary tests"
	@echo "  test-basic    - Test basic gwb2ged functionality"
	@echo "  test-indexes  - Test gwb2ged -indexes option"
	@echo "  clean         - Clean temporary test files"
	@echo "  help          - Show this help"
