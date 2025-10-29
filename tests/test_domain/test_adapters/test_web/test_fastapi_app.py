"""Tests pour l'application FastAPI - 20 lignes max par fonction"""
import sys
from pathlib import Path
from typing import Dict, List, Optional
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "src" / "python"))

from gwd.domain.entities.person import Person
from gwd.adapters.database.base_repository import BaseRepository
from gwd.adapters.web.fastapi_app import create_app


class MockConfig:
    """Configuration de test"""
    templates_dir = "tests/templates"
    static_dir = "tests/static"


class MockBaseRepository(BaseRepository):
    """Mock du repository pour les tests"""
    
    def __init__(self):
        self.persons = {
            1: Person(id=1, first_name="Jean", surname="Dupont"),
            2: Person(id=2, first_name="Marie", surname="Martin")
        }
        # Créer une base mock
        self.base = MagicMock()
        self.base.persons_count = 2
        self.base.families_count = 1
        
    def load_base(self, base_name: str):
        return self.base if base_name == "test_base" else None
    
    def get_person_by_id(self, base_name: str, person_id: int) -> Optional[Person]:
        if base_name != "test_base":
            return None
        return self.persons.get(person_id)
    
    def search_persons(self, base_name: str, query: str) -> List[Person]:
        if base_name != "test_base":
            return []
        return [p for p in self.persons.values() 
                if query.lower() in p.first_name.lower() 
                or query.lower() in p.surname.lower()]


def test_home_route():
    """Test route d'accueil"""
    repository = MockBaseRepository()
    app = create_app(MockConfig(), repository)
    client = TestClient(app)
    
    response = client.get("/test_base")
    assert response.status_code == 200
    # La réponse contiendrait normalement du HTML, mais comme
    # nous n'avons pas de vrais templates, on vérifie juste que
    # ce n'est pas une erreur


def test_person_route():
    """Test route personne"""
    repository = MockBaseRepository()
    app = create_app(MockConfig(), repository)
    client = TestClient(app)
    
    response = client.get("/test_base/person/1")
    assert response.status_code == 200
    
    # Personne qui n'existe pas
    response = client.get("/test_base/person/999")
    assert response.status_code == 404


def test_search_route():
    """Test route recherche"""
    repository = MockBaseRepository()
    app = create_app(MockConfig(), repository)
    client = TestClient(app)
    
    response = client.get("/test_base/search?q=Dupont")
    assert response.status_code == 200
