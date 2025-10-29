"""Tests d'intégration de l'application complète - MAX 20 LIGNES par fonction"""
import sys
import pytest
from pathlib import Path
from unittest import mock

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "python"))

# Import des modules nécessaires pour les tests
from gwd.domain.entities.person import Person
from gwd.domain.entities.family import Family
from gwd.domain.entities.base import GenealogyBase
from gwd.domain.services.auth_factory import AuthStrategyFactory
from gwd.use_cases.commands import GetPersonCommand, SearchPersonsCommand, RenderPageCommand
from gwd.infrastructure.config import Config
from gwd.adapters.web.template_strategies import TemplateStrategy


@pytest.fixture
def genealogy_base():
    """Fixture: Création d'une base généalogique de test"""
    # Créer des personnes
    jean = Person(id=1, first_name="Jean", surname="Dupont", public_name="Jean-Pierre")
    marie = Person(id=2, first_name="Marie", surname="Martin")
    pierre = Person(id=3, first_name="Pierre", surname="Dupont")
    
    # Créer une famille
    family = Family(id=1, husband_id=1, wife_id=2, children_ids=[3])
    
    # Créer la base
    base = GenealogyBase(
        name="Famille Dupont",
        persons={1: jean, 2: marie, 3: pierre},
        families={1: family}
    )
    
    return base


@pytest.fixture
def mock_repository(genealogy_base):
    """Fixture: Repository mock pour les tests"""
    class MockRepository:
        def __init__(self, base):
            self.base = base
        
        def get_person_by_id(self, base_name, person_id):
            return self.base.get_person(person_id)
        
        def search_persons(self, base_name, query):
            query_lower = query.lower()
            return [
                p for p in self.base.persons.values()
                if query_lower in p.first_name.lower() or query_lower in p.surname.lower()
            ]
            
        def load_base(self, base_name):
            return self.base
    
    return MockRepository(genealogy_base)


@pytest.fixture
def mock_template_strategy():
    """Fixture: Template strategy mock pour les tests"""
    class MockTemplateStrategy(TemplateStrategy):
        def render(self, template_name, context):
            if template_name == "person":
                person = context.get('person')
                return f"<html><body><h1>{person.display_name}</h1></body></html>"
            elif template_name == "base_home":
                return f"<html><body><h1>Base: {context.get('base_name', 'Unknown')}</h1></body></html>"
            elif template_name == "search_results":
                results = context.get('results', [])
                count = len(results)
                return f"<html><body><h1>Résultats: {count}</h1></body></html>"
            return f"<html><body><h1>Template: {template_name}</h1></body></html>"
    
    return MockTemplateStrategy()


@pytest.fixture
def auth_factory():
    """Fixture: Factory d'authentification pour les tests"""
    return AuthStrategyFactory("wizard123", "friend456")


def test_integration_person_access(genealogy_base, mock_repository, mock_template_strategy):
    """Test d'intégration: Accès à une personne"""
    # 1. Obtenir une personne via le use case
    get_cmd = GetPersonCommand(mock_repository)
    person = get_cmd.execute("test_base", 1)
    
    assert person is not None
    assert person.id == 1
    assert person.display_name == "Jean-Pierre Dupont"
    
    # 2. Générer la page HTML pour cette personne
    render_cmd = RenderPageCommand(mock_template_strategy)
    html = render_cmd.execute({
        'template': 'person',
        'person': person,
        'base_name': 'test_base'
    })
    
    assert html is not None
    assert "<html>" in html
    assert "Jean-Pierre Dupont" in html


def test_integration_search(genealogy_base, mock_repository, mock_template_strategy):
    """Test d'intégration: Recherche de personnes"""
    # 1. Rechercher des personnes via le use case
    search_cmd = SearchPersonsCommand(mock_repository)
    results = search_cmd.execute("test_base", "Jean")
    
    assert len(results) == 1
    assert results[0].display_name == "Jean-Pierre Dupont"
    
    # 2. Générer la page de résultats HTML
    render_cmd = RenderPageCommand(mock_template_strategy)
    html = render_cmd.execute({
        'template': 'search_results',
        'query': 'Jean',
        'results': results,
        'count': len(results),
        'base_name': 'test_base'
    })
    
    assert html is not None
    assert "<html>" in html
    assert "Résultats: 1" in html


def test_integration_authentication(auth_factory):
    """Test d'intégration: Authentification"""
    import base64
    
    # 1. Test d'authentification wizard
    wizard_creds = base64.b64encode(b"admin:wizard123").decode()
    wizard_result = auth_factory.authenticate("basic", wizard_creds)
    
    assert wizard_result.is_authenticated
    assert wizard_result.is_wizard
    
    # 2. Test d'authentification friend
    friend_creds = base64.b64encode(b"user:friend456").decode()
    friend_result = auth_factory.authenticate("basic", friend_creds)
    
    assert friend_result.is_authenticated
    assert friend_result.is_friend
    
    # 3. Test d'authentification échec
    fail_creds = base64.b64encode(b"user:wrong").decode()
    fail_result = auth_factory.authenticate("basic", fail_creds)
    
    assert not fail_result.is_authenticated


def test_integration_config_repository(genealogy_base, mock_repository, tmp_path):
    """Test d'intégration: Configuration et Repository"""
    # 1. Créer une configuration
    config = Config(
        bases_dir=str(tmp_path),
        port=2317,
        host="localhost",
        auth_type="basic",
        wizard_password="wizard123",
        friend_password="friend456"
    )
    
    assert config.bases_dir == str(tmp_path)
    assert config.port == 2317
    
    # 2. Simuler le chargement d'une base depuis le repository
    base = mock_repository.load_base("test_base")
    
    assert base is not None
    assert base.name == "Famille Dupont"
    assert base.persons_count == 3
    assert base.families_count == 1


@mock.patch('gwd.adapters.middleware.robot_observer.datetime')
def test_integration_robot_protection(mock_datetime):
    """Test d'intégration: Protection contre les robots"""
    from gwd.adapters.middleware.robot_observer import RobotDetector
    from datetime import datetime, timedelta
    
    # Simuler le temps pour les tests
    current_time = datetime(2023, 1, 1, 12, 0, 0)
    mock_datetime.now.return_value = current_time
    
    # Créer un détecteur avec une limite basse pour les tests
    detector = RobotDetector(max_requests_per_minute=5)
    
    # Test utilisateur normal (pas assez de requêtes pour être bloqué)
    for i in range(5):
        detector.observe("192.168.1.1", f"/test{i}")
    
    assert not detector.is_blocked("192.168.1.1")
    
    # Test robot (trop de requêtes en peu de temps)
    for i in range(10):
        detector.observe("192.168.1.100", f"/test{i}")
    
    assert detector.is_blocked("192.168.1.100")
    assert detector.is_suspicious("192.168.1.100")
    
    # Test de réinitialisation après une période
    mock_datetime.now.return_value = current_time + timedelta(minutes=2)
    detector.observe("192.168.1.100", "/test_new")
    
    assert not detector.is_blocked("192.168.1.100")
