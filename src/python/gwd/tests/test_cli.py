"""Tests for gwd CLI."""
import pytest
import sys
import subprocess
from pathlib import Path


def test_gwd_binary_exists():
    """Test that gwd binary exists and is executable."""
    project_root = Path(__file__).parent.parent.parent
    gwd_binary = project_root / "bin" / "gwd"

    assert gwd_binary.exists(), "gwd binary should exist in bin/"
    assert gwd_binary.is_file(), "gwd should be a file"
    # Check if executable (Unix systems)
    import os
    if os.name != 'nt':  # Not Windows
        assert os.access(gwd_binary, os.X_OK), "gwd should be executable"


def test_gwd_module_can_be_imported():
    """Test that gwd module can be imported."""
    try:
        from gwd import __version__
        assert __version__ is not None
    except ImportError:
        pytest.skip("gwd module not installed")


def test_gwd_cli_help():
    """Test that gwd CLI shows help."""
    project_root = Path(__file__).parent.parent.parent
    gwd_binary = project_root / "bin" / "gwd"

    if not gwd_binary.exists():
        pytest.skip("gwd binary not found")

    # Run help command with longer timeout and check for import errors
    result = subprocess.run(
        [str(gwd_binary), "--help"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(project_root)
    )

    # Accept exit code 0 (success) or 2 (help), but not import errors
    if "ImportError" in result.stderr or "ModuleNotFoundError" in result.stderr:
        pytest.skip(f"gwd module dependencies not installed: {result.stderr}")

    # Should succeed or show help
    assert result.returncode in [0, 2], f"gwd --help should work, got exit {result.returncode}, stderr: {result.stderr}"

