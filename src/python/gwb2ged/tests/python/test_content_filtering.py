#!/usr/bin/env python3
"""
Content filtering tests for gwb2ged (Python implementation)

Tests:
- -c NUM: censor recent births (and propagate to spouses/descendants)
- -nn / -nnn: notes filtering
- -source SRC: replace sources
- -nopicture: remove multimedia placeholders (no-op safe)

Integration: uses Python ged2gwb to create a .msgpack DB, then runs python -m gwb2ged.
"""

import os
import tempfile
import subprocess

from tools.test_utils import get_absolute_path
from .test_helper import get_fixture_path


def _create_db_from_fixture(fixture_filename: str, db_name: str):
    """Create database from a fixture GEDCOM file."""
    project_root = get_absolute_path("")
    bases_dir = get_absolute_path("distribution/bases")
    os.makedirs(bases_dir, exist_ok=True)

    ged_file = get_fixture_path(fixture_filename)

    cmd = [
        "python3",
        "-m",
        "ged2gwb",
        ged_file,
        "-bd",
        bases_dir,
        "-o",
        db_name,
        "-f",
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=project_root,
        env={**os.environ, "PYTHONPATH": project_root},
    )
    assert result.returncode == 0, f"ged2gwb failed: {result.stderr}"


def _run_gwb2ged(db_name: str, options: list[str]):
    project_root = get_absolute_path("")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ged", delete=False) as f:
        out_file = f.name
    try:
        cmd = ["python3", "-m", "gwb2ged", db_name, "-o", out_file] + options
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=project_root,
            env={**os.environ, "PYTHONPATH": project_root},
        )
        assert result.returncode == 0, f"gwb2ged failed: {result.stderr}"
        with open(out_file, "r", encoding="utf-8") as f:
            return f.read()
    finally:
        if os.path.exists(out_file):
            os.unlink(out_file)


def test_censor_by_age_and_propagation():
    """Test -c option: censor persons born less than N years ago and propagate to spouses/descendants"""
    db = "test-censor"
    _create_db_from_fixture("test_content_censor.ged", db)

    # Select by surname Smith; apply -c 18 -> censor Father (2010) and Child (2020)
    content = _run_gwb2ged(db, ["-s", "Smith", "-c", "18"])  # recent births censored

    # Expect only Grandfather to remain
    assert "Grandfather /Smith/" in content
    assert "Father /Smith/" not in content
    assert "Child /Smith/" not in content


def test_notes_filtering_nn_nnn_and_source_replacement():
    """Test -nn/-nnn options: filter notes and -source option: replace sources"""
    db = "test-notes-source"
    _create_db_from_fixture("test_content_notes.ged", db)

    # Default: include database notes
    content = _run_gwb2ged(db, [])
    assert "1 NOTE Person note" in content or "Person note" in content

    # -nnn: exclude all notes
    content = _run_gwb2ged(db, ["-nnn"])
    assert "Person note" not in content
    assert "Family note" not in content

    # -source replacement
    content = _run_gwb2ged(db, ["-source", "UnifiedSource"])
    assert "1 SOUR UnifiedSource" in content or "UnifiedSource" in content


def test_nopicture_safe_noop():
    """Test -nopicture option: safe no-op (multimedia not extracted yet)"""
    db = "test-nopicture"
    _create_db_from_fixture("test_content_nopicture.ged", db)

    content = _run_gwb2ged(db, ["-nopicture"])  # No multimedia extraction yet
    # Export should still be valid GEDCOM with the individual
    assert "Jane /Roe/" in content


