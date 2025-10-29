#!/usr/bin/env python3
"""
Test for the gwb2ged -charset option
Tests that different charset options produce correct GEDCOM headers and encoding
"""

import sys
import os
import subprocess
import tempfile
import shutil

def test_gwb2ged_charset():
    """Test gwb2ged with different charset options"""

    print("=== Test GWB2GED -charset Option ===\n")

    # Check that we're in the right directory
    if not os.path.exists("Makefile"):
        print("ERROR: This script must be run from the GeneWeb project root")
        return False

    # Binary paths
    gwb2ged_path = "distribution/gw/gwb2ged"
    ged2gwb_path = "distribution/gw/ged2gwb"

    # Check that binaries exist
    if not os.path.exists(gwb2ged_path):
        print(f"ERROR: gwb2ged binary not found: {gwb2ged_path}")
        print("Please build GeneWeb first: make")
        return False

    if not os.path.exists(ged2gwb_path):
        print(f"ERROR: ged2gwb binary not found: {ged2gwb_path}")
        print("Please build GeneWeb first: make")
        return False

    print("✓ Binaries found")

    # Create a GEDCOM test file with UTF-8 characters
    test_gedcom_content = """0 HEAD
1 GEDC
2 VERS 5.5.1
1 CHAR UTF-8
0 @I1@ INDI
1 NAME François /Müller/
2 GIVN François
2 SURN Müller
1 SEX M
1 BIRT
2 DATE 01 JAN 1950
0 @I2@ INDI
1 NAME Marie /Dupont/
2 GIVN Marie
2 SURN Dupont
1 SEX F
1 BIRT
2 DATE 01 JAN 1955
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
0 TRLR
"""

    # Create temporary GEDCOM file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False, encoding='utf-8') as f:
        f.write(test_gedcom_content)
        test_gedcom = f.name

    test_db_name = "test-charset"
    test_db_path = f"distribution/bases/{test_db_name}"

    # Test each charset option
    charsets = ["UTF-8", "ASCII", "ANSEL", "ANSI"]
    output_files = {}

    try:
        # Clean up existing test database
        if os.path.exists(test_db_path):
            shutil.rmtree(test_db_path)

        print("1. Creating test database...")

        # Create database
        cmd = [ged2gwb_path, test_gedcom, "-o", test_db_name, "-f"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"ERROR: Failed to create database: {result.stderr}")
            return False

        print("✓ Test database created")

        # Test each charset
        for charset in charsets:
            print(f"\n2. Testing export with charset: {charset}...")

            with tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False) as f:
                output_files[charset] = f.name

            cmd = [gwb2ged_path, test_db_name, "-charset", charset, "-o", output_files[charset]]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"ERROR: Export with charset {charset} failed: {result.stderr}")
                return False

            # Read the exported file
            with open(output_files[charset], 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()

            # Verify CHAR header
            expected_char = f"1 CHAR {charset}"
            if expected_char not in content:
                print(f"ERROR: CHAR header not found for charset {charset}")
                print(f"Expected: {expected_char}")
                print(f"Content sample:\n{content[:500]}")
                return False

            print(f"✓ CHAR header correct: {expected_char}")

            # Verify GEDCOM version
            if charset == "UTF-8":
                if "2 VERS 5.5.1" not in content:
                    print(f"ERROR: Expected VERS 5.5.1 for UTF-8, not found")
                    return False
                print("✓ GEDCOM version correct: 5.5.1")
            else:
                if "2 VERS 5.5" not in content:
                    print(f"ERROR: Expected VERS 5.5 for {charset}, not found")
                    return False
                print("✓ GEDCOM version correct: 5.5")

            # Verify basic GEDCOM structure
            if not ("0 HEAD" in content and "0 TRLR" in content):
                print(f"ERROR: Invalid GEDCOM format for charset {charset}")
                return False

            print(f"✓ Export with {charset} OK")

        # Test default (should be UTF-8)
        print("\n3. Testing export without charset option (default should be UTF-8)...")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False) as f:
            default_output = f.name

        cmd = [gwb2ged_path, test_db_name, "-o", default_output]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"ERROR: Export without charset option failed: {result.stderr}")
            return False

        with open(default_output, 'r', encoding='utf-8', errors='replace') as f:
            default_content = f.read()

        if "1 CHAR UTF-8" not in default_content:
            print("ERROR: Default charset should be UTF-8, but not found")
            return False

        if "2 VERS 5.5.1" not in default_content:
            print("ERROR: Default should use VERS 5.5.1, but not found")
            return False

        print("✓ Default charset is UTF-8 (as expected)")

        # Display sample of results
        print("\n4. Sample of results:")
        print("-" * 50)
        for charset in charsets:
            with open(output_files[charset], 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
                print(f"\n{charset}:")
                for i, line in enumerate(lines[:15]):
                    print(f"  {line.rstrip()}")
                if len(lines) > 15:
                    print(f"  ... ({len(lines) - 15} additional lines)")
        print("-" * 50)

        return True

    finally:
        # Cleanup
        if os.path.exists(test_gedcom):
            os.unlink(test_gedcom)
        for charset, output_file in output_files.items():
            if os.path.exists(output_file):
                os.unlink(output_file)
        if 'default_output' in locals() and os.path.exists(default_output):
            os.unlink(default_output)
        if os.path.exists(test_db_path):
            shutil.rmtree(test_db_path)

        print("\n✓ Cleanup completed")


if __name__ == "__main__":
    if test_gwb2ged_charset():
        print("✓ PASS")
        sys.exit(0)
    else:
        print("✗ FAIL")
        sys.exit(1)

