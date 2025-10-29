#!/bin/bash
# Run all OCaml binary tests for gwb2ged
# This script runs all test files in the ocaml directory

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# We know we're in src/python/gwb2ged/tests/ocaml, so go up 5 levels to root
PROJECT_ROOT="$SCRIPT_DIR"
for i in {1..6}; do
    PROJECT_ROOT="$(dirname "$PROJECT_ROOT")"
    # Check if this is the root Makefile (one that exists and is not in a subdirectory)
    if [ -f "$PROJECT_ROOT/Makefile" ] && [ ! -f "$(dirname "$PROJECT_ROOT")/Makefile" ]; then
        break
    fi
done

# Verify we found a valid project root (should have distribution/ directory)
if [ ! -f "$PROJECT_ROOT/Makefile" ] || [ ! -d "$PROJECT_ROOT/distribution" ]; then
    exit 1
fi

# Find all test files
OCAML_DIR="$SCRIPT_DIR"
TESTS=()

for test_file in "$OCAML_DIR"/test_*.py; do
    if [ -f "$test_file" ]; then
        filename=$(basename "$test_file")
        if [ "$filename" != "run_all_tests.py" ] && [ "$filename" != "run_all_tests.sh" ]; then
            TESTS+=("$filename")
        fi
    fi
done

# Sort tests
IFS=$'\n' TESTS=($(sort <<<"${TESTS[*]}"))
unset IFS

# If no tests found, exit
if [ ${#TESTS[@]} -eq 0 ]; then
    exit 1
fi

# Run each test
FAILED=0
for test_file in "${TESTS[@]}"; do
    test_path="$OCAML_DIR/$test_file"

    if [ ! -f "$test_path" ]; then
        echo "✗ FAIL: $test_file (file not found)"
        FAILED=1
        continue
    fi

    # Run test (output redirected, we only care about exit code)
    cd "$PROJECT_ROOT" || exit 1
    if PYTHONPATH="$PROJECT_ROOT/src/python" python3 "$test_path" >/dev/null 2>&1; then
        echo "✓ PASS: $test_file"
    else
        echo "✗ FAIL: $test_file"
        FAILED=1
    fi
done

# Exit with appropriate code
exit $FAILED

