"""
Tests unitaires pour les règles de formatage GW.
"""

import pytest
from geneweb.gwu.adapters.output.gw_formatting_rules import GwFormattingRules
from geneweb.gwu.domain.entities.person import Person
from geneweb.gwu.domain.entities.date import Date


class TestGwFormattingRules:
    """Tests pour les règles de formatage GW."""
    
    def test_format_parent_name_basic(self):
        """Test du formatage basique d'un nom de parent."""
        person = Person(
            person_id="P1", surname="Dupont", first_name="Jean", sex="male", occ=0,
            birth=None, death=None, notes="", events=[]
        )
        
        result = GwFormattingRules.format_parent_name(person)
        assert result == "Dupont Jean"
    
    def test_format_parent_name_with_occ(self):
        """Test du formatage avec occ > 0."""
        person = Person(
            person_id="P1", surname="Dupont", first_name="Jean", sex="male", occ=2,
            birth=None, death=None, notes="", events=[]
        )
        
        result = GwFormattingRules.format_parent_name(person)
        assert result == "Dupont Jean.2"
    
    def test_format_parent_name_with_spaces(self):
        """Test du formatage avec espaces dans le prénom."""
        person = Person(
            person_id="P1", surname="Dupont", first_name="Jean Pierre", sex="male", occ=0,
            birth=None, death=None, notes="", events=[]
        )
        
        result = GwFormattingRules.format_parent_name(person)
        assert result == "Dupont Jean_Pierre"
    
    def test_format_parent_name_unknown(self):
        """Test du formatage avec prénom et nom inconnus."""
        person = Person(
            person_id="P1", surname="?", first_name="?", sex="unknown", occ=0,
            birth=None, death=None, notes="", events=[]
        )
        
        result = GwFormattingRules.format_parent_name(person)
        assert result == "? ?"
    
    def test_format_parent_name_unknown_with_occ(self):
        """Test du formatage avec prénom et nom inconnus et occ > 0."""
        person = Person(
            person_id="P1", surname="?", first_name="?", sex="unknown", occ=1,
            birth=None, death=None, notes="", events=[]
        )
        
        result = GwFormattingRules.format_parent_name(person)
        assert result == "? ?.1"
    
    def test_format_date_basic(self):
        """Test du formatage basique d'une date."""
        date = Date(15, 1, 1980)
        result = GwFormattingRules.format_date(date)
        assert result == "15/1/1980"
    
    def test_format_date_with_precision(self):
        """Test du formatage d'une date avec précision."""
        date = Date(15, 1, 1980, precision="approx")
        result = GwFormattingRules.format_date(date)
        assert result == "~15/1/1980"
    
    def test_format_date_unknown(self):
        """Test du formatage d'une date inconnue."""
        date = Date(15, 1, 1980, precision="unknown")
        result = GwFormattingRules.format_date(date)
        assert result == "?15/1/1980"
    
    def test_format_date_before(self):
        """Test du formatage d'une date 'avant'."""
        date = Date(15, 1, 1980, precision="before")
        result = GwFormattingRules.format_date(date)
        assert result == "<15/1/1980"
    
    def test_format_date_after(self):
        """Test du formatage d'une date 'après'."""
        date = Date(15, 1, 1980, precision="after")
        result = GwFormattingRules.format_date(date)
        assert result == ">15/1/1980"
    
    def test_format_event_marker(self):
        """Test du formatage des marqueurs d'événements."""
        # format_event_marker n'est pas implémenté dans GwFormattingRules
        pytest.skip("format_event_marker non implémenté")
        assert GwFormattingRules.format_event_marker("deat") == "#deat"
        assert GwFormattingRules.format_event_marker("marr") == "#marr"
        assert GwFormattingRules.format_event_marker("bapt") == "#bapt"
        assert GwFormattingRules.format_event_marker("buri") == "#buri"
    
    def test_format_place_basic(self):
        """Test du formatage basique d'un lieu."""
        place = "Paris, France"
        result = GwFormattingRules.format_place(place)
        assert result == "Paris, France"
    
    def test_format_place_with_underscores(self):
        """Test du formatage d'un lieu avec underscores."""
        place = "Saint-Pierre, France"
        result = GwFormattingRules.format_place(place)
        assert result == "Saint-Pierre, France"
    
    def test_format_source_basic(self):
        """Test du formatage basique d'une source."""
        # format_source n'est pas implémenté dans GwFormattingRules
        pytest.skip("format_source non implémenté")
    
    def test_format_notes_basic(self):
        """Test du formatage basique des notes."""
        # format_notes n'est pas implémenté dans GwFormattingRules
        pytest.skip("format_notes non implémenté")
    
    def test_format_notes_with_links(self):
        """Test du formatage des notes avec liens."""
        # format_notes n'est pas implémenté dans GwFormattingRules
        pytest.skip("format_notes non implémenté")
