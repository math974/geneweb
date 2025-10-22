#!/usr/bin/env python3
"""
Tests réels pour les options -k et --sep de GWU.

Ce module teste les options avancées de GWU avec des cas d'usage réels
et vérifie la parité avec le binaire OCaml.
"""

import pytest
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any
import shutil
import os

# Import des fonctions du module gwu_golden
from gwu_golden import cmd_verify, build_scenario_suffix, gwu_extra_args


class TestGwuRealOptions:
    """Tests réels pour les options -k et --sep."""
    
    @pytest.fixture
    def galichet_base(self) -> str:
        """Base de données de test."""
        return "distribution/bases/galichet"
    
    @pytest.fixture
    def dist_dir(self) -> Path:
        """Répertoire de distribution."""
        return Path("distribution")
    
    def test_key_option_real(self, galichet_base: str, dist_dir: Path):
        """Test réel de l'option -k avec des clés spécifiques."""
        # Clés de test réelles de la base galichet
        test_keys = [
            "Jean Pierre.0 Galichet",
            "Marie Elisabeth.0 Loche", 
            "Jean Charles.0 Galichet",
            "Pierre.0 Galichet",
            "Paul.0 Galichet"
        ]
        
        for key in test_keys:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Test avec le binaire Python
                python_output = temp_path / f"python_{key.replace(' ', '_').replace('.', '_')}.gw"
                python_cmd = [
                    "python", "test/run_gwu_python.py",
                    f"{galichet_base}.raw.golden.gw",
                    "-k", key,
                    "-o", str(python_output)
                ]
                
                result = subprocess.run(python_cmd, capture_output=True, text=True)
                assert result.returncode == 0, f"Erreur Python pour clé {key}: {result.stderr}"
                assert python_output.exists(), f"Fichier Python non créé pour clé {key}"
                
                # Vérifier que le fichier n'est pas vide
                content = python_output.read_text()
                assert len(content) > 100, f"Fichier Python trop petit pour clé {key}"
                assert "encoding: utf-8" in content, f"En-tête manquant pour clé {key}"
                # Vérifier que le fichier contient des données de famille
                assert "fam " in content, f"Données de famille manquantes pour clé {key}"
                assert "beg" in content, f"Données d'enfants manquantes pour clé {key}"
    
    def test_sep_option_real(self, galichet_base: str, dist_dir: Path):
        """Test réel de l'option --sep avec des personnes spécifiques."""
        # Personnes de test réelles de la base galichet
        test_persons = [
            "Jean Pierre.0 Galichet",
            "Marie Elisabeth.0 Loche",
            "Jean Charles.0 Galichet"
        ]
        
        for person in test_persons:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Test avec le binaire Python
                python_output_dir = temp_path / "python_separated"
                python_cmd = [
                    "python", "test/run_gwu_python.py",
                    f"{galichet_base}.raw.golden.gw",
                    "--sep", person,
                    "--odir", str(python_output_dir)
                ]
                
                result = subprocess.run(python_cmd, capture_output=True, text=True)
                assert result.returncode == 0, f"Erreur Python pour séparation {person}: {result.stderr}"
                assert python_output_dir.exists(), f"Répertoire Python non créé pour {person}"
                
                # Vérifier que des fichiers ont été générés
                files = list(python_output_dir.glob("*.gw"))
                assert len(files) > 0, f"Aucun fichier généré pour {person}"
                
                # Vérifier le contenu d'un fichier
                if files:
                    content = files[0].read_text()
                    assert len(content) > 30, f"Fichier séparé trop petit pour {person}"
                    assert "encoding: utf-8" in content, f"En-tête manquant pour {person}"
                    # Vérifier que le fichier contient des données valides (personne ou famille)
                    assert ("# " in content or "fam " in content or "beg" in content), f"Données manquantes pour {person}"
    
    def test_key_vs_ocaml_parity(self, galichet_base: str, dist_dir: Path):
        """Test de parité entre Python et OCaml pour l'option -k."""
        test_key = "Jean Pierre.0 Galichet"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Test avec le binaire Python
            python_output = temp_path / "python_key.gw"
            python_cmd = [
                "python", "test/run_gwu_python.py",
                f"{galichet_base}.raw.golden.gw",
                "-k", test_key,
                "--no-notes",
                "-o", str(python_output)
            ]
            
            result = subprocess.run(python_cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Erreur Python: {result.stderr}"
            
            # Test avec le binaire OCaml
            ocaml_output = temp_path / "ocaml_key.gw"
            ocaml_cmd = [
                str(dist_dir / "gw" / "gwu"),
                f"{galichet_base}",
                "-key", test_key,
                "-nnn",
                "-o", str(ocaml_output)
            ]
            
            result = subprocess.run(ocaml_cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Erreur OCaml: {result.stderr}"
            
            # Comparer les fichiers
            assert python_output.exists(), "Fichier Python non créé"
            assert ocaml_output.exists(), "Fichier OCaml non créé"
            
            python_content = python_output.read_text()
            ocaml_content = ocaml_output.read_text()
            
            # Parité stricte: contenus identiques
            assert python_content == ocaml_content, "Les contenus Python et OCaml diffèrent pour -k"
    
    def test_sep_vs_ocaml_parity(self, galichet_base: str, dist_dir: Path):
        """Test de parité entre Python et OCaml pour l'option --sep."""
        test_person = "Jean Pierre.0 Galichet"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Test avec le binaire Python
            python_output_dir = temp_path / "python_separated"
            python_cmd = [
                "python", "test/run_gwu_python.py",
                f"{galichet_base}.raw.golden.gw",
                "--sep", test_person,
                "--no-notes",
                "--odir", str(python_output_dir)
            ]
            
            result = subprocess.run(python_cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Erreur Python: {result.stderr}"
            
            # Test avec le binaire OCaml
            ocaml_output_dir = temp_path / "ocaml_separated"
            ocaml_cmd = [
                str(dist_dir / "gw" / "gwu"),
                f"{galichet_base}",
                "--sep", test_person,
                "-nnn",
                "--odir", str(ocaml_output_dir)
            ]
            
            result = subprocess.run(ocaml_cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Erreur OCaml: {result.stderr}"
            
            # Comparer les répertoires
            assert python_output_dir.exists(), "Répertoire Python non créé"
            assert ocaml_output_dir.exists(), "Répertoire OCaml non créé"
            
            python_files = {p.name: p for p in python_output_dir.glob("*.gw")}
            ocaml_files = {p.name: p for p in ocaml_output_dir.glob("*.gw")}
            assert set(python_files.keys()) == set(ocaml_files.keys()), "Ensembles de fichiers différents entre Python et OCaml"

            # Parité stricte fichier par fichier
            for name in sorted(python_files.keys()):
                python_content = python_files[name].read_text()
                ocaml_content = ocaml_files[name].read_text()
                assert python_content == ocaml_content, f"Contenu différent pour le fichier {name}"
    
    def test_key_combinations(self, galichet_base: str, dist_dir: Path):
        """Test des combinaisons d'options avec -k."""
        test_key = "Jean Pierre.0 Galichet"
        
        combinations = [
            ["-k", test_key, "-nn"],
            ["-k", test_key, "-nnn"],
            ["-k", test_key, "-mem"],
            ["-k", test_key, "--old-gw"],
            ["-k", test_key, "--raw"],
        ]
        
        for combo in combinations:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Test avec le binaire Python
                python_output = temp_path / f"python_{'_'.join(combo[1:])}.gw"
                python_cmd = [
                    "python", "test/run_gwu_python.py",
                    f"{galichet_base}.raw.golden.gw",
                    "-o", str(python_output)
                ] + combo
                
                result = subprocess.run(python_cmd, capture_output=True, text=True)
                assert result.returncode == 0, f"Erreur Python pour combo {combo}: {result.stderr}"
                assert python_output.exists(), f"Fichier Python non créé pour combo {combo}"
                
                # Vérifier le contenu
                content = python_output.read_text()
                assert len(content) > 50, f"Fichier trop petit pour combo {combo}"
                assert "encoding: utf-8" in content, f"En-tête manquant pour combo {combo}"
    
    def test_sep_combinations(self, galichet_base: str, dist_dir: Path):
        """Test des combinaisons d'options avec --sep."""
        test_person = "Jean Pierre.0 Galichet"
        
        combinations = [
            ["--sep", test_person, "-nn"],
            ["--sep", test_person, "-nnn"],
            ["--sep", test_person, "-mem"],
            ["--sep", test_person, "--old-gw"],
            ["--sep", test_person, "--raw"],
        ]
        
        for combo in combinations:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Test avec le binaire Python
                python_output_dir = temp_path / f"python_sep_{'_'.join(combo[1:])}"
                python_cmd = [
                    "python", "test/run_gwu_python.py",
                    f"{galichet_base}.raw.golden.gw",
                    "--odir", str(python_output_dir)
                ] + combo
                
                result = subprocess.run(python_cmd, capture_output=True, text=True)
                assert result.returncode == 0, f"Erreur Python pour combo {combo}: {result.stderr}"
                assert python_output_dir.exists(), f"Répertoire Python non créé pour combo {combo}"
                
                # Vérifier que des fichiers ont été générés
                files = list(python_output_dir.glob("*.gw"))
                assert len(files) > 0, f"Aucun fichier généré pour combo {combo}"
                
                # Vérifier le contenu
                if files:
                    content = files[0].read_text()
                    assert len(content) > 50, f"Fichier trop petit pour combo {combo}"
                    assert "encoding: utf-8" in content, f"En-tête manquant pour combo {combo}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
