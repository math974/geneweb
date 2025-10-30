"""Tests for gwd entities (adapted from tests.py)."""
import pytest
import sys
from pathlib import Path

# Add gwd directory to path for relative imports
gwd_dir = Path(__file__).parent.parent
sys.path.insert(0, str(gwd_dir))

try:
    from domain.entities.person import Person
    from domain.entities.family import Family
    from domain.entities.base import GenealogyBase
except ImportError:
    pytest.skip("gwd domain entities not available")


class TestEntities:
    """Tests for domain entities."""

    def test_person_creation(self):
        """Test person creation."""
        person = Person(id=1, first_name="Jean", surname="Dupont")
        assert person.id == 1
        assert person.display_name == "Jean Dupont"

    def test_person_public_name(self):
        """Test person public name."""
        person = Person(id=1, first_name="Jean", surname="Dupont", public_name="Jean-Pierre")
        assert person.display_name == "Jean-Pierre Dupont"

    def test_family_creation(self):
        """Test family creation."""
        family = Family(id=1, husband_id=1, wife_id=2)
        assert family.id == 1
        assert family.husband_id == 1
        assert family.wife_id == 2

    def test_base_creation(self):
        """Test base creation."""
        person = Person(id=1, first_name="Jean", surname="Dupont")
        family = Family(id=1, husband_id=1, wife_id=2)
        base = GenealogyBase(
            name="Test Base",
            path="/test",
            persons={1: person},
            families={1: family},
            last_modified="2024-01-01"
        )
        assert base.name == "Test Base"
        assert base.persons_count == 1
        assert base.families_count == 1

