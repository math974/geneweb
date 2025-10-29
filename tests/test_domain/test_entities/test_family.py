"""Tests pour l'entité Family - 20 lignes max par fonction"""
import pytest
import sys
from pathlib import Path
from datetime import date

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src" / "python"))

from gwd.domain.entities.family import Family

def test_family_creation():
    """Test création d'une famille"""
    family = Family(id=1, husband_id=1, wife_id=2)
    assert family.id == 1
    assert family.husband_id == 1
    assert family.wife_id == 2

def test_family_add_child():
    """Test ajout d'enfant à une famille"""
    family = Family(id=1, husband_id=1, wife_id=2, children_ids=[])
    family.add_child(3)
    assert 3 in family.children_ids
    assert family.get_children_count() == 1

def test_family_add_child_duplicate():
    """Test ajout d'enfant en double"""
    family = Family(id=1, children_ids=[3])
    family.add_child(3)
    assert family.get_children_count() == 1

def test_family_is_complete():
    """Test famille complète"""
    family = Family(id=1, husband_id=1, wife_id=2)
    assert family.is_complete()

def test_family_not_complete():
    """Test famille incomplète"""
    family = Family(id=1, husband_id=1)
    assert not family.is_complete()

def test_family_is_married():
    """Test couple marié"""
    family = Family(id=1, marriage_date=date(2000, 1, 1))
    assert family.is_married

def test_family_is_divorced():
    """Test couple divorcé"""
    family = Family(id=1, divorce_date=date(2010, 1, 1))
    assert family.is_divorced

