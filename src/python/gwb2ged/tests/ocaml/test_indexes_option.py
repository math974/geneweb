#!/usr/bin/env python3
"""
Specific test for the gwb2ged-test-indexes-option branch
Tests that the gwb2ged -indexes option works correctly
"""

import sys
import os
import subprocess
import tempfile
from pathlib import Path
from tools.test_utils import get_absolute_path

def test_gwb2ged_indexes():
    """Simple test for the gwb2ged -indexes option"""

    # Binary paths
    gwb2ged_path = get_absolute_path("distribution/gw/gwb2ged")
    ged2gwb_path = get_absolute_path("distribution/gw/ged2gwb")

    # Check that binaries exist
    if not os.path.exists(gwb2ged_path):
        print(f"$(RED)ERROR: gwb2ged binary not found: {gwb2ged_path}$(NC)")
        print("$(RED)Please build GeneWeb first: make$(NC)")
        return False

    if not os.path.exists(ged2gwb_path):
        print(f"$(RED)ERROR: ged2gwb binary not found: {ged2gwb_path}$(NC)")
        print("$(RED)Please build GeneWeb first: make$(NC)")
        return False

    print("$(GREEN)✓ Binaries found$(NC)")

    # Create a simple GEDCOM test file
    test_gedcom_content = """0 HEAD
1 GEDC
2 VERS 5.5.1
1 CHAR UTF-8
0 @I1@ INDI
1 NAME Jean /MARTIN/
2 GIVN Jean
2 SURN MARTIN
1 SEX M
1 BIRT
2 DATE 01 JAN 1950
0 @I2@ INDI
1 NAME Marie /DUPONT/
2 GIVN Marie
2 SURN DUPONT
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

    test_db_name = "test-indexes"
    test_db_path = f"distribution/bases/{test_db_name}"

    # Initialize output files variables
    output_no_indexes = None
    output_with_indexes = None

    try:
        # Clean up existing test database
        if os.path.exists(test_db_path):
            import shutil
            shutil.rmtree(test_db_path)

        print("1. Creating test database...")

        # Create database
        cmd = [ged2gwb_path, test_gedcom, "-o", test_db_name, "-f"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"ERROR: Failed to create database: {result.stderr}")
            return False

        print("✓ Test database created")

        # Test 1: Export WITHOUT indexes
        print("\n2. Testing export WITHOUT indexes...")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False) as f:
            output_no_indexes = f.name

        cmd = [gwb2ged_path, test_db_name, "-o", output_no_indexes]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"ERROR: Export without indexes failed: {result.stderr}")
            return False

        # Verify that _GWID tags are NOT present
        with open(output_no_indexes, 'r') as f:
            content_no_indexes = f.read()

        if "_GWID" in content_no_indexes:
            print("ERROR: _GWID tags found in export without -indexes")
            return False

        print("✓ Export without indexes OK (no _GWID tags)")

        # Test 2: Export WITH indexes
        print("\n3. Testing export WITH indexes...")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False) as f:
            output_with_indexes = f.name

        cmd = [gwb2ged_path, test_db_name, "-indexes", "-o", output_with_indexes]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"ERROR: Export with indexes failed: {result.stderr}")
            return False

        # Verify that _GWID tags ARE present
        with open(output_with_indexes, 'r') as f:
            content_with_indexes = f.read()

        if "_GWID" not in content_with_indexes:
            print("ERROR: No _GWID tags found in export with -indexes")
            return False

        # Count _GWID tags
        gwid_count = content_with_indexes.count("_GWID")
        print(f"✓ Export with indexes OK ({gwid_count} _GWID tags found)")

        # Test 3: Verify GEDCOM format
        print("\n4. Verifying GEDCOM format...")

        for content, name in [(content_no_indexes, "without indexes"), (content_with_indexes, "with indexes")]:
            if not ("0 HEAD" in content and "0 TRLR" in content):
                print(f"ERROR: Invalid GEDCOM format ({name})")
                return False

        print("✓ GEDCOM format valid")

        # Test 4: Compare sizes
        print("\n5. Comparing sizes...")

        size_no_indexes = len(content_no_indexes)
        size_with_indexes = len(content_with_indexes)

        print(f"  Without indexes: {size_no_indexes} characters")
        print(f"  With indexes: {size_with_indexes} characters")

        if size_with_indexes > size_no_indexes:
            print("✓ File with indexes is larger (expected)")
        else:
            print("⚠ Warning: File with indexes is not larger")

        # Display sample of result with indexes
        print("\n6. Sample of result with indexes:")
        print("-" * 50)
        lines = content_with_indexes.split('\n')
        for i, line in enumerate(lines[:20]):
            print(f"{i+1:2d}: {line}")
        if len(lines) > 20:
            print(f"    ... ({len(lines) - 20} additional lines)")
        print("-" * 50)

        return True

    finally:
        # Cleanup
        if os.path.exists(test_gedcom):
            os.unlink(test_gedcom)
        if output_no_indexes and os.path.exists(output_no_indexes):
            os.unlink(output_no_indexes)
        if output_with_indexes and os.path.exists(output_with_indexes):
            os.unlink(output_with_indexes)
        if os.path.exists(test_db_path):
            import shutil
            shutil.rmtree(test_db_path)

        print("\n✓ Cleanup completed")

if __name__ == "__main__":

    if test_gwb2ged_indexes():
        print("✓ ALL TESTS PASSED!")
        print("The gwb2ged -indexes option works correctly.")
        print("It adds _GWID tags to preserve internal GeneWeb IDs.")
        sys.exit(0)
    else:
        print("\n" + "=" * 50)
        print("✗ TESTS FAILED!")
        print("The gwb2ged -indexes option is not working correctly.")
        sys.exit(1)
