"""
Tests unitaires pour les entités du domaine.
"""

import pytest
from geneweb.gwu.domain.entities.person import Person
from geneweb.gwu.domain.entities.family import Family
from geneweb.gwu.domain.entities.date import Date
from geneweb.gwu.domain.entities.event import Event
from geneweb.gwu.domain.entities.note import Note
from geneweb.common.types import Sex, EventType


class TestPerson:
    """Tests pour l'entité Person."""
    
    def test_person_creation(self):
        """Test de création d'une personne."""
        person = Person(
            person_id="P1",
            surname="Dupont",
            first_name="Jean",
            sex=Sex.MALE,
            occ=0,
            birth=Date(15, 1, 1980),  # Corriger l'ordre: jour, mois, année
            death=None,
            notes="Notes de test",
            events=[]
        )
        
        assert person.person_id == "P1"
        assert person.surname == "Dupont"
        assert person.first_name == "Jean"
        assert person.sex == Sex.MALE
        assert person.occ == 0
        assert person.birth == Date(15, 1, 1980)
        assert person.death is None
        assert person.notes == "Notes de test"
        assert person.events == []
    
    def test_person_has_notes(self):
        """Test de la méthode has_notes."""
        person_with_notes = Person(
            person_id="P1", surname="Dupont", first_name="Jean", sex=Sex.MALE, occ=0,
            birth=None, death=None, notes="Notes", events=[]
        )
        
        person_without_notes = Person(
            person_id="P2", surname="Martin", first_name="Marie", sex=Sex.FEMALE, occ=0,
            birth=None, death=None, notes="", events=[]
        )
        
        assert person_with_notes.has_notes() is True
        assert person_without_notes.has_notes() is False
    
    def test_person_has_events(self):
        """Test de la méthode has_events."""
        person_with_events = Person(
            person_id="P1", surname="Dupont", first_name="Jean", sex=Sex.MALE, occ=0,
            birth=None, death=None, notes="", events=[Event("bapt", Date(20, 1, 1980))]
        )
        
        person_without_events = Person(
            person_id="P2", surname="Martin", first_name="Marie", sex=Sex.FEMALE, occ=0,
            birth=None, death=None, notes="", events=[]
        )
        
        assert person_with_events.has_events() is True
        assert person_without_events.has_events() is False


class TestFamily:
    """Tests pour l'entité Family."""
    
    def test_family_creation(self):
        """Test de création d'une famille."""
        family = Family(
            family_id="F1",
            father_id="P1",
            mother_id="P2",
            children=["P3", "P4"],
            marriage=Event(EventType.MARRIAGE, Date(15, 6, 2000)),
            notes="Notes de famille"
        )
        
        assert family.family_id == "F1"
        assert family.father_id == "P1"
        assert family.mother_id == "P2"
        assert family.children == ["P3", "P4"]
        assert family.marriage == Event(EventType.MARRIAGE, Date(15, 6, 2000))
        assert family.notes == "Notes de famille"
    
    def test_family_has_notes(self):
        """Test de la méthode has_notes."""
        family_with_notes = Family(
            family_id="F1", father_id="P1", mother_id="P2", children=[],
            marriage=None, notes="Notes de famille"
        )
        
        family_without_notes = Family(
            family_id="F2", father_id="P3", mother_id="P4", children=[],
            marriage=None, notes=""
        )
        
        assert family_with_notes.has_notes() is True
        assert family_without_notes.has_notes() is False


class TestDate:
    """Tests pour l'entité Date."""
    
    def test_date_creation(self):
        """Test de création d'une date."""
        date = Date(15, 1, 1980)  # jour, mois, année
        
        assert date.day == 15
        assert date.month == 1
        assert date.year == 1980
    
    def test_date_str(self):
        """Test de la représentation string d'une date."""
        date = Date(15, 1, 1980)  # jour, mois, année
        assert str(date) == "15/1/1980"
    
    def test_date_precision(self):
        """Test de la précision des dates."""
        # Date complète
        date1 = Date(15, 1, 1980)  # jour, mois, année
        assert date1.precision == "sure"
        
        # Date approximative
        date2 = Date(15, 1, 1980, precision="approx")  # jour, mois, année
        assert date2.precision == "approx"


class TestEvent:
    """Tests pour l'entité Event."""
    
    def test_event_creation(self):
        """Test de création d'un événement."""
        event = Event(EventType.BAPTISM, Date(20, 1, 1980))  # jour, mois, année
        
        assert event.event_type == EventType.BAPTISM
        assert event.date == Date(20, 1, 1980)
    
    def test_event_str(self):
        """Test de la représentation string d'un événement."""
        event = Event(EventType.BAPTISM, Date(20, 1, 1980))  # jour, mois, année
        assert str(event) == "baptism 20/1/1980"


class TestNote:
    """Tests pour l'entité Note."""
    
    def test_note_creation(self):
        """Test de création d'une note."""
        note = Note("Contenu de la note")
        
        assert note.content == "Contenu de la note"
    
    def test_note_str(self):
        """Test de la représentation string d'une note."""
        note = Note("Contenu de la note")
        assert str(note) == "Contenu de la note"
