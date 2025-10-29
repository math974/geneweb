"""Tests d'intégration pour tous les composants - MAX 20 LIGNES par fonction"""
import sys
import pytest
import tempfile
import os
from pathlib import Path
from unittest import mock

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "python"))

# Import des modules nécessaires pour les tests
from gwd.domain.entities.person import Person
from gwd.domain.entities.family import Family
from gwd.domain.entities.base import GenealogyBase
from gwd.domain.value_objects.auth_result import AuthResult
from gwd.infrastructure.config import Config
from gwd.adapters.middleware.middleware_chain import MiddlewareChain
from gwd.adapters.middleware.robot_observer import RobotDetector


class MockRequest:
    """Mock Request pour les tests"""
    def __init__(self, path="/", client=None, headers=None):
        self.url = type('obj', (object,), {'path': path})
        self.client = client or type('obj', (object,), {'host': '127.0.0.1'})
        self.headers = headers or {}


class MockResponse:
    """Mock Response pour les tests"""
    def __init__(self):
        self.headers = {}
        self.status_code = 200


@pytest.fixture
def complete_workflow_setup():
    """Fixture: Configuration complète pour le workflow"""
    # 1. Créer une configuration temporaire
    temp_dir = tempfile.mkdtemp()
    config = Config(
        bases_dir=temp_dir,
        port=2317,
        host="localhost",
        auth_type="basic",
        wizard_password="wizard123",
        friend_password="friend456",
        debug=True
    )
    
    # 2. Créer une base de test
    jean = Person(id=1, first_name="Jean", surname="Dupont", public_name="Jean-Pierre")
    marie = Person(id=2, first_name="Marie", surname="Martin")
    pierre = Person(id=3, first_name="Pierre", surname="Dupont")
    
    family = Family(id=1, husband_id=1, wife_id=2, children_ids=[3])
    
    base = GenealogyBase(
        name="Famille Dupont",
        persons={1: jean, 2: marie, 3: pierre},
        families={1: family}
    )
    
    # 3. Créer un mock repository
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
    
    repo = MockRepository(base)
    
    # 4. Créer un robot detector
    robot_detector = RobotDetector(max_requests_per_minute=5)
    
    # 5. Créer un objet pour le rendu des templates
    class MockTemplateStrategy:
        def render(self, template_name, context):
            if template_name == "person":
                person = context.get('person')
                return f"<html><body><h1>{person.display_name}</h1></body></html>"
            elif template_name == "base_home":
                return f"<html><body><h1>Base: {context.get('base_name', 'Unknown')}</h1></body></html>"
            return "<html><body><h1>Template</h1></body></html>"
    
    template_strategy = MockTemplateStrategy()
    
    # Nettoyer à la fin des tests
    yield {
        'config': config,
        'base': base,
        'repository': repo,
        'robot_detector': robot_detector,
        'template_strategy': template_strategy,
        'temp_dir': temp_dir
    }
    
    # Nettoyage du répertoire temporaire
    try:
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
    except OSError:
        pass


@pytest.fixture
def auth_middleware():
    """Fixture: Middleware d'authentification pour les tests"""
    class MockAuthMiddlewareHandler:
        def __init__(self):
            self.results = {}  # path -> AuthResult
            
        def add_auth_result(self, path, result):
            self.results[path] = result
            
        async def handle(self, request):
            path = request.url.path
            if path in self.results:
                return self.results[path].is_authenticated
            return True  # Par défaut, autoriser
    
    return MockAuthMiddlewareHandler()


@pytest.fixture
def robot_middleware(complete_workflow_setup):
    """Fixture: Middleware robot pour les tests"""
    class MockRobotMiddlewareHandler:
        def __init__(self, detector):
            self.detector = detector
            
        async def handle(self, request):
            client_ip = request.client.host
            path = request.url.path
            
            self.detector.observe(client_ip, path)
            return not self.detector.is_blocked(client_ip)
    
    return MockRobotMiddlewareHandler(complete_workflow_setup['robot_detector'])


@pytest.mark.asyncio
async def test_complete_workflow_chain(complete_workflow_setup, auth_middleware, robot_middleware):
    """Test d'intégration: Workflow complet avec la chaîne de middleware"""
    # Configuration
    config = complete_workflow_setup['config']
    base = complete_workflow_setup['base']
    repository = complete_workflow_setup['repository']
    
    # Créer la chaîne de middleware
    chain = MiddlewareChain()
    chain.add_handler(auth_middleware)
    chain.add_handler(robot_middleware)
    
    # Simuler des autorisations d'accès
    auth_middleware.add_auth_result("/base/public", AuthResult.success("guest"))
    auth_middleware.add_auth_result("/base/private", AuthResult.failed("unknown"))
    
    # Test 1: Accès autorisé
    request1 = MockRequest("/base/public", 
                           client=type('obj', (object,), {'host': '192.168.1.1'}))
    allowed1 = await chain.process(request1)
    assert allowed1 is True
    
    # Test 2: Accès refusé par auth
    request2 = MockRequest("/base/private", 
                           client=type('obj', (object,), {'host': '192.168.1.2'}))
    allowed2 = await chain.process(request2)
    assert allowed2 is False
    
    # Test 3: Robot détecté et bloqué
    request3 = MockRequest("/base/public", 
                           client=type('obj', (object,), {'host': '192.168.1.3'}))
    
    # Simuler plusieurs requêtes pour déclencher la détection de robot
    for i in range(10):
        robot_middleware.detector.observe("192.168.1.3", f"/test{i}")
    
    # La requête doit être refusée car l'IP est maintenant bloquée
    allowed3 = await chain.process(request3)
    assert allowed3 is False
    assert robot_middleware.detector.is_blocked("192.168.1.3")


@pytest.mark.asyncio
async def test_use_cases_integration(complete_workflow_setup):
    """Test d'intégration: Use cases avec repository et template"""
    from gwd.use_cases.commands import GetPersonCommand, SearchPersonsCommand, RenderPageCommand
    
    repository = complete_workflow_setup['repository']
    template_strategy = complete_workflow_setup['template_strategy']
    
    # 1. Récupérer une personne
    get_person_cmd = GetPersonCommand(repository)
    person = get_person_cmd.execute("test_base", 1)
    
    assert person is not None
    assert person.display_name == "Jean-Pierre Dupont"
    
    # 2. Afficher la personne avec un template
    render_cmd = RenderPageCommand(template_strategy)
    html = render_cmd.execute({
        'template': 'person',
        'person': person
    })
    
    assert "<html>" in html
    assert "Jean-Pierre Dupont" in html
    
    # 3. Rechercher des personnes
    search_cmd = SearchPersonsCommand(repository)
    results = search_cmd.execute("test_base", "Dupont")
    
    assert len(results) == 2
    surnames = [p.surname for p in results]
    assert all(s == "Dupont" for s in surnames)
    
    # 4. Vérifier que les personnes de la recherche sont correctes
    first_names = [p.first_name for p in results]
    assert "Jean" in first_names
    assert "Pierre" in first_names


def test_config_persistence(complete_workflow_setup):
    """Test d'intégration: Persistance de la configuration"""
    config = complete_workflow_setup['config']
    temp_dir = complete_workflow_setup['temp_dir']
    
    # Créer un fichier temporaire pour sauvegarder la config
    config_path = os.path.join(temp_dir, "config.json")
    
    # 1. Sauvegarder la configuration
    config.save_to_file(config_path)
    assert os.path.exists(config_path)
    
    # 2. Charger la configuration
    loaded_config = Config.from_file(config_path)
    
    # 3. Vérifier que les valeurs sont identiques
    assert loaded_config.bases_dir == config.bases_dir
    assert loaded_config.port == config.port
    assert loaded_config.host == config.host
    assert loaded_config.auth_type == config.auth_type
    assert loaded_config.wizard_password == config.wizard_password
    assert loaded_config.friend_password == config.friend_password
    
    # Nettoyage
    os.remove(config_path)
