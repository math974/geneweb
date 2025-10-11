"""Tests unitaires pour l'entité Family."""

import pytest

from geneweb.common.types import EventType
from geneweb.gwu.domain.entities import Family, Event, Date


class TestFamilyCreation:
    """Tests de création de familles."""
    
    def test_create_simple_family(self):
        """Test création famille simple."""
        family = Family(
            family_id="F1",
            father_id="P1",
            mother_id="P2"
        )
        assert family.family_id == "F1"
        assert family.father_id == "P1"
        assert family.mother_id == "P2"
    
    def test_empty_family_id_raises_error(self):
        """Test ID vide génère erreur."""
        with pytest.raises(ValueError, match="famille"):
            Family(
                family_id="",
                father_id="P1",
                mother_id="P2"
            )
    
    def test_empty_father_id_raises_error(self):
        """Test ID père vide génère erreur."""
        with pytest.raises(ValueError, match="père"):
            Family(
                family_id="F1",
                father_id="",
                mother_id="P2"
            )
    
    def test_empty_mother_id_raises_error(self):
        """Test ID mère vide génère erreur."""
        with pytest.raises(ValueError, match="mère"):
            Family(
                family_id="F1",
                father_id="P1",
                mother_id=""
            )


class TestFamilyChildren:
    """Tests de gestion des enfants."""
    
    def test_add_child(self):
        """Test ajout enfant."""
        family = Family(
            family_id="F1",
            father_id="P1",
            mother_id="P2"
        )
        family.add_child("P3")
        assert family.children_count() == 1
        assert "P3" in family.children
    
    def test_add_child_no_duplicate(self):
        """Test pas de doublon lors ajout enfant."""
        family = Family(
            family_id="F1",
            father_id="P1",
            mother_id="P2"
        )
        family.add_child("P3")
        family.add_child("P3")
        assert family.children_count() == 1
    
    def test_remove_child(self):
        """Test suppression enfant."""
        family = Family(
            family_id="F1",
            father_id="P1",
            mother_id="P2",
            children=["P3", "P4"]
        )
        removed = family.remove_child("P3")
        assert removed is True
        assert family.children_count() == 1
        assert "P3" not in family.children
    
    def test_remove_nonexistent_child(self):
        """Test suppression enfant inexistant."""
        family = Family(
            family_id="F1",
            father_id="P1",
            mother_id="P2"
        )
        removed = family.remove_child("P99")
        assert removed is False
    
    def test_has_children(self):
        """Test détection enfants."""
        family = Family(
            family_id="F1",
            father_id="P1",
            mother_id="P2",
            children=["P3"]
        )
        assert family.has_children()
    
    def test_no_children(self):
        """Test absence enfants."""
        family = Family(
            family_id="F1",
            father_id="P1",
            mother_id="P2"
        )
        assert not family.has_children()


class TestFamilyMarriage:
    """Tests des événements de mariage."""
    
    def test_has_marriage(self):
        """Test détection mariage."""
        family = Family(
            family_id="F1",
            father_id="P1",
            mother_id="P2",
            marriage=Event(event_type=EventType.MARRIAGE)
        )
        assert family.has_marriage()
    
    def test_no_marriage(self):
        """Test absence mariage."""
        family = Family(
            family_id="F1",
            father_id="P1",
            mother_id="P2"
        )
        assert not family.has_marriage()
    
    def test_is_married(self):
        """Test couple marié (mariage sans divorce)."""
        family = Family(
            family_id="F1",
            father_id="P1",
            mother_id="P2",
            marriage=Event(event_type=EventType.MARRIAGE)
        )
        assert family.is_married()
    
    def test_not_married_without_marriage(self):
        """Test couple non marié sans mariage."""
        family = Family(
            family_id="F1",
            father_id="P1",
            mother_id="P2"
        )
        assert not family.is_married()


class TestFamilyDivorce:
    """Tests des événements de divorce."""
    
    def test_has_divorce(self):
        """Test détection divorce."""
        family = Family(
            family_id="F1",
            father_id="P1",
            mother_id="P2",
            divorce=Event(event_type=EventType.DIVORCE)
        )
        assert family.has_divorce()
    
    def test_is_divorced(self):
        """Test couple divorcé."""
        family = Family(
            family_id="F1",
            father_id="P1",
            mother_id="P2",
            marriage=Event(event_type=EventType.MARRIAGE),
            divorce=Event(event_type=EventType.DIVORCE)
        )
        assert family.is_divorced()
        assert not family.is_married()


class TestFamilyPredicates:
    """Tests des prédicats de famille."""
    
    def test_get_parents(self):
        """Test récupération tuple parents."""
        family = Family(
            family_id="F1",
            father_id="P1",
            mother_id="P2"
        )
        father, mother = family.get_parents()
        assert father == "P1"
        assert mother == "P2"


class TestFamilyStringRepresentation:
    """Tests de représentation string."""
    
    def test_str_representation(self):
        """Test __str__."""
        family = Family(
            family_id="F1",
            father_id="P1",
            mother_id="P2",
            children=["P3", "P4"]
        )
        str_repr = str(family)
        assert "P1" in str_repr
        assert "P2" in str_repr
        assert "2 enfants" in str_repr
    
    def test_repr_representation(self):
        """Test __repr__."""
        family = Family(
            family_id="F1",
            father_id="P1",
            mother_id="P2"
        )
        repr_str = repr(family)
        assert "Family" in repr_str
        assert "id=F1" in repr_str
        assert "father=P1" in repr_str
        assert "mother=P2" in repr_str
