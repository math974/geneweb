#!/usr/bin/env python3
"""
Test for Python gwb2ged implementation
This test uses the same structure as the OCaml tests but for Python version
"""

import sys
import os
import tempfile
import subprocess
import shutil

# Add parent directory to path to import test helpers
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ocaml.test_helper import (
        detect_binary,
        get_absolute_path,
        run_gwb2ged,
        validate_gedcom_structure,
    )
except ImportError:
    # Fallback if test_helper not available
    def detect_binary(binary_name="gwb2ged"):
        """Simple fallback for binary detection"""
        use_python = os.getenv("USE_PYTHON_GWB2GED", "false").lower() == "true"
        if use_python:
            return (["python3", "-m", "gwb2ged"], "python")
        ocaml_bin = f"distribution/gw/{binary_name}"
        if os.path.exists(ocaml_bin):
            return ([ocaml_bin], "ocaml")
        raise FileNotFoundError(f"{binary_name} not found")


def test_python_basic_export():
    """Test Python gwb2ged basic export."""

    # Change to project root to ensure correct paths
    from tools.test_utils import get_project_root
    project_root = get_project_root()
    os.chdir(str(project_root))

    # Force Python version
    os.environ["USE_PYTHON_GWB2GED"] = "true"

    try:
        cmd_base, binary_type = detect_binary()
    except FileNotFoundError as e:
        print(f"SKIP: {e}")
        return False

    if binary_type != "python":
        print("SKIP: Python gwb2ged not available")
        return False

    ged2gwb_path = get_absolute_path("distribution/gw/ged2gwb")

    if not os.path.exists(ged2gwb_path):
        print("SKIP: ged2gwb binary not found (needed to create test database)")
        return False

    # Create simple test GEDCOM
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

    with tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False, encoding='utf-8') as f:
        f.write(test_gedcom_content)
        test_gedcom = f.name

    test_db_name = "test-python-export"
    bases_dir = get_absolute_path("distribution/bases")
    test_db_path = os.path.join(bases_dir, test_db_name)

    output_file = None

    try:
        # Clean up existing database
        if os.path.exists(test_db_path):
            shutil.rmtree(test_db_path)

        # Create database using ged2gwb
        cmd = [ged2gwb_path, test_gedcom, "-o", test_db_name, "-f"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"ERROR: Failed to create test database: {result.stderr}")
            return False

        # Export using Python gwb2ged
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False) as f:
            output_file = f.name

        returncode, stdout, stderr = run_gwb2ged(
            cmd_base, test_db_name, output_file=output_file
        )

        if returncode != 0:
            print(f"ERROR: Python export failed: {stderr}")
            return False

        # Validate exported GEDCOM
        with open(output_file, 'r', encoding='utf-8', errors='replace') as f:
            gedcom_content = f.read()

        is_valid, issues = validate_gedcom_structure(gedcom_content)

        if not is_valid:
            print(f"ERROR: Invalid GEDCOM structure: {issues}")
            return False

        return True

    finally:
        if output_file and os.path.exists(output_file):
            os.unlink(output_file)
        if os.path.exists(test_gedcom):
            os.unlink(test_gedcom)
        if os.path.exists(test_db_path):
            shutil.rmtree(test_db_path)


if __name__ == "__main__":
    if test_python_basic_export():
        print("✓ PASS")
        sys.exit(0)
    else:
        print("✗ FAIL")
        sys.exit(1)

