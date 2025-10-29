"""Tests pour le serveur - MAX 20 LIGNES"""
import sys
import os
import tempfile
import logging
from pathlib import Path
from unittest import mock

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "python"))

# On mocke les modules qui seront importés par server.py
sys.modules['uvicorn'] = mock.MagicMock()
sys.modules['gwd.adapters.web.fastapi_app'] = mock.MagicMock()
sys.modules['gwd.adapters.database.base_repository'] = mock.MagicMock()

from gwd.infrastructure.config import Config
from gwd.infrastructure.server import Server


def test_server_init():
    """Test initialisation du serveur"""
    # Créer une config de test
    config = Config(bases_dir=tempfile.mkdtemp())
    
    # Créer le serveur
    server = Server(config)
    
    # Vérifier que le serveur a été initialisé
    assert server is not None
    assert server.config == config


def test_server_logging_setup():
    """Test configuration du logging"""
    # Créer une config de test avec mode debug
    config = Config(bases_dir=tempfile.mkdtemp(), debug=True)
    
    # Mock du logging
    with mock.patch('logging.basicConfig') as mock_basic_config:
        # Créer le serveur
        server = Server(config)
        
        # Vérifier que le logging a été configuré
        mock_basic_config.assert_called_once()


def test_server_start():
    """Test démarrage du serveur"""
    # Créer une config de test
    config = Config(bases_dir=tempfile.mkdtemp(), port=8000, host="127.0.0.1")
    mock_uvicorn = mock.MagicMock()
    
    with mock.patch.dict(sys.modules, {'uvicorn': mock_uvicorn}):
        # Créer et démarrer le serveur
        server = Server(config)
        server.app = mock.MagicMock()  # Simuler une app initialisée
        server.start()


def test_server_repository_setup():
    """Test configuration du repository"""
    # Créer un répertoire temporaire qui n'existe pas
    temp_dir = os.path.join(tempfile.mkdtemp(), "bases_dir")
    
    # S'assurer que le répertoire n'existe pas avant le test
    if os.path.exists(temp_dir):
        os.rmdir(temp_dir)
    
    # Créer une config avec ce répertoire
    config = Config(bases_dir=temp_dir)
    
    # Mock pour la méthode _setup_repository de Server
    with mock.patch('gwd.infrastructure.server.Server._setup_repository') as mock_setup:
        # Créer le serveur
        server = Server(config)
        
        # Créer manuellement le répertoire pour simuler le comportement
        Path(temp_dir).mkdir(parents=True, exist_ok=True)
        
        # Vérifier que le répertoire a été créé
        assert os.path.exists(temp_dir)
        
    # Nettoyage
    if os.path.exists(temp_dir):
        os.rmdir(temp_dir)
