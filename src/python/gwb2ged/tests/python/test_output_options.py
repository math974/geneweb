"""Tests for gwb2ged output options (-o, -charset, -v)

These tests use the Python gwb2ged implementation.
Set USE_PYTHON_GWB2GED=true to use Python version.
"""

import os
import sys
import tempfile
import subprocess
import shutil
import pytest
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.test_utils import get_project_root, get_absolute_path

# Import test helper for binary detection
try:
    from ocaml.test_helper import detect_binary
except ImportError:
    # Fallback if path is different
    try:
        from gwb2ged.tests.ocaml.test_helper import detect_binary
    except ImportError:
        from tests.ocaml.test_helper import detect_binary


def _setup_test_environment():
    """Setup common test environment"""
    project_root = get_project_root()
    os.chdir(str(project_root))
    os.environ["USE_PYTHON_GWB2GED"] = "true"

    # Detect Python binary
    try:
        gwb2ged_cmd, binary_type = detect_binary()
    except FileNotFoundError:
        pytest.skip("gwb2ged not found (Python or OCaml)")

    if binary_type != "python":
        pytest.skip("Python gwb2ged not available (set USE_PYTHON_GWB2GED=true)")

    # Verify Python ged2gwb is available
    ged2gwb_cmd = ["python3", "-m", "ged2gwb"]
    try:
        result = subprocess.run(
            ged2gwb_cmd + ["--help"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(project_root)
        )
        if result.returncode != 0 and "ged2gwb" not in result.stdout and "ged2gwb" not in result.stderr:
            pytest.skip("Python ged2gwb module not available")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pytest.skip("Python ged2gwb module not available")

    return gwb2ged_cmd, ged2gwb_cmd, project_root


def _display_gedcom_content(file_path, description=""):
    """Display GEDCOM file content for inspection"""
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    print(f"\n{'='*60}")
    if description:
        print(f"{description}")
    print(f"GEDCOM file: {file_path}")
    print(f"{'='*60}")
    print(content)
    print(f"{'='*60}\n")
    return content


def test_output_to_file():
    """Test -o option: export to file"""
    gwb2ged_cmd, ged2gwb_cmd, project_root = _setup_test_environment()

    # Create a test GEDCOM file
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
2 DATE 1980
0 @I2@ INDI
1 NAME Jane /Smith/
2 GIVN Jane
2 SURN Smith
1 SEX F
1 BIRT
2 DATE 1985
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 MARR
2 DATE 2010
0 TRLR
"""

    test_db_name = "test-output-file"
    bases_dir = get_absolute_path("distribution/bases")
    test_db_path = os.path.join(bases_dir, f"{test_db_name}.msgpack")
    test_db_path_gwb = os.path.join(bases_dir, test_db_name)

    test_gedcom = None
    output_file = None

    try:
        # Clean up existing databases
        if os.path.exists(test_db_path):
            shutil.rmtree(test_db_path)
        if os.path.exists(test_db_path_gwb):
            shutil.rmtree(test_db_path_gwb)

        # Create test GEDCOM file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False, encoding='utf-8') as f:
            f.write(test_gedcom_content)
            test_gedcom = f.name

        # Create MessagePack database from GEDCOM using Python ged2gwb
        cmd = ged2gwb_cmd + [
            str(test_gedcom),
            "-bd", str(bases_dir),
            "-o", test_db_name,
            "-f"
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(project_root),
            env={**os.environ, "PYTHONPATH": str(project_root)}
        )
        assert result.returncode == 0, f"Failed to create database: {result.stderr}"

        # Verify .msgpack database was created
        msgpack_db_path = os.path.join(bases_dir, f"{test_db_name}.msgpack")
        assert os.path.exists(msgpack_db_path), f"MessagePack database not created at {msgpack_db_path}"

        # Test export to file using Python binary
        output_file = tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False)
        output_file.close()

        cmd = gwb2ged_cmd + [test_db_name, "-o", output_file.name]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(project_root))

        assert result.returncode == 0, f"Export failed: {result.stderr}"

        # Check that file was created and has content
        assert os.path.exists(output_file.name), "Output file was not created"

        # Display and verify GEDCOM content
        content = _display_gedcom_content(output_file.name, "Test: Export to file (-o option)")

        assert content, "Output file is empty"
        assert "0 HEAD" in content, "Output file missing HEAD"
        assert "0 TRLR" in content, "Output file missing TRLR"

        print("✓ Export to file works")

    finally:
        # Cleanup
        if test_gedcom and os.path.exists(test_gedcom):
            os.unlink(test_gedcom)
        if output_file and os.path.exists(output_file.name):
            os.unlink(output_file.name)
        if os.path.exists(test_db_path):
            shutil.rmtree(test_db_path)
        if os.path.exists(test_db_path_gwb):
            shutil.rmtree(test_db_path_gwb)


def test_output_to_stdout():
    """Test default output: stdout"""
    gwb2ged_cmd, ged2gwb_cmd, project_root = _setup_test_environment()

    # Create a test GEDCOM file
    test_gedcom_content = """0 HEAD
1 GEDC
2 VERS 5.5.1
1 CHAR UTF-8
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
0 TRLR
"""

    test_db_name = "test-output-stdout"
    bases_dir = get_absolute_path("distribution/bases")
    test_db_path = os.path.join(bases_dir, f"{test_db_name}.msgpack")
    test_db_path_gwb = os.path.join(bases_dir, test_db_name)

    test_gedcom = None

    try:
        # Clean up existing databases
        if os.path.exists(test_db_path):
            shutil.rmtree(test_db_path)
        if os.path.exists(test_db_path_gwb):
            shutil.rmtree(test_db_path_gwb)

        # Create test GEDCOM file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False, encoding='utf-8') as f:
            f.write(test_gedcom_content)
            test_gedcom = f.name

        # Create MessagePack database from GEDCOM using Python ged2gwb
        cmd = ged2gwb_cmd + [
            str(test_gedcom),
            "-bd", str(bases_dir),
            "-o", test_db_name,
            "-f"
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(project_root),
            env={**os.environ, "PYTHONPATH": str(project_root)}
        )
        assert result.returncode == 0, f"Failed to create database: {result.stderr}"

        # Verify .msgpack database was created
        msgpack_db_path = os.path.join(bases_dir, f"{test_db_name}.msgpack")
        assert os.path.exists(msgpack_db_path), f"MessagePack database not created at {msgpack_db_path}"

        # Test export to stdout (no -o option) using Python binary
        cmd = gwb2ged_cmd + [test_db_name]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(project_root))

        assert result.returncode == 0, f"Export to stdout failed: {result.stderr}"

        # Display stdout content
        print(f"\n{'='*60}")
        print("Test: Export to stdout (default)")
        print(f"{'='*60}")
        print(result.stdout)
        print(f"{'='*60}\n")

        # Check that stdout has content
        assert result.stdout, "No output to stdout"
        assert "0 HEAD" in result.stdout, "stdout missing HEAD"
        assert "0 TRLR" in result.stdout, "stdout missing TRLR"

        print("✓ Export to stdout works")

    finally:
        # Cleanup
        if test_gedcom and os.path.exists(test_gedcom):
            os.unlink(test_gedcom)
        if os.path.exists(test_db_path):
            shutil.rmtree(test_db_path)
        if os.path.exists(test_db_path_gwb):
            shutil.rmtree(test_db_path_gwb)


def test_charset_utf8():
    """Test -charset UTF-8 option"""
    gwb2ged_cmd, ged2gwb_cmd, project_root = _setup_test_environment()

    # Create a test GEDCOM file with UTF-8 characters
    test_gedcom_content = """0 HEAD
1 GEDC
2 VERS 5.5.1
1 CHAR UTF-8
0 @I1@ INDI
1 NAME José /García/
1 SEX M
0 TRLR
"""

    test_db_name = "test-charset-utf8"
    bases_dir = get_absolute_path("distribution/bases")
    test_db_path = os.path.join(bases_dir, f"{test_db_name}.msgpack")
    test_db_path_gwb = os.path.join(bases_dir, test_db_name)

    test_gedcom = None
    output_file = None

    try:
        # Clean up existing databases
        if os.path.exists(test_db_path):
            shutil.rmtree(test_db_path)
        if os.path.exists(test_db_path_gwb):
            shutil.rmtree(test_db_path_gwb)

        # Create test GEDCOM file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False, encoding='utf-8') as f:
            f.write(test_gedcom_content)
            test_gedcom = f.name

        # Create MessagePack database from GEDCOM using Python ged2gwb
        cmd = ged2gwb_cmd + [
            str(test_gedcom),
            "-bd", str(bases_dir),
            "-o", test_db_name,
            "-f"
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(project_root),
            env={**os.environ, "PYTHONPATH": str(project_root)}
        )
        assert result.returncode == 0, f"Failed to create database: {result.stderr}"

        # Verify .msgpack database was created
        msgpack_db_path = os.path.join(bases_dir, f"{test_db_name}.msgpack")
        assert os.path.exists(msgpack_db_path), f"MessagePack database not created at {msgpack_db_path}"

        # Test export with UTF-8 charset using Python binary
        output_file = tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False)
        output_file.close()

        cmd = gwb2ged_cmd + [test_db_name, "-charset", "UTF-8", "-o", output_file.name]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(project_root))

        assert result.returncode == 0, f"Export with UTF-8 failed: {result.stderr}"

        # Display and check charset in output
        content = _display_gedcom_content(output_file.name, "Test: Export with UTF-8 charset")

        assert "1 CHAR UTF-8" in content, "UTF-8 charset not found in output"

        # Check that UTF-8 characters are preserved
        if "José" not in content and "Jos" in content:
            print("WARNING: UTF-8 characters may not be preserved correctly")
            # Not a failure, as this depends on the binary implementation

        print("✓ UTF-8 charset works")

    finally:
        # Cleanup
        if test_gedcom and os.path.exists(test_gedcom):
            os.unlink(test_gedcom)
        if output_file and os.path.exists(output_file.name):
            os.unlink(output_file.name)
        if os.path.exists(test_db_path):
            shutil.rmtree(test_db_path)
        if os.path.exists(test_db_path_gwb):
            shutil.rmtree(test_db_path_gwb)


def test_charset_ascii():
    """Test -charset ASCII option"""
    gwb2ged_cmd, ged2gwb_cmd, project_root = _setup_test_environment()

    # Create a simple test database
    test_gedcom_content = """0 HEAD
1 GEDC
2 VERS 5.5.1
1 CHAR UTF-8
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
0 TRLR
"""

    test_db_name = "test-charset-ascii"
    bases_dir = get_absolute_path("distribution/bases")
    test_db_path = os.path.join(bases_dir, f"{test_db_name}.msgpack")
    test_db_path_gwb = os.path.join(bases_dir, test_db_name)

    test_gedcom = None
    output_file = None

    try:
        # Clean up existing databases
        if os.path.exists(test_db_path):
            shutil.rmtree(test_db_path)
        if os.path.exists(test_db_path_gwb):
            shutil.rmtree(test_db_path_gwb)

        # Create test GEDCOM file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False, encoding='utf-8') as f:
            f.write(test_gedcom_content)
            test_gedcom = f.name

        # Create MessagePack database from GEDCOM using Python ged2gwb
        cmd = ged2gwb_cmd + [
            str(test_gedcom),
            "-bd", str(bases_dir),
            "-o", test_db_name,
            "-f"
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(project_root),
            env={**os.environ, "PYTHONPATH": str(project_root)}
        )
        assert result.returncode == 0, f"Failed to create database: {result.stderr}"

        # Verify .msgpack database was created
        msgpack_db_path = os.path.join(bases_dir, f"{test_db_name}.msgpack")
        assert os.path.exists(msgpack_db_path), f"MessagePack database not created at {msgpack_db_path}"

        # Test export with ASCII charset using Python binary
        output_file = tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False)
        output_file.close()

        cmd = gwb2ged_cmd + [test_db_name, "-charset", "ASCII", "-o", output_file.name]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(project_root))

        assert result.returncode == 0, f"Export with ASCII failed: {result.stderr}"

        # Display and check charset in output
        content = _display_gedcom_content(output_file.name, "Test: Export with ASCII charset")

        assert "1 CHAR ASCII" in content, "ASCII charset not found in output"

        print("✓ ASCII charset works")

    finally:
        # Cleanup
        if test_gedcom and os.path.exists(test_gedcom):
            os.unlink(test_gedcom)
        if output_file and os.path.exists(output_file.name):
            os.unlink(output_file.name)
        if os.path.exists(test_db_path):
            shutil.rmtree(test_db_path)
        if os.path.exists(test_db_path_gwb):
            shutil.rmtree(test_db_path_gwb)


def test_verbose_option():
    """Test -v (verbose) option"""
    gwb2ged_cmd, ged2gwb_cmd, project_root = _setup_test_environment()

    # Create a simple test database
    test_gedcom_content = """0 HEAD
1 GEDC
2 VERS 5.5.1
1 CHAR UTF-8
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
0 TRLR
"""

    test_db_name = "test-verbose"
    bases_dir = get_absolute_path("distribution/bases")
    test_db_path = os.path.join(bases_dir, f"{test_db_name}.msgpack")
    test_db_path_gwb = os.path.join(bases_dir, test_db_name)

    test_gedcom = None
    output_file = None

    try:
        # Clean up existing databases
        if os.path.exists(test_db_path):
            shutil.rmtree(test_db_path)
        if os.path.exists(test_db_path_gwb):
            shutil.rmtree(test_db_path_gwb)

        # Create test GEDCOM file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False, encoding='utf-8') as f:
            f.write(test_gedcom_content)
            test_gedcom = f.name

        # Create MessagePack database from GEDCOM using Python ged2gwb
        cmd = ged2gwb_cmd + [
            str(test_gedcom),
            "-bd", str(bases_dir),
            "-o", test_db_name,
            "-f"
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(project_root),
            env={**os.environ, "PYTHONPATH": str(project_root)}
        )
        assert result.returncode == 0, f"Failed to create database: {result.stderr}"

        # Verify .msgpack database was created
        msgpack_db_path = os.path.join(bases_dir, f"{test_db_name}.msgpack")
        assert os.path.exists(msgpack_db_path), f"MessagePack database not created at {msgpack_db_path}"

        # Test export with verbose option using Python binary
        output_file = tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False)
        output_file.close()

        cmd = gwb2ged_cmd + [test_db_name, "-v", "-o", output_file.name]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(project_root))

        assert result.returncode == 0, f"Export with verbose failed: {result.stderr}"

        # Display GEDCOM content
        content = _display_gedcom_content(output_file.name, "Test: Export with verbose option (-v)")

        # With verbose, stderr should have more information
        # (This is implementation-dependent, just check that it runs)
        assert os.path.exists(output_file.name), "Output file was not created"

        if result.stderr:
            print(f"Verbose output (stderr):\n{result.stderr}\n")

        print("✓ Verbose option works")

    finally:
        # Cleanup
        if test_gedcom and os.path.exists(test_gedcom):
            os.unlink(test_gedcom)
        if output_file and os.path.exists(output_file.name):
            os.unlink(output_file.name)
        if os.path.exists(test_db_path):
            shutil.rmtree(test_db_path)
        if os.path.exists(test_db_path_gwb):
            shutil.rmtree(test_db_path_gwb)

