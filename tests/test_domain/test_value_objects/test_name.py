"""Tests pour le value object Name - 20 lignes max par fonction"""
import pytest
import sys
from pathlib import Path

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src" / "python"))

from gwd.domain.value_objects.name import Name

def test_name_creation():
    """Test création d'un nom"""
    name = Name(first_name="Jean", surname="Dupont")
    assert name.first_name == "Jean"
    assert name.surname == "Dupont"

def test_name_display_with_public_name():
    """Test nom d'affichage avec nom public"""
    name = Name(first_name="Jean", surname="Dupont", public_name="Jacques")
    assert name.display_name == "Jacques Dupont"

def test_name_display_without_public_name():
    """Test nom d'affichage sans nom public"""
    name = Name(first_name="Jean", surname="Dupont")
    assert name.display_name == "Jean Dupont"

def test_name_str_representation():
    """Test représentation string"""
    name = Name(first_name="Jean", surname="Dupont")
    assert str(name) == "Jean Dupont"

