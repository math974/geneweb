"""Tests pour l'entité Person - 20 lignes max par fonction"""
import pytest
import sys
from pathlib import Path
from datetime import date

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src" / "python"))

from gwd.domain.entities.person import Person

def test_person_creation():
    """Test création d'une personne"""
    person = Person(
        id=1,
        first_name="Jean",
        surname="Dupont",
        birth=date(1950, 1, 1)
    )
    assert person.id == 1
    assert person.first_name == "Jean"
    assert person.surname == "Dupont"

def test_person_display_name():
    """Test nom d'affichage"""
    person = Person(
        id=1,
        first_name="Jean",
        surname="Dupont",
        public_name="Jacques"
    )
    assert person.display_name == "Jacques Dupont"

def test_person_display_name_no_public():
    """Test nom d'affichage sans nom public"""
    person = Person(id=1, first_name="Jean", surname="Dupont")
    assert person.display_name == "Jean Dupont"

def test_person_age_at_death():
    """Test calcul âge au décès"""
    person = Person(
        id=1,
        first_name="Jean",
        surname="Dupont",
        birth=date(1950, 1, 1),
        death=date(2020, 1, 1)
    )
    assert person.age_at_death == 70

def test_person_age_at_death_none():
    """Test âge au décès si pas décédé"""
    person = Person(
        id=1,
        first_name="Jean",
        surname="Dupont",
        birth=date(1950, 1, 1)
    )
    assert person.age_at_death is None

