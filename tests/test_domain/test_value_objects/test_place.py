"""Tests pour le value object Place - 20 lignes max par fonction"""
import pytest
import sys
from pathlib import Path

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src" / "python"))

from gwd.domain.value_objects.place import Place

def test_place_creation():
    """Test création d'un lieu"""
    place = Place(city="Paris", region="Île-de-France", country="France")
    assert place.city == "Paris"
    assert place.region == "Île-de-France"

def test_place_full_place():
    """Test lieu complet"""
    place = Place(city="Paris", region="Île-de-France", country="France")
    assert place.full_place == "Paris, Île-de-France, France"

def test_place_short_place():
    """Test lieu court"""
    place = Place(city="Paris")
    assert place.short_place == "Paris"

def test_place_str_representation():
    """Test représentation string"""
    place = Place(city="Paris", country="France")
    assert str(place) == "Paris, France"

