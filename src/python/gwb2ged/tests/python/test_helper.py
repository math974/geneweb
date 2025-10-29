"""Helper functions for gwb2ged tests"""

import os
from pathlib import Path
from tools.test_utils import get_absolute_path


def get_fixture_path(filename: str) -> str:
    """
    Get path to a GEDCOM fixture file.

    Args:
        filename: Name of the fixture file (e.g., 'test_selection_key.ged')

    Returns:
        Absolute path to the fixture file
    """
    fixtures_dir = get_absolute_path("src/python/fixtures/gedcom")
    fixture_path = os.path.join(fixtures_dir, filename)

    if not os.path.exists(fixture_path):
        raise FileNotFoundError(
            f"Fixture file not found: {fixture_path}\n"
            f"Please ensure the fixture file exists in {fixtures_dir}"
        )

    return fixture_path

