"""Tests unitaires pour l'entité Person."""

import pytest

from geneweb.common.types import Sex, AccessLevel, EventType
from geneweb.gwu.domain.entities import Person, Event, Date, Note, Source


class TestPersonCreation:
    """Tests de création de personnes."""
    
    def test_create_simple_person(self):
        """Test création personne simple."""
        person = Person(
            person_id="1",
            first_name="Jean",
            surname="Dupont",
            sex=Sex.MALE
        )
        assert person.person_id == "1"
        assert person.first_name == "Jean"
        assert person.surname == "Dupont"
        assert person.sex == Sex.MALE
        assert person.occ == 0
    
    def test_create_person_with_occ(self):
        """Test création personne avec occurrence."""
        person = Person(
            person_id="2",
            first_name="Jean",
            surname="Dupont",
            occ=1,
            sex=Sex.MALE
        )
        assert person.occ == 1
    
    def test_empty_first_name_raises_error(self):
        """Test nom vide génère erreur."""
        with pytest.raises(ValueError, match="prénom"):
            Person(
                person_id="1",
                first_name="",
                surname="Dupont",
                sex=Sex.MALE
            )
    
    def test_empty_surname_raises_error(self):
        """Test patronyme vide génère erreur."""
        with pytest.raises(ValueError, match="nom de famille"):
            Person(
                person_id="1",
                first_name="Jean",
                surname="",
                sex=Sex.MALE
            )
    
    def test_negative_occ_raises_error(self):
        """Test occurrence négative génère erreur."""
        with pytest.raises(ValueError, match="occurrence"):
            Person(
                person_id="1",
                first_name="Jean",
                surname="Dupont",
                occ=-1,
                sex=Sex.MALE
            )


class TestPersonFormatting:
    """Tests de formatage des noms."""
    
    def test_format_name_occ_zero(self):
        """Test format nom avec occ=0."""
        person = Person(
            person_id="1",
            first_name="Jean",
            surname="Dupont",
            sex=Sex.MALE
        )
        assert person.format_name() == "Jean.0 Dupont"
    
    def test_format_name_occ_one(self):
        """Test format nom avec occ=1."""
        person = Person(
            person_id="2",
            first_name="Jean",
            surname="Dupont",
            occ=1,
            sex=Sex.MALE
        )
        assert person.format_name() == "Jean.1 Dupont"
    
    def test_format_key_equals_format_name(self):
        """Test format_key identique à format_name."""
        person = Person(
            person_id="1",
            first_name="Marie",
            surname="Martin",
            sex=Sex.FEMALE
        )
        assert person.format_key() == person.format_name()


class TestPersonPredicates:
    """Tests des prédicats de personne."""
    
    def test_is_male(self):
        """Test identification sexe masculin."""
        person = Person(
            person_id="1",
            first_name="Jean",
            surname="Dupont",
            sex=Sex.MALE
        )
        assert person.is_male()
        assert not person.is_female()
    
    def test_is_female(self):
        """Test identification sexe féminin."""
        person = Person(
            person_id="1",
            first_name="Marie",
            surname="Martin",
            sex=Sex.FEMALE
        )
        assert person.is_female()
        assert not person.is_male()
    
    def test_is_isolated_without_relations(self):
        """Test personne isolée sans relations."""
        person = Person(
            person_id="1",
            first_name="Jean",
            surname="Dupont",
            sex=Sex.MALE
        )
        assert person.is_isolated()
    
    def test_not_isolated_with_parents(self):
        """Test personne non isolée avec parents."""
        person = Person(
            person_id="1",
            first_name="Jean",
            surname="Dupont",
            sex=Sex.MALE,
            parents="F1"
        )
        assert not person.is_isolated()
    
    def test_not_isolated_with_spouses(self):
        """Test personne non isolée avec conjoint."""
        person = Person(
            person_id="1",
            first_name="Jean",
            surname="Dupont",
            sex=Sex.MALE,
            spouses=["F2"]
        )
        assert not person.is_isolated()
    
    def test_has_birth(self):
        """Test détection naissance."""
        person = Person(
            person_id="1",
            first_name="Jean",
            surname="Dupont",
            sex=Sex.MALE,
            birth=Event(event_type=EventType.BIRTH)
        )
        assert person.has_birth()
    
    def test_no_birth(self):
        """Test absence naissance."""
        person = Person(
            person_id="1",
            first_name="Jean",
            surname="Dupont",
            sex=Sex.MALE
        )
        assert not person.has_birth()
    
    def test_is_public(self):
        """Test personne publique."""
        person = Person(
            person_id="1",
            first_name="Jean",
            surname="Dupont",
            sex=Sex.MALE,
            public=True,
            access=AccessLevel.PUBLIC
        )
        assert person.is_public()
    
    def test_not_public(self):
        """Test personne privée."""
        person = Person(
            person_id="1",
            first_name="Jean",
            surname="Dupont",
            sex=Sex.MALE,
            public=False
        )
        assert not person.is_public()


class TestPersonStringRepresentation:
    """Tests de représentation string."""
    
    def test_str_representation(self):
        """Test __str__."""
        person = Person(
            person_id="1",
            first_name="Jean",
            surname="Dupont",
            sex=Sex.MALE
        )
        assert str(person) == "Jean.0 Dupont"
    
    def test_repr_representation(self):
        """Test __repr__."""
        person = Person(
            person_id="1",
            first_name="Jean",
            surname="Dupont",
            sex=Sex.MALE
        )
        repr_str = repr(person)
        assert "Person" in repr_str
        assert "id=1" in repr_str
        assert "Jean.0 Dupont" in repr_str
