"""
Configuration pytest pour les tests GWU.
Fixtures communes et configuration des tests.
"""

import pytest
import tempfile
import os
from pathlib import Path
from typing import List, Dict, Any

# Ajouter le chemin du module
import sys
sys.path.insert(0, '/Users/lucasmaelarnassalom/Project/geneweb/geneweb-python/src')

from geneweb.gwu.domain.entities.person import Person
from geneweb.gwu.domain.entities.family import Family
from geneweb.gwu.domain.entities.date import Date
from geneweb.gwu.domain.entities.event import Event
from geneweb.gwu.domain.entities.note import Note
from geneweb.gwu.adapters.output.gw_writer import GwWriterOptions
from geneweb.common.types import Sex, EventType


@pytest.fixture
def sample_person():
    """Personne de test avec données complètes."""
    return Person(
        person_id="P1",
        surname="Dupont",
        first_name="Jean",
        sex=Sex.MALE,
        occ=0,
        birth=Date(15, 1, 1980),  # Corriger l'ordre: jour, mois, année
        death=None,
        notes="Notes de test pour Jean Dupont",
        events=[]
    )


@pytest.fixture
def sample_family():
    """Famille de test avec données complètes."""
    return Family(
        family_id="F1",
        father_id="P1",
        mother_id="P2",
        children=["P3", "P4"],
        marriage=Event(EventType.MARRIAGE, Date(15, 6, 2000)),  # Corriger l'ordre: jour, mois, année
        notes="Notes de famille"
    )


@pytest.fixture
def sample_persons():
    """Liste de personnes de test."""
    return [
        Person(
            person_id="P1",
            surname="Dupont",
            first_name="Jean",
            sex=Sex.MALE,
            occ=0,
            birth=Date(15, 1, 1980),  # Corriger l'ordre: jour, mois, année
            death=None,
            notes="Notes Jean",
            events=[]
        ),
        Person(
            person_id="P2",
            surname="Martin",
            first_name="Marie",
            sex=Sex.FEMALE,
            occ=0,
            birth=Date(20, 3, 1982),  # Corriger l'ordre: jour, mois, année
            death=None,
            notes="Notes Marie",
            events=[]
        ),
        Person(
            person_id="P3",
            surname="Dupont",
            first_name="Pierre",
            sex=Sex.MALE,
            occ=0,
            birth=Date(10, 5, 2010),  # Corriger l'ordre: jour, mois, année
            death=None,
            notes="Notes Pierre",
            events=[]
        )
    ]


@pytest.fixture
def sample_families():
    """Liste de familles de test."""
    return [
        Family(
            family_id="F1",
            father_id="P1",
            mother_id="P2",
            children=["P3"],
            marriage=Event(EventType.MARRIAGE, Date(15, 6, 2000)),  # Corriger l'ordre: jour, mois, année
            notes="Famille Dupont-Martin"
        )
    ]


@pytest.fixture
def gw_writer_options():
    """Options par défaut pour GwWriter."""
    return GwWriterOptions()


@pytest.fixture
def temp_gw_file():
    """Fichier .gw temporaire pour les tests."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.gw', delete=False) as f:
        # Écrire un contenu de test minimal
        f.write("""#gwplus
#encoding utf-8
#charset utf-8
#version 7.0
#base test

notes-db
beg
Notes de base de test
end notes-db

page-ext test1
TITLE=Test Page 1
Content de test

page-ext test2
TITLE=Test Page 2
Autre contenu de test

""")
        temp_file = f.name
    
    yield temp_file
    
    # Nettoyer
    if os.path.exists(temp_file):
        os.unlink(temp_file)


@pytest.fixture
def galichet_gw_file():
    """Fichier galichet.gw pour les tests golden master."""
    return "/Users/lucasmaelarnassalom/Project/geneweb/test/galichet.gw"


@pytest.fixture
def test_data_dir():
    """Répertoire des données de test."""
    return Path("/Users/lucasmaelarnassalom/Project/geneweb/test")


@pytest.fixture
def golden_master_dir():
    """Répertoire des golden masters."""
    return Path("/Users/lucasmaelarnassalom/Project/geneweb/test/golden")


@pytest.fixture
def output_dir():
    """Répertoire de sortie pour les tests."""
    return Path("/tmp/gwu_tests")


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Configuration automatique de l'environnement de test."""
    # Créer le répertoire de sortie
    output_dir = Path("/tmp/gwu_tests")
    output_dir.mkdir(exist_ok=True)
    
    yield
    
    # Nettoyer après les tests
    if output_dir.exists():
        import shutil
        shutil.rmtree(output_dir, ignore_errors=True)
