"""Tests unitaires pour FamilyService."""

import pytest
from unittest.mock import Mock, MagicMock
from typing import List

from geneweb.common.types import Sex, PersonId, FamilyId
from geneweb.gwu.domain.entities import Person, Family, Event, Date
from geneweb.gwu.domain.repositories import PersonRepository, FamilyRepository
from geneweb.gwu.domain.services.family_service import (
    FamilyService, 
    AncestryResult, 
    DescendantsResult
)


class TestFamilyService:
    """Tests du FamilyService."""
    
    @pytest.fixture
    def mock_person_repo(self):
        """Mock du PersonRepository."""
        return Mock(spec=PersonRepository)
    
    @pytest.fixture
    def mock_family_repo(self):
        """Mock du FamilyRepository."""
        return Mock(spec=FamilyRepository)
    
    @pytest.fixture
    def family_service(self, mock_person_repo, mock_family_repo):
        """Instance de FamilyService avec mocks."""
        return FamilyService(mock_person_repo, mock_family_repo)
    
    @pytest.fixture
    def sample_family(self):
        """Famille d'exemple pour les tests."""
        return Family(
            family_id="F1",
            father_id="P1",
            mother_id="P2",
            children=["P3", "P4"]
        )
    
    @pytest.fixture
    def sample_persons(self):
        """Personnes d'exemple pour les tests."""
        return {
            "P1": Person(
                person_id="P1",
                first_name="Jean",
                surname="Dupont",
                occ=0,
                sex=Sex.MALE,
                parents="F0"  # Parents de P1
            ),
            "P2": Person(
                person_id="P2",
                first_name="Marie",
                surname="Martin",
                occ=0,
                sex=Sex.FEMALE,
                parents="F0"  # Parents de P2
            ),
            "P3": Person(
                person_id="P3",
                first_name="Pierre",
                surname="Dupont",
                occ=0,
                sex=Sex.MALE,
                parents="F1"  # Enfant de F1
            ),
            "P4": Person(
                person_id="P4",
                first_name="Anne",
                surname="Dupont",
                occ=0,
                sex=Sex.FEMALE,
                parents="F1"  # Enfant de F1
            )
        }
    
    def test_get_family_by_id_success(self, family_service, mock_family_repo, sample_family):
        """Test récupération famille par ID - succès."""
        mock_family_repo.get_by_id.return_value = sample_family
        
        result = family_service.get_family_by_id("F1")
        
        assert result == sample_family
        mock_family_repo.get_by_id.assert_called_once_with("F1")
    
    def test_get_family_by_id_not_found(self, family_service, mock_family_repo):
        """Test récupération famille par ID - non trouvée."""
        mock_family_repo.get_by_id.return_value = None
        
        result = family_service.get_family_by_id("F999")
        
        assert result is None
        mock_family_repo.get_by_id.assert_called_once_with("F999")
    
    def test_get_families_of_person(self, family_service, mock_family_repo, sample_family):
        """Test récupération familles d'une personne."""
        mock_family_repo.get_families_of_person.return_value = [sample_family]
        
        result = family_service.get_families_of_person("P1")
        
        assert result == [sample_family]
        mock_family_repo.get_families_of_person.assert_called_once_with("P1")
    
    def test_get_family_of_parents(self, family_service, mock_family_repo, sample_family):
        """Test récupération famille par parents."""
        mock_family_repo.get_family_of_parents.return_value = sample_family
        
        result = family_service.get_family_of_parents("P1", "P2")
        
        assert result == sample_family
        mock_family_repo.get_family_of_parents.assert_called_once_with("P1", "P2")
    
    def test_get_all_families(self, family_service, mock_family_repo, sample_family):
        """Test récupération de toutes les familles."""
        mock_family_repo.get_all.return_value = iter([sample_family])
        
        result = family_service.get_all_families()
        
        assert list(result) == [sample_family]
        mock_family_repo.get_all.assert_called_once()
    
    def test_get_family_count(self, family_service, mock_family_repo):
        """Test comptage des familles."""
        mock_family_repo.get_count.return_value = 5
        
        count = family_service.get_family_count()
        
        assert count == 5
        mock_family_repo.get_count.assert_called_once()
    
    def test_get_ancestors_simple(self, family_service, mock_person_repo, mock_family_repo, sample_persons):
        """Test calcul ascendance simple."""
        # Configuration des mocks
        def mock_get_by_id(person_id):
            return sample_persons.get(person_id)
        
        def mock_get_families_of_person(person_id):
            if person_id == "P1":
                return [Family(family_id="F1", father_id="P1", mother_id="P2", children=["P3", "P4"])]
            return []
        
        # P3 a P1 et P2 comme parents (famille F1)
        def mock_get_family_by_id(family_id):
            if family_id == "F1":
                return Family(family_id="F1", father_id="P1", mother_id="P2", children=["P3", "P4"])
            return None
        
        mock_person_repo.get_by_id.side_effect = mock_get_by_id
        mock_family_repo.get_by_id.side_effect = mock_get_family_by_id
        mock_family_repo.get_families_of_person.side_effect = mock_get_families_of_person
        
        result = family_service.get_ancestors("P3", max_depth=1)
        
        assert isinstance(result, AncestryResult)
        assert len(result.ancestors) == 2  # P1 et P2
        assert "P1" in result.ancestors
        assert "P2" in result.ancestors
        assert result.depth_reached == 1
    
    def test_get_descendants_simple(self, family_service, mock_person_repo, mock_family_repo, sample_persons):
        """Test calcul descendance simple."""
        # Configuration des mocks
        def mock_get_by_id(person_id):
            return sample_persons.get(person_id)
        
        def mock_get_families_of_person(person_id):
            if person_id == "P1":
                return [Family(family_id="F1", father_id="P1", mother_id="P2", children=["P3", "P4"])]
            return []
        
        mock_person_repo.get_by_id.side_effect = mock_get_by_id
        mock_family_repo.get_families_of_person.side_effect = mock_get_families_of_person
        
        result = family_service.get_descendants("P1", max_depth=1)
        
        assert isinstance(result, DescendantsResult)
        assert len(result.descendants) == 2  # P3 et P4
        assert "P3" in result.descendants
        assert "P4" in result.descendants
        assert result.depth_reached == 1
    
    def test_get_ancestors_and_descendants(self, family_service, mock_person_repo, mock_family_repo, sample_persons):
        """Test calcul ascendance et descendance combinées."""
        # Configuration des mocks
        def mock_get_by_id(person_id):
            return sample_persons.get(person_id)
        
        def mock_get_families_of_person(person_id):
            if person_id == "P1":
                return [Family(family_id="F1", father_id="P1", mother_id="P2", children=["P3", "P4"])]
            return []
        
        mock_person_repo.get_by_id.side_effect = mock_get_by_id
        mock_family_repo.get_by_id.return_value = Family(family_id="F0", father_id="P5", mother_id="P6", children=["P1", "P2"])
        mock_family_repo.get_families_of_person.side_effect = mock_get_families_of_person
        
        result = family_service.get_ancestors_and_descendants("P1", asc_depth=1, desc_depth=1)
        
        # P1 + ses parents (P5, P6) + ses enfants (P3, P4)
        assert len(result) == 5
        assert "P1" in result  # La personne elle-même
        assert "P5" in result  # Parent
        assert "P6" in result  # Parent
        assert "P3" in result  # Enfant
        assert "P4" in result  # Enfant
    
    def test_get_related_persons(self, family_service, mock_person_repo, mock_family_repo, sample_persons):
        """Test calcul des personnes liées par parenté."""
        # Configuration des mocks
        def mock_get_by_id(person_id):
            return sample_persons.get(person_id)
        
        def mock_get_families_of_person(person_id):
            if person_id == "P1":
                return [Family(family_id="F1", father_id="P1", mother_id="P2", children=["P3", "P4"])]
            return []
        
        mock_person_repo.get_by_id.side_effect = mock_get_by_id
        mock_family_repo.get_by_id.return_value = Family(family_id="F0", father_id="P5", mother_id="P6", children=["P1", "P2"])
        mock_family_repo.get_families_of_person.side_effect = mock_get_families_of_person
        
        result = family_service.get_related_persons("P1", "P2")
        
        # P1, P2 et leurs ancêtres/descendants communs
        assert "P1" in result
        assert "P2" in result
        assert len(result) >= 2
    
    def test_get_family_tree(self, family_service, mock_person_repo, mock_family_repo, sample_persons):
        """Test construction de l'arbre généalogique."""
        # Configuration des mocks
        def mock_get_by_id(person_id):
            return sample_persons.get(person_id)
        
        def mock_get_families_of_person(person_id):
            if person_id == "P1":
                return [Family(family_id="F1", father_id="P1", mother_id="P2", children=["P3", "P4"])]
            return []
        
        mock_person_repo.get_by_id.side_effect = mock_get_by_id
        mock_family_repo.get_by_id.return_value = Family(family_id="F0", father_id="P5", mother_id="P6", children=["P1", "P2"])
        mock_family_repo.get_families_of_person.side_effect = mock_get_families_of_person
        
        tree = family_service.get_family_tree("P1", max_depth=2)
        
        assert isinstance(tree, dict)
        assert tree["id"] == "P1"
        assert tree["name"] == "Jean.0 Dupont"
        assert tree["sex"] == "male"
        assert len(tree["parents"]) == 2  # P5 et P6
        assert len(tree["children"]) == 2  # P3 et P4
    
    def test_validate_family_success(self, family_service, mock_person_repo, sample_family, sample_persons):
        """Test validation famille - succès."""
        def mock_get_by_id(person_id):
            return sample_persons.get(person_id)
        
        mock_person_repo.get_by_id.side_effect = mock_get_by_id
        
        errors = family_service.validate_family(sample_family)
        
        assert len(errors) == 0
    
    def test_validate_family_errors(self, family_service, mock_person_repo):
        """Test validation famille - erreurs."""
        # Créer une famille invalide en contournant la validation __post_init__
        invalid_family = Family.__new__(Family)
        invalid_family.family_id = ""  # ID vide
        invalid_family.father_id = "P999"  # Père inexistant
        invalid_family.mother_id = ""  # Mère vide
        invalid_family.children = ["P888"]  # Enfant inexistant
        invalid_family.marriage = None
        invalid_family.marriage_bann = None
        invalid_family.marriage_contract = None
        invalid_family.marriage_license = None
        invalid_family.engagement = None
        invalid_family.divorce = None
        invalid_family.separated = None
        invalid_family.annulment = None
        invalid_family.events = []
        invalid_family.notes = None
        invalid_family.sources = []
        invalid_family.witnesses = []
        
        mock_person_repo.get_by_id.return_value = None
        
        errors = family_service.validate_family(invalid_family)
        
        assert len(errors) >= 4
        assert "L'ID de la famille est obligatoire" in errors
        assert "L'ID de la mère est obligatoire" in errors
        assert "Père non trouvé: P999" in errors
        assert "Mère non trouvée: " in errors
        assert "Enfant non trouvé: P888" in errors
