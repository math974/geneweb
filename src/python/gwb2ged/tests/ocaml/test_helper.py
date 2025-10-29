#!/usr/bin/env python3
"""
Helper functions for testing gwb2ged binary (OCaml or Python)
"""

import os
import subprocess
from pathlib import Path


def detect_binary(binary_name="gwb2ged"):
    """
    Detect which binary to use (Python or OCaml).

    Priority:
    1. Python version (if USE_PYTHON_GWB2GED=true)
    2. OCaml binary in distribution/gw/

    Returns:
        tuple: (command_list, binary_type) where command_list is the command to run
    """
    # Check environment variable for Python version
    use_python = os.getenv("USE_PYTHON_GWB2GED", "false").lower() == "true"

    if use_python:
        # Try to find Python module
        try:
            result = subprocess.run(
                ["python3", "-m", "gwb2ged", "--help"],
                capture_output=True,
                timeout=2
            )
            if result.returncode == 0 or "gwb2ged" in result.stderr.decode():
                return (["python3", "-m", "gwb2ged"], "python")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    # Fallback to OCaml binary
    ocaml_bin = get_absolute_path(f"distribution/gw/{binary_name}")
    if os.path.exists(ocaml_bin):
        return ([ocaml_bin], "ocaml")

    raise FileNotFoundError(
        f"{binary_name} not found. "
        f"Set USE_PYTHON_GWB2GED=true for Python version or ensure OCaml binary exists."
    )


def get_absolute_path(relative_path):
    """Get absolute path from project root."""
    # Find project root (where main Makefile is)
    current = Path(__file__).resolve()
    # Go up from tests/ocaml/test_helper.py to project root
    # tests/ocaml/ -> tests/ -> gwb2ged/ -> python/ -> src/ -> root
    for parent in [current] + list(current.parents):
        if (parent / "Makefile").exists() and (parent / "distribution").exists():
            return str(parent / relative_path)
        # Also check for src/python/Makefile pattern
        if (parent / "src" / "python" / "Makefile").exists():
            return str(parent / relative_path)
    # Fallback to current directory relative
    script_dir = Path(__file__).parent
    # Try to go up to project root
    project_root = script_dir.parent.parent.parent.parent
    if (project_root / "Makefile").exists():
        return str(project_root / relative_path)
    return os.path.abspath(relative_path)


def run_gwb2ged(cmd_base, database_name, output_file=None, options=None):
    """
    Run gwb2ged with given parameters.

    Args:
        cmd_base: Base command list from detect_binary()
        database_name: Name of the database to export
        output_file: Output GEDCOM file path (optional)
        options: List of additional options (e.g., ["-indexes", "-charset", "UTF-8"])

    Returns:
        tuple: (returncode, stdout, stderr)
    """
    cmd = cmd_base + [database_name]

    if options:
        cmd.extend(options)

    if output_file:
        cmd.extend(["-o", output_file])

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def compare_gedcom_files(file1_path, file2_path, tolerance=True):
    """
    Compare two GEDCOM files.

    Args:
        file1_path: Path to first GEDCOM file
        file2_path: Path to second GEDCOM file
        tolerance: If True, allows minor differences (dates, IDs)

    Returns:
        tuple: (are_equal, differences)
    """
    with open(file1_path, 'r', encoding='utf-8', errors='replace') as f:
        content1 = f.read()

    with open(file2_path, 'r', encoding='utf-8', errors='replace') as f:
        content2 = f.read()

    if content1 == content2:
        return True, []

    if not tolerance:
        return False, [f"Files differ: {len(content1)} vs {len(content2)} bytes"]

    # Normalize differences (dates, IDs, etc.)
    lines1 = content1.splitlines()
    lines2 = content2.splitlines()

    differences = []
    max_lines = max(len(lines1), len(lines2))

    for i in range(max_lines):
        line1 = lines1[i] if i < len(lines1) else None
        line2 = lines2[i] if i < len(lines2) else None

        if line1 != line2:
            # Check if it's a difference we can tolerate
            if not _is_tolerable_difference(line1, line2):
                differences.append(f"Line {i+1}: {line1} != {line2}")

    return len(differences) == 0, differences


def _is_tolerable_difference(line1, line2):
    """Check if two lines differ only in acceptable ways."""
    if line1 is None or line2 is None:
        return False

    # Tolerate differences in:
    # - SOUR GeneWeb version numbers
    # - DATE in HEAD (export timestamp)
    # - ID numbers (I1 vs @I1@)

    # Skip SOUR lines with different versions
    if "SOUR GeneWeb" in line1 and "SOUR GeneWeb" in line2:
        return True

    # Skip DATE lines in HEAD (timestamps)
    if "DATE" in line1 and "DATE" in line2 and "HEAD" in line1:
        return True

    return False


def validate_gedcom_structure(gedcom_content):
    """
    Validate basic GEDCOM structure.

    Returns:
        tuple: (is_valid, issues)
    """
    issues = []

    if not gedcom_content.strip():
        issues.append("Empty GEDCOM file")
        return False, issues

    lines = gedcom_content.splitlines()

    # Must start with HEAD
    if not any("HEAD" in line for line in lines[:10]):
        issues.append("Missing HEAD record")

    # Must end with TRLR
    if not any("TRLR" in line for line in lines[-10:]):
        issues.append("Missing TRLR record")

    # Must have CHAR in HEAD
    has_char = False
    in_head = False
    for line in lines:
        if "HEAD" in line:
            in_head = True
        if in_head and "CHAR" in line:
            has_char = True
            break
        if line.strip().startswith("0 ") and "HEAD" not in line:
            in_head = False

    if not has_char:
        issues.append("Missing CHAR in HEAD")

    return len(issues) == 0, issues

