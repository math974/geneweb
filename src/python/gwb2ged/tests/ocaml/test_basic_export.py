#!/usr/bin/env python3
"""
Simple test to understand gwb2ged OCaml behavior
Creates a temporary database using ged2gwb and tests gwb2ged export
"""

import sys
import os
import tempfile
import subprocess
from tools.test_utils import get_absolute_path, check_file_exists, run_command

def test_basic_export():
    """Test basic export without options - minimal compliance checks."""
    gwb2ged_path = get_absolute_path("distribution/gw/gwb2ged")
    ged2gwb_path = get_absolute_path("distribution/gw/ged2gwb")

    # Check if binaries exist
    if not check_file_exists(gwb2ged_path):
        print("SKIP: gwb2ged binary not found")
        return None

    if not check_file_exists(ged2gwb_path):
        print("SKIP: ged2gwb binary not found")
        return None

    # Create a simple GEDCOM file for testing
    test_gedcom_content = """0 HEAD
1 GEDC
2 VERS 5.5.1
1 CHAR UTF-8
0 @I1@ INDI
1 NAME John /Doe/
2 GIVN John
2 SURN Doe
1 SEX M
1 BIRT
2 DATE 01 JAN 1950
0 @I2@ INDI
1 NAME Jane /Smith/
2 GIVN Jane
2 SURN Smith
1 SEX F
1 BIRT
2 DATE 01 JAN 1955
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
0 TRLR
"""

    # Create temporary GEDCOM file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False) as f:
        f.write(test_gedcom_content)
        test_gedcom = f.name

    test_db_name = "test-basic-export"
    test_db_path = f"distribution/bases/{test_db_name}"

    try:
        # Clean up existing test database
        if os.path.exists(test_db_path):
            import shutil
            shutil.rmtree(test_db_path)

        print("Creating test database...")

        # Create database from GEDCOM
        cmd = [ged2gwb_path, test_gedcom, "-o", test_db_name, "-f"]
        returncode, stdout, stderr = run_command(cmd)

        if returncode != 0:
            print(f"FAIL: Failed to create test database: {stderr}")
            return None

        print("✓ Test database created")

        # Test gwb2ged export
        print("Testing gwb2ged export...")
        cmd = [gwb2ged_path, test_db_name]
        returncode, stdout, stderr = run_command(cmd)

        if returncode != 0:
            print(f"FAIL: Export failed: {stderr}")
            return None

        # Check GEDCOM compliance
        output = stdout + stderr
        lines = output.splitlines()

        # Minimal checks
        has_head = any(line.endswith("HEAD") or " HEAD" in line for line in lines)
        has_trlr = any(line.endswith("TRLR") or " TRLR" in line for line in lines)
        has_utf8 = any("CHAR UTF-8" in line for line in lines)
        has_version = any("VERS 5.5.1" in line for line in lines)

        if not (has_head and has_trlr and has_utf8 and has_version):
            print("FAIL: GEDCOM minimal compliance checks failed")
            print(f"  HEAD: {has_head}, TRLR: {has_trlr}, UTF-8: {has_utf8}, VERS: {has_version}")
            return None

        print("✓ GEDCOM compliance verified")
        print("✓ Basic export test passed")

        return output

    finally:
        # Cleanup
        if os.path.exists(test_gedcom):
            os.unlink(test_gedcom)
        if os.path.exists(test_db_path):
            import shutil
            shutil.rmtree(test_db_path)
        print("✓ Cleanup completed")

if __name__ == "__main__":
    print("=== Testing gwb2ged basic export ===")
    result = test_basic_export()
    if result is None:
        print("FAIL")
        sys.exit(1)
    print("PASS")
    sys.exit(0)
