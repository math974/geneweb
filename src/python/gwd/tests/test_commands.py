"""Tests for gwd commands (adapted from tests.py)."""
import pytest
import sys
from pathlib import Path

# Add gwd directory to path for relative imports
gwd_dir = Path(__file__).parent.parent
sys.path.insert(0, str(gwd_dir))

try:
    from domain.entities.person import Person
    from domain.entities.base import GenealogyBase
    from use_cases.commands import GetPersonCommand, SearchPersonsCommand
except ImportError:
    pytest.skip("gwd command modules not available")


class TestCommands:
    """Tests for use case commands."""

    def test_get_person_command(self):
        """Test get person command."""
        # Create a mock repository
        class MockRepository:
            def get_person_by_id(self, base_name, person_id):
                return Person(id=person_id, first_name="Jean", surname="Dupont")

        repository = MockRepository()
        command = GetPersonCommand(base_name="test_base", person_id=1, repository=repository)
        result = command.execute()

        assert result is not None
        assert result.id == 1
        assert result.display_name == "Jean Dupont"

    def test_search_persons_command(self):
        """Test search persons command."""
        # Create a mock repository
        class MockRepository:
            def search_persons(self, base_name, query):
                if "Dupont" in query:
                    return [
                        Person(id=1, first_name="Jean", surname="Dupont"),
                        Person(id=2, first_name="Marie", surname="Dupont")
                    ]
                elif "Jean" in query:
                    return [Person(id=1, first_name="Jean", surname="Dupont")]
                return []

        repository = MockRepository()

        # Search by surname
        command = SearchPersonsCommand(base_name="test_base", query="Dupont", repository=repository)
        results = command.execute()

        assert len(results) == 2
        assert any(p.id == 1 for p in results)
        assert any(p.id == 2 for p in results)

        # Search by first name
        command = SearchPersonsCommand(base_name="test_base", query="Jean", repository=repository)
        results = command.execute()

        assert len(results) == 1
        assert results[0].id == 1

