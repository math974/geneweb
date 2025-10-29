"""Tests pour l'entité GenealogyBase - 20 lignes max par fonction"""
import pytest
import sys
from pathlib import Path
from datetime import date

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src" / "python"))

from gwd.domain.entities.base import GenealogyBase
from gwd.domain.entities.person import Person
from gwd.domain.entities.family import Family

def test_base_creation():
    """Test création d'une base"""
    base = GenealogyBase(name="test")
    assert base.name == "test"
    assert base.persons_count == 0
    assert base.families_count == 0

def test_base_add_person():
    """Test ajout d'une personne"""
    base = GenealogyBase(name="test")
    person = Person(1, "Jean", "Dupont")
    base.add_person(person)
    assert base.persons_count == 1

def test_base_get_person():
    """Test récupération d'une personne"""
    base = GenealogyBase(name="test")
    person = Person(1, "Jean", "Dupont")
    base.add_person(person)
    retrieved = base.get_person(1)
    assert retrieved is not None
    assert retrieved.first_name == "Jean"

def test_base_search_persons():
    """Test recherche de personnes"""
    base = GenealogyBase(name="test")
    base.add_person(Person(1, "Jean", "Dupont"))
    base.add_person(Person(2, "Marie", "Martin"))
    results = base.search_persons("Dupont")
    assert len(results) == 1
    assert results[0].surname == "Dupont"

def test_base_search_persons_multiple():
    """Test recherche avec plusieurs résultats"""
    base = GenealogyBase(name="test")
    base.add_person(Person(1, "Jean", "Dupont"))
    base.add_person(Person(2, "Jean", "Martin"))
    results = base.search_persons("Jean")
    assert len(results) == 2

def test_base_add_family():
    """Test ajout d'une famille"""
    base = GenealogyBase(name="test")
    family = Family(id=1)
    base.add_family(family)
    assert base.families_count == 1

def test_base_get_family():
    """Test récupération d'une famille"""
    base = GenealogyBase(name="test")
    family = Family(id=1)
    base.add_family(family)
    retrieved = base.get_family(1)
    assert retrieved is not None
    assert retrieved.id == 1

