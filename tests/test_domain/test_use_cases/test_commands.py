"""Tests pour les commandes (Command Pattern) - 20 lignes max par fonction"""
import sys
from pathlib import Path
from typing import Optional, List, Dict
from unittest.mock import MagicMock

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src" / "python"))

from gwd.domain.entities.person import Person
from gwd.adapters.database.base_repository import BaseRepository
from gwd.use_cases.commands import GetPersonCommand, SearchPersonsCommand, RenderPageCommand


class MockRepository(BaseRepository):
    """Repository de test pour les commandes"""
    
    def __init__(self):
        self.person = Person(id=1, first_name="Jean", surname="Dupont")
    
    def load_base(self, base_name: str):
        return MagicMock()
    
    def get_person_by_id(self, base_name: str, person_id: int) -> Optional[Person]:
        return self.person if person_id == 1 else None
    
    def search_persons(self, base_name: str, query: str) -> List[Person]:
        return [self.person] if "Dup" in query else []


class MockTemplateStrategy:
    """Stratégie de template de test"""
    
    def render(self, template_name: str, context: Dict) -> str:
        return f"Rendered {template_name} with {len(context)} context items"


def test_get_person_command():
    """Test GetPersonCommand"""
    repository = MockRepository()
    command = GetPersonCommand(repository)
    person = command.execute("base1", 1)
    assert person is not None
    assert person.first_name == "Jean"
    assert person.surname == "Dupont"


def test_get_person_command_not_found():
    """Test GetPersonCommand avec ID inexistant"""
    repository = MockRepository()
    command = GetPersonCommand(repository)
    person = command.execute("base1", 2)
    assert person is None


def test_search_persons_command():
    """Test SearchPersonsCommand"""
    repository = MockRepository()
    command = SearchPersonsCommand(repository)
    results = command.execute("base1", "Dupont")
    assert len(results) == 1
    assert results[0].surname == "Dupont"


def test_search_persons_command_no_results():
    """Test SearchPersonsCommand sans résultats"""
    repository = MockRepository()
    command = SearchPersonsCommand(repository)
    results = command.execute("base1", "Martin")
    assert len(results) == 0


def test_render_page_command():
    """Test RenderPageCommand"""
    template_strategy = MockTemplateStrategy()
    command = RenderPageCommand(template_strategy)
    html = command.execute({"name": "Jean", "template": "person"})
    assert html == "Rendered person with 2 context items"


def test_render_page_command_default_template():
    """Test RenderPageCommand avec template par défaut"""
    template_strategy = MockTemplateStrategy()
    command = RenderPageCommand(template_strategy)
    html = command.execute({"name": "Jean"})
    assert html == "Rendered base with 1 context items"
