"""Tests unitaires pour SelectionService."""

import pytest
from unittest.mock import Mock, MagicMock
from typing import List, Set

from geneweb.common.types import Sex, PersonId, AccessLevel
from geneweb.gwu.domain.entities import Person, Family
from geneweb.gwu.domain.repositories import PersonRepository, FamilyRepository
from geneweb.gwu.domain.services.selection_service import SelectionService, SelectionResult
from geneweb.gwu.domain.config import SelectionCriteria, ExportOptions


class TestSelectionService:
    """Tests du SelectionService."""
    
    @pytest.fixture
    def mock_person_repo(self):
        """Mock du PersonRepository."""
        return Mock(spec=PersonRepository)
    
    @pytest.fixture
    def mock_family_repo(self):
        """Mock du FamilyRepository."""
        return Mock(spec=FamilyRepository)
    
    @pytest.fixture
    def selection_service(self, mock_person_repo, mock_family_repo):
        """Instance de SelectionService avec mocks."""
        return SelectionService(mock_person_repo, mock_family_repo)
    
    @pytest.fixture
    def sample_persons(self):
        """Personnes d'exemple pour les tests."""
        return [
            Person(
                person_id="P1",
                first_name="Jean",
                surname="Dupont",
                occ=0,
                sex=Sex.MALE,
                access=AccessLevel.PUBLIC,
                public=True
            ),
            Person(
                person_id="P2",
                first_name="Marie",
                surname="Martin",
                occ=0,
                sex=Sex.FEMALE,
                access=AccessLevel.PUBLIC,
                public=True
            ),
            Person(
                person_id="P3",
                first_name="Pierre",
                surname="Dupont",
                occ=1,
                sex=Sex.MALE,
                access=AccessLevel.PRIVATE,
                public=False
            )
        ]
    
    def test_select_persons_empty_criteria(self, selection_service, mock_person_repo, sample_persons):
        """Test sélection avec critères vides."""
        mock_person_repo.get_all.return_value = iter(sample_persons)
        
        criteria = SelectionCriteria()
        result = selection_service.select_persons(criteria)
        
        assert isinstance(result, SelectionResult)
        assert len(result.person_ids) == 3
        assert result.total_selected == 3
        assert result.selection_type == "all"
    
    def test_select_persons_by_keys(self, selection_service, mock_person_repo, sample_persons):
        """Test sélection par clés."""
        def mock_get_by_key(first_name, surname, occ):
            for person in sample_persons:
                if (person.first_name == first_name and 
                    person.surname == surname and 
                    person.occ == occ):
                    return person
            return None
        
        mock_person_repo.get_by_key.side_effect = mock_get_by_key
        
        criteria = SelectionCriteria(keys={"Jean.0 Dupont", "Marie.0 Martin"})
        result = selection_service.select_persons(criteria)
        
        assert len(result.person_ids) == 2
        assert "P1" in result.person_ids
        assert "P2" in result.person_ids
        assert result.selection_type == "keys"
    
    def test_select_persons_by_keys_not_found(self, selection_service, mock_person_repo):
        """Test sélection par clés - non trouvées."""
        mock_person_repo.get_by_key.return_value = None
        mock_person_repo.get_all.return_value = iter([])
        
        criteria = SelectionCriteria(keys={"Inconnu.0 Dupont"})
        result = selection_service.select_persons(criteria)
        
        assert len(result.person_ids) == 0
        assert result.selection_type == "keys"
    
    def test_select_persons_isolated_only(self, selection_service, mock_person_repo, sample_persons):
        """Test sélection personnes isolées."""
        # Simuler une personne isolée
        isolated_person = Person(
            person_id="P4",
            first_name="Isolé",
            surname="Seul",
            occ=0,
            sex=Sex.MALE
        )
        
        mock_person_repo.get_isolated_persons.return_value = iter([isolated_person])
        
        criteria = SelectionCriteria(isolated_only=True)
        result = selection_service.select_persons(criteria)
        
        assert len(result.person_ids) == 1
        assert "P4" in result.person_ids
        assert result.selection_type == "isolated"
    
    def test_select_persons_with_filters(self, selection_service, mock_person_repo, sample_persons):
        """Test sélection avec filtres."""
        def mock_get_by_id(person_id):
            for person in sample_persons:
                if person.person_id == person_id:
                    return person
            return None
        
        mock_person_repo.get_all.return_value = iter(sample_persons)
        mock_person_repo.get_by_id.side_effect = mock_get_by_id
        
        criteria = SelectionCriteria(public_only=True)
        result = selection_service.select_persons(criteria)
        
        # P1 et P2 sont publiques, P3 est privée
        assert len(result.person_ids) == 2
        assert "P1" in result.person_ids
        assert "P2" in result.person_ids
        assert "P3" not in result.person_ids
    
    def test_select_persons_from_options(self, selection_service, mock_person_repo, sample_persons):
        """Test sélection à partir des options d'export."""
        def mock_get_by_key(first_name, surname, occ):
            if first_name == "Jean" and surname == "Dupont" and occ == 0:
                return sample_persons[0]  # P1
            return None
        
        def mock_get_by_id(person_id):
            for person in sample_persons:
                if person.person_id == person_id:
                    return person
            return None
        
        mock_person_repo.get_by_key.side_effect = mock_get_by_key
        mock_person_repo.get_by_id.side_effect = mock_get_by_id
        mock_person_repo.get_all.return_value = iter(sample_persons)
        
        options = ExportOptions(
            keys=["Jean.0 Dupont"],
            filter_public=True
        )
        
        result = selection_service.select_persons_from_options(options)
        
        assert len(result.person_ids) == 1
        assert "P1" in result.person_ids
        assert result.selection_type == "keys"
    
    def test_select_by_keys(self, selection_service, mock_person_repo, sample_persons):
        """Test sélection par clés (méthode privée)."""
        def mock_get_by_key(first_name, surname, occ):
            for person in sample_persons:
                if (person.first_name == first_name and 
                    person.surname == surname and 
                    person.occ == occ):
                    return person
            return None
        
        mock_person_repo.get_by_key.side_effect = mock_get_by_key
        
        keys = {"Jean.0 Dupont", "Marie.0 Martin"}
        result = selection_service._select_by_keys(keys)
        
        assert len(result) == 2
        assert "P1" in result
        assert "P2" in result
    
    def test_select_isolated_persons(self, selection_service, mock_person_repo):
        """Test sélection personnes isolées (méthode privée)."""
        isolated_persons = [
            Person(
                person_id="P4",
                first_name="Isolé1",
                surname="Seul",
                occ=0,
                sex=Sex.MALE
            ),
            Person(
                person_id="P5",
                first_name="Isolé2",
                surname="Seul",
                occ=0,
                sex=Sex.FEMALE
            )
        ]
        
        mock_person_repo.get_isolated_persons.return_value = iter(isolated_persons)
        
        result = selection_service._select_isolated_persons()
        
        assert len(result) == 2
        assert "P4" in result
        assert "P5" in result
    
    def test_apply_filters_public_only(self, selection_service, mock_person_repo, sample_persons):
        """Test application des filtres - public seulement."""
        def mock_get_by_id(person_id):
            for person in sample_persons:
                if person.person_id == person_id:
                    return person
            return None
        
        mock_person_repo.get_by_id.side_effect = mock_get_by_id
        
        person_ids = {"P1", "P2", "P3"}
        criteria = SelectionCriteria(public_only=True)
        
        result = selection_service._apply_filters(person_ids, criteria)
        
        # P1 et P2 sont publiques, P3 est privée
        assert len(result) == 2
        assert "P1" in result
        assert "P2" in result
        assert "P3" not in result
    
    def test_apply_filters_private_only(self, selection_service, mock_person_repo, sample_persons):
        """Test application des filtres - privé seulement."""
        def mock_get_by_id(person_id):
            for person in sample_persons:
                if person.person_id == person_id:
                    return person
            return None
        
        mock_person_repo.get_by_id.side_effect = mock_get_by_id
        
        person_ids = {"P1", "P2", "P3"}
        criteria = SelectionCriteria(private_only=True)
        
        result = selection_service._apply_filters(person_ids, criteria)
        
        # P3 est privée, P1 et P2 sont publiques
        assert len(result) == 1
        assert "P3" in result
        assert "P1" not in result
        assert "P2" not in result
    
    def test_apply_filters_with_events(self, selection_service, mock_person_repo):
        """Test application des filtres - avec événements."""
        person_with_events = Person(
            person_id="P1",
            first_name="Jean",
            surname="Dupont",
            occ=0,
            sex=Sex.MALE,
            events=[{"type": "birth", "date": "1850"}]
        )
        person_without_events = Person(
            person_id="P2",
            first_name="Marie",
            surname="Martin",
            occ=0,
            sex=Sex.FEMALE
        )
        
        def mock_get_by_id(person_id):
            if person_id == "P1":
                return person_with_events
            elif person_id == "P2":
                return person_without_events
            return None
        
        mock_person_repo.get_by_id.side_effect = mock_get_by_id
        
        person_ids = {"P1", "P2"}
        criteria = SelectionCriteria(with_events=True)
        
        result = selection_service._apply_filters(person_ids, criteria)
        
        assert len(result) == 1
        assert "P1" in result
        assert "P2" not in result
    
    def test_parse_key_to_person_success(self, selection_service, mock_person_repo, sample_persons):
        """Test parsing clé vers personne - succès."""
        def mock_get_by_key(first_name, surname, occ):
            for person in sample_persons:
                if (person.first_name == first_name and 
                    person.surname == surname and 
                    person.occ == occ):
                    return person
            return None
        
        mock_person_repo.get_by_key.side_effect = mock_get_by_key
        
        result = selection_service._parse_key_to_person("Jean.0 Dupont")
        
        assert result == sample_persons[0]
        mock_person_repo.get_by_key.assert_called_once_with("Jean", "Dupont", 0)
    
    def test_parse_key_to_person_without_occ(self, selection_service, mock_person_repo, sample_persons):
        """Test parsing clé sans occurrence."""
        def mock_get_by_key(first_name, surname, occ):
            for person in sample_persons:
                if (person.first_name == first_name and 
                    person.surname == surname and 
                    person.occ == occ):
                    return person
            return None
        
        mock_person_repo.get_by_key.side_effect = mock_get_by_key
        
        result = selection_service._parse_key_to_person("Jean Dupont")
        
        assert result == sample_persons[0]
        mock_person_repo.get_by_key.assert_called_once_with("Jean", "Dupont", 0)
    
    def test_parse_key_to_person_invalid(self, selection_service, mock_person_repo):
        """Test parsing clé invalide."""
        mock_person_repo.get_by_key.return_value = None
        
        result = selection_service._parse_key_to_person("Invalid Key")
        
        assert result is None
    
    def test_get_selection_type_keys(self, selection_service):
        """Test détermination du type de sélection - clés."""
        criteria = SelectionCriteria(keys={"Jean.0 Dupont"})
        
        result = selection_service._get_selection_type(criteria)
        
        assert result == "keys"
    
    def test_get_selection_type_parentship(self, selection_service):
        """Test détermination du type de sélection - parenté."""
        criteria = SelectionCriteria(keys={"Jean.0 Dupont", "Marie.0 Martin"}, parentship=True)
        
        result = selection_service._get_selection_type(criteria)
        
        assert result == "parentship"
    
    def test_get_selection_type_isolated(self, selection_service):
        """Test détermination du type de sélection - isolées."""
        criteria = SelectionCriteria(isolated_only=True)
        
        result = selection_service._get_selection_type(criteria)
        
        assert result == "isolated"
    
    def test_get_selection_type_all(self, selection_service):
        """Test détermination du type de sélection - toutes."""
        criteria = SelectionCriteria()
        
        result = selection_service._get_selection_type(criteria)
        
        assert result == "all"
