"""
Tests d'intégration pour l'interface CLI.
"""

import pytest
import subprocess
import tempfile
import os
from pathlib import Path
from geneweb.gwu.cli.gwu_cli import GwuCLI


class TestGwuCLI:
    """Tests d'intégration pour GwuCLI."""
    
    def test_cli_help(self):
        """Test de l'aide CLI."""
        result = subprocess.run([
            "python", "-m", "geneweb.gwu", "--help"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower()
        assert "gwu" in result.stdout.lower()
    
    def test_cli_version(self):
        """Test de la version CLI."""
        result = subprocess.run([
            "python", "-m", "geneweb.gwu", "--version"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "version" in result.stdout.lower()
    
    def test_cli_export_database(self, galichet_gw_file):
        """Test d'export de base de données via CLI."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            output_file = f.name
        
        try:
            result = subprocess.run([
                "python", "-m", "geneweb.gwu",
                "--database", galichet_gw_file,
                "--output", output_file
            ], capture_output=True, text=True)
            
            assert result.returncode == 0, f"Erreur CLI: {result.stderr}"
            assert os.path.exists(output_file)
            
            # Vérifier le contenu
            with open(output_file, 'r') as f:
                content = f.read()
            
            assert "#gwplus" in content
            assert "#encoding" in content
            assert "#charset" in content
            assert "#version" in content
            assert "#base" in content
            
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_cli_export_selection(self, galichet_gw_file):
        """Test d'export de sélection via CLI."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            output_file = f.name
        
        try:
            result = subprocess.run([
                "python", "-m", "geneweb.gwu",
                "--database", galichet_gw_file,
                "--output", output_file,
                "--selection", "P1"
            ], capture_output=True, text=True)
            
            assert result.returncode == 0, f"Erreur CLI: {result.stderr}"
            assert os.path.exists(output_file)
            
            # Vérifier le contenu
            with open(output_file, 'r') as f:
                content = f.read()
            
            assert "#gwplus" in content
            assert "#encoding" in content
            assert "#charset" in content
            assert "#version" in content
            assert "#base" in content
            
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_cli_export_separated(self, galichet_gw_file):
        """Test d'export séparé via CLI."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run([
                "python", "-m", "geneweb.gwu",
                "--database", galichet_gw_file,
                "--output-dir", temp_dir,
                "--separated"
            ], capture_output=True, text=True)
            
            assert result.returncode == 0, f"Erreur CLI: {result.stderr}"
            
            # Vérifier que des fichiers ont été créés
            files = list(Path(temp_dir).glob("*.gw"))
            assert len(files) > 0
    
    def test_cli_invalid_database(self):
        """Test avec une base de données invalide."""
        result = subprocess.run([
            "python", "-m", "geneweb.gwu",
            "--database", "/nonexistent/file.gw",
            "--output", "/tmp/test.gw"
        ], capture_output=True, text=True)
        
        assert result.returncode != 0
        assert "error" in result.stderr.lower() or "not found" in result.stderr.lower()
    
    def test_cli_missing_arguments(self):
        """Test avec des arguments manquants."""
        result = subprocess.run([
            "python", "-m", "geneweb.gwu"
        ], capture_output=True, text=True)
        
        assert result.returncode != 0
        assert "error" in result.stderr.lower() or "required" in result.stderr.lower()
    
    def test_cli_verbose_mode(self, galichet_gw_file):
        """Test du mode verbose."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            output_file = f.name
        
        try:
            result = subprocess.run([
                "python", "-m", "geneweb.gwu",
                "--database", galichet_gw_file,
                "--output", output_file,
                "--verbose"
            ], capture_output=True, text=True)
            
            assert result.returncode == 0, f"Erreur CLI: {result.stderr}"
            assert os.path.exists(output_file)
            
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_cli_no_events_option(self, galichet_gw_file):
        """Test de l'option --no-events."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            output_file = f.name
        
        try:
            result = subprocess.run([
                "python", "-m", "geneweb.gwu",
                "--database", galichet_gw_file,
                "--output", output_file,
                "--no-events"
            ], capture_output=True, text=True)
            
            assert result.returncode == 0, f"Erreur CLI: {result.stderr}"
            assert os.path.exists(output_file)
            
            # Vérifier que les événements ne sont pas présents
            with open(output_file, 'r') as f:
                content = f.read()
            
            assert "pevt " not in content
            assert "#birt" not in content
            assert "#deat" not in content
            
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_cli_no_notes_option(self, galichet_gw_file):
        """Test de l'option --no-notes."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            output_file = f.name
        
        try:
            result = subprocess.run([
                "python", "-m", "geneweb.gwu",
                "--database", galichet_gw_file,
                "--output", output_file,
                "--no-notes"
            ], capture_output=True, text=True)
            
            assert result.returncode == 0, f"Erreur CLI: {result.stderr}"
            assert os.path.exists(output_file)
            
            # Vérifier que les notes ne sont pas présentes
            with open(output_file, 'r') as f:
                content = f.read()
            
            assert "notes " not in content
            assert "beg" not in content
            assert "end notes" not in content
            
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
