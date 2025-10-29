"""Tests pour la chaîne de middleware - 20 lignes max par fonction"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock
import pytest
from datetime import datetime

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "src" / "python"))

from gwd.adapters.middleware.middleware_chain import MiddlewareHandler, MiddlewareChain, AuthMiddlewareHandler, RobotMiddlewareHandler
from gwd.adapters.middleware.robot_observer import RobotDetector


class MockHandler(MiddlewareHandler):
    """Handler de test"""
    
    def __init__(self, should_pass=True):
        self.called = False
        self.should_pass = should_pass
        
    async def handle(self, request):
        self.called = True
        return self.should_pass


@pytest.mark.asyncio
async def test_middleware_chain_all_pass():
    """Test chaîne avec tous les handlers qui passent"""
    chain = MiddlewareChain()
    
    # Ajouter 3 handlers qui passent tous
    handler1 = MockHandler(True)
    handler2 = MockHandler(True)
    handler3 = MockHandler(True)
    
    chain.add_handler(handler1)
    chain.add_handler(handler2)
    chain.add_handler(handler3)
    
    # Créer une requête mock
    request = MagicMock()
    
    # Exécuter la chaîne
    result = await chain.process(request)
    
    # Vérifier résultats
    assert result is True
    assert handler1.called
    assert handler2.called
    assert handler3.called


@pytest.mark.asyncio
async def test_middleware_chain_second_fails():
    """Test chaîne avec un handler qui échoue"""
    chain = MiddlewareChain()
    
    # Ajouter 3 handlers, le second échoue
    handler1 = MockHandler(True)
    handler2 = MockHandler(False)
    handler3 = MockHandler(True)
    
    chain.add_handler(handler1)
    chain.add_handler(handler2)
    chain.add_handler(handler3)
    
    # Créer une requête mock
    request = MagicMock()
    
    # Exécuter la chaîne
    result = await chain.process(request)
    
    # Vérifier résultats
    assert result is False
    assert handler1.called
    assert handler2.called
    assert not handler3.called  # Le 3ème ne doit pas être appelé


@pytest.mark.asyncio
async def test_robot_middleware_handler():
    """Test handler anti-robot"""
    # Créer le détecteur avec un seuil bas
    detector = RobotDetector(max_requests_per_minute=5)
    
    # Créer le handler
    handler = RobotMiddlewareHandler(detector)
    
    # Créer une requête mock avec headers et client
    request = MagicMock()
    request.client.host = "192.168.1.5"
    request.headers = {}
    request.url.path = "/test"
    
    # Premier appel - devrait passer
    result = await handler.handle(request)
    assert result is True
    
    # Simuler plusieurs requêtes pour dépasser le seuil
    for _ in range(5):
        await handler.handle(request)
    
    # Le prochain appel devrait échouer (IP bloquée)
    result = await handler.handle(request)
    assert result is False
    assert detector.is_blocked("192.168.1.5")
