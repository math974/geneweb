"""Tests pour la configuration - MAX 20 LIGNES"""
import sys
import os
import json
import tempfile
from pathlib import Path
from unittest import mock

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "python"))

from gwd.infrastructure.config import Config


def test_config_default_values():
    """Test des valeurs par défaut de la configuration"""
    config = Config(bases_dir="./bases")
    assert config.bases_dir == "./bases"
    assert config.port == 2317
    assert config.host == "localhost"
    assert config.auth_type == "basic"
    assert config.debug is False


def test_config_from_env():
    """Test du chargement depuis les variables d'environnement"""
    with mock.patch.dict(os.environ, {
        "BASES_DIR": "/tmp/bases",
        "PORT": "8080",
        "HOST": "0.0.0.0",
        "AUTH_TYPE": "digest",
        "DEBUG": "true"
    }):
        config = Config.from_env()
        assert config.bases_dir == "/tmp/bases"
        assert config.port == 8080
        assert config.host == "0.0.0.0"
        assert config.auth_type == "digest"
        assert config.debug is True


def test_config_to_dict():
    """Test de la conversion en dictionnaire"""
    config = Config(
        bases_dir="./test_bases",
        port=8000,
        host="127.0.0.1",
        auth_type="digest"
    )
    
    config_dict = config.to_dict()
    assert config_dict["bases_dir"] == "./test_bases"
    assert config_dict["port"] == 8000
    assert config_dict["host"] == "127.0.0.1"
    assert config_dict["auth_type"] == "digest"


def test_config_save_and_load():
    """Test de la sauvegarde et du chargement depuis un fichier"""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # Créer et sauvegarder la configuration
        original_config = Config(
            bases_dir="./save_test",
            port=9000,
            host="example.com"
        )
        original_config.save_to_file(tmp_path)
        
        # Charger la configuration
        loaded_config = Config.from_file(tmp_path)
        
        # Vérifier
        assert loaded_config.bases_dir == "./save_test"
        assert loaded_config.port == 9000
        assert loaded_config.host == "example.com"
    finally:
        # Nettoyer le fichier temporaire
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
