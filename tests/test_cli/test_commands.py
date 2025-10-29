"""Tests pour les commandes CLI - MAX 20 LIGNES par fonction"""
import sys
import pytest
import os
import tempfile
from pathlib import Path
from unittest import mock
from click.testing import CliRunner

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "python"))

# Importer le CLI à tester
from gwd.cli.main import cli, serve, list_bases, info, search, version


@pytest.fixture
def runner():
    """Fixture: CliRunner pour les tests"""
    return CliRunner()


@pytest.fixture
def mock_server():
    """Fixture: Mock pour Server"""
    server = mock.MagicMock()
    return server


@pytest.fixture
def mock_config():
    """Fixture: Mock pour Config"""
    with mock.patch('gwd.cli.main.Config') as mock_config:
        mock_config_instance = mock.MagicMock()
        mock_config.return_value = mock_config_instance
        yield mock_config


@pytest.fixture
def mock_repository():
    """Fixture: Mock pour MessagePackBaseRepository"""
    with mock.patch('gwd.cli.main.MessagePackBaseRepository') as mock_repo:
        mock_repo_instance = mock.MagicMock()
        mock_repo.return_value = mock_repo_instance
        yield mock_repo, mock_repo_instance


def test_cli_version(runner):
    """Test commande version"""
    result = runner.invoke(version)
    assert result.exit_code == 0
    assert "GeneWeb GWD Python" in result.output
    assert "v1.0.0" in result.output


def test_cli_serve(runner, mock_server, mock_config):
    """Test commande serve"""
    with mock.patch('gwd.cli.main.Server', return_value=mock_server):
        result = runner.invoke(serve, ['--bases-dir', '/test/bases'])
        
        assert result.exit_code == 0
        assert "Démarrage" in result.output
        mock_config.assert_called_once_with(
            bases_dir='/test/bases',
            port=2317,
            host='localhost',
            debug=False
        )
        mock_server.start.assert_called_once()


def test_cli_list_bases(runner):
    """Test commande list_bases"""
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Créer des fichiers test
        open(os.path.join(tmpdirname, "test1.msgpack"), 'a').close()
        open(os.path.join(tmpdirname, "test2.msgpack"), 'a').close()
        open(os.path.join(tmpdirname, "ignore.txt"), 'a').close()
        
        result = runner.invoke(list_bases, [tmpdirname])
        
        assert result.exit_code == 0
        assert "test1" in result.output
        assert "test2" in result.output
        assert "ignore" not in result.output


def test_cli_info(runner, mock_repository):
    """Test commande info"""
    mock_repo, mock_repo_instance = mock_repository
    
    # Mock pour base
    mock_base = mock.MagicMock()
    mock_base.name = "Test Base"
    mock_base.persons_count = 10
    mock_base.families_count = 5
    
    mock_repo_instance.load_base.return_value = mock_base
    
    result = runner.invoke(info, ["testbase", "--bases-dir", "/test/bases"])
    
    assert result.exit_code == 0
    assert "Test Base" in result.output
    assert "Personnes: 10" in result.output
    assert "Familles: 5" in result.output
    mock_repo.assert_called_once_with("/test/bases")
    mock_repo_instance.load_base.assert_called_once_with("testbase")


def test_cli_info_not_found(runner, mock_repository):
    """Test commande info avec base non trouvée"""
    mock_repo, mock_repo_instance = mock_repository
    mock_repo_instance.load_base.return_value = None
    
    result = runner.invoke(info, ["nonexistent", "--bases-dir", "/test/bases"])
    
    assert result.exit_code == 0
    assert "non trouvée" in result.output
    mock_repo_instance.load_base.assert_called_once_with("nonexistent")


def test_cli_search(runner, mock_repository):
    """Test commande search"""
    mock_repo, mock_repo_instance = mock_repository
    
    # Mock pour SearchPersonsCommand
    mock_cmd = mock.MagicMock()
    mock_cmd.execute.return_value = [
        mock.MagicMock(display_name="Jean Dupont"),
        mock.MagicMock(display_name="Pierre Dupont")
    ]
    
    with mock.patch('gwd.cli.main.SearchPersonsCommand', return_value=mock_cmd):
        result = runner.invoke(search, ["testbase", "Dupont", "--bases-dir", "/test/bases"])
        
        assert result.exit_code == 0
        assert "Recherche 'Dupont'" in result.output
        assert "Jean Dupont" in result.output
        assert "Pierre Dupont" in result.output
        assert "2 résultats" in result.output
        mock_cmd.execute.assert_called_once_with("testbase", "Dupont")


def test_cli_search_no_results(runner, mock_repository):
    """Test commande search sans résultats"""
    mock_repo, mock_repo_instance = mock_repository
    
    # Mock pour SearchPersonsCommand
    mock_cmd = mock.MagicMock()
    mock_cmd.execute.return_value = []
    
    with mock.patch('gwd.cli.main.SearchPersonsCommand', return_value=mock_cmd):
        result = runner.invoke(search, ["testbase", "Unknown", "--bases-dir", "/test/bases"])
        
        assert result.exit_code == 0
        assert "Aucun résultat" in result.output
