"""Tests unitaires pour PersonService."""

import pytest
from unittest.mock import Mock, MagicMock
from typing import List

from geneweb.common.types import Sex, AccessLevel, PersonId
from geneweb.gwu.domain.entities import Person, Event, Date, Place
from geneweb.gwu.domain.repositories import PersonRepository
from geneweb.gwu.domain.services.person_service import PersonService, PersonSearchResult
from geneweb.gwu.domain.config import SelectionCriteria


class TestPersonService:
    """Tests du PersonService."""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock du PersonRepository."""
        return Mock(spec=PersonRepository)
    
    @pytest.fixture
    def person_service(self, mock_repository):
        """Instance de PersonService avec mock."""
        return PersonService(mock_repository)
    
    @pytest.fixture
    def sample_person(self):
        """Personne d'exemple pour les tests."""
        return Person(
            person_id="P1",
            first_name="Jean",
            surname="Dupont",
            occ=0,
            sex=Sex.MALE,
            access=AccessLevel.PUBLIC
        )
    
    @pytest.fixture
    def sample_persons(self):
        """Liste de personnes d'exemple."""
        return [
            Person(
                person_id="P1",
                first_name="Jean",
                surname="Dupont",
                occ=0,
                sex=Sex.MALE,
                access=AccessLevel.PUBLIC
            ),
            Person(
                person_id="P2",
                first_name="Marie",
                surname="Martin",
                occ=0,
                sex=Sex.FEMALE,
                access=AccessLevel.PUBLIC
            ),
            Person(
                person_id="P3",
                first_name="Pierre",
                surname="Dupont",
                occ=1,
                sex=Sex.MALE,
                access=AccessLevel.PRIVATE
            )
        ]
    
    def test_get_person_by_id_success(self, person_service, mock_repository, sample_person):
        """Test récupération personne par ID - succès."""
        mock_repository.get_by_id.return_value = sample_person
        
        result = person_service.get_person_by_id("P1")
        
        assert result == sample_person
        mock_repository.get_by_id.assert_called_once_with("P1")
    
    def test_get_person_by_id_not_found(self, person_service, mock_repository):
        """Test récupération personne par ID - non trouvée."""
        mock_repository.get_by_id.return_value = None
        
        result = person_service.get_person_by_id("P999")
        
        assert result is None
        mock_repository.get_by_id.assert_called_once_with("P999")
    
    def test_get_person_by_key_success(self, person_service, mock_repository, sample_person):
        """Test récupération personne par clé - succès."""
        mock_repository.get_by_key.return_value = sample_person
        
        result = person_service.get_person_by_key("Jean", "Dupont", 0)
        
        assert result == sample_person
        mock_repository.get_by_key.assert_called_once_with("Jean", "Dupont", 0)
    
    def test_get_person_by_key_not_found(self, person_service, mock_repository):
        """Test récupération personne par clé - non trouvée."""
        mock_repository.get_by_key.return_value = None
        
        result = person_service.get_person_by_key("Inconnu", "Dupont", 0)
        
        assert result is None
        mock_repository.get_by_key.assert_called_once_with("Inconnu", "Dupont", 0)
    
    def test_search_persons(self, person_service, mock_repository, sample_persons):
        """Test recherche de personnes."""
        mock_repository.search_by_name.return_value = sample_persons[:2]
        
        result = person_service.search_persons("Dupont")
        
        assert isinstance(result, PersonSearchResult)
        assert len(result.persons) == 2
        assert result.total_count == 2
        assert result.filtered_count == 2
        mock_repository.search_by_name.assert_called_once_with("Dupont")
    
    def test_search_persons_with_limit(self, person_service, mock_repository, sample_persons):
        """Test recherche de personnes avec limite."""
        mock_repository.search_by_name.return_value = sample_persons
        
        result = person_service.search_persons("Dupont", limit=2)
        
        assert len(result.persons) == 2
        assert result.total_count == 2
    
    def test_get_all_persons(self, person_service, mock_repository, sample_persons):
        """Test récupération de toutes les personnes."""
        mock_repository.get_all.return_value = iter(sample_persons)
        
        result = person_service.get_all_persons()
        
        assert list(result) == sample_persons
        mock_repository.get_all.assert_called_once()
    
    def test_get_persons_by_criteria_empty(self, person_service, mock_repository, sample_persons):
        """Test sélection par critères vides."""
        mock_repository.get_all.return_value = iter(sample_persons)
        
        criteria = SelectionCriteria()
        result = person_service.get_persons_by_criteria(criteria)
        
        assert len(result.persons) == 3
        assert result.total_count == 3
        assert result.filtered_count == 3
    
    def test_get_persons_by_criteria_with_keys(self, person_service, mock_repository, sample_person):
        """Test sélection par critères avec clés."""
        def mock_get_by_key(first_name, surname, occ):
            if first_name == "Jean" and surname == "Dupont" and occ == 0:
                return sample_person
            return None
        
        def mock_get_by_id(person_id):
            if person_id == sample_person.person_id:
                return sample_person
            return None
        
        mock_repository.get_by_key.side_effect = mock_get_by_key
        mock_repository.get_by_id.side_effect = mock_get_by_id
        mock_repository.get_all.return_value = iter([sample_person])
        
        criteria = SelectionCriteria(keys={"Jean.0 Dupont"})
        result = person_service.get_persons_by_criteria(criteria)
        
        assert len(result.persons) == 1
        assert result.persons[0] == sample_person
    
    def test_get_persons_by_sex(self, person_service, mock_repository, sample_persons):
        """Test récupération par sexe."""
        mock_repository.get_all.return_value = iter(sample_persons)
        
        males = person_service.get_persons_by_sex(Sex.MALE)
        
        assert len(males) == 2
        assert all(p.sex == Sex.MALE for p in males)
    
    def test_get_persons_by_access_level(self, person_service, mock_repository, sample_persons):
        """Test récupération par niveau d'accès."""
        mock_repository.get_all.return_value = iter(sample_persons)
        
        public = person_service.get_persons_by_access_level(AccessLevel.PUBLIC)
        
        assert len(public) == 2
        assert all(p.access == AccessLevel.PUBLIC for p in public)
    
    def test_get_public_persons(self, person_service, mock_repository, sample_persons):
        """Test récupération des personnes publiques."""
        mock_repository.get_all.return_value = iter(sample_persons)
        
        public = person_service.get_public_persons()
        
        assert len(public) == 2
        assert all(p.is_public() for p in public)
    
    def test_get_persons_with_events(self, person_service, mock_repository):
        """Test récupération des personnes avec événements."""
        person_with_events = Person(
            person_id="P1",
            first_name="Jean",
            surname="Dupont",
            occ=0,
            sex=Sex.MALE,
            events=[Event(event_type="birth", date=Date.from_year(1850))]
        )
        person_without_events = Person(
            person_id="P2",
            first_name="Marie",
            surname="Martin",
            occ=0,
            sex=Sex.FEMALE
        )
        
        mock_repository.get_all.return_value = iter([person_with_events, person_without_events])
        
        with_events = person_service.get_persons_with_events()
        
        assert len(with_events) == 1
        assert with_events[0] == person_with_events
    
    def test_get_person_count(self, person_service, mock_repository):
        """Test comptage des personnes."""
        mock_repository.get_count.return_value = 42
        
        count = person_service.get_person_count()
        
        assert count == 42
        mock_repository.get_count.assert_called_once()
    
    def test_validate_person_success(self, person_service, sample_person):
        """Test validation personne - succès."""
        errors = person_service.validate_person(sample_person)
        
        assert len(errors) == 0
    
    def test_validate_person_errors(self, person_service):
        """Test validation personne - erreurs."""
        # Créer une personne invalide en contournant la validation __post_init__
        invalid_person = Person.__new__(Person)
        invalid_person.person_id = "P1"
        invalid_person.first_name = ""  # Prénom vide
        invalid_person.surname = ""     # Nom vide
        invalid_person.occ = -1         # Occurrence négative
        invalid_person.sex = Sex.MALE
        invalid_person.public = True
        invalid_person.access = "public"
        invalid_person.parents = None
        invalid_person.spouses = []
        invalid_person.events = []
        invalid_person.notes = None
        invalid_person.sources = []
        invalid_person.occupation = None
        invalid_person.titles = []
        invalid_person.image = None
        invalid_person.related_persons = []
        
        errors = person_service.validate_person(invalid_person)
        
        assert len(errors) >= 3
        assert "Le prénom est obligatoire" in errors
        assert "Le nom de famille est obligatoire" in errors
        assert "L'occurrence ne peut pas être négative" in errors
    
    def test_parse_key_to_person_success(self, person_service, mock_repository, sample_person):
        """Test parsing clé vers personne - succès."""
        mock_repository.get_by_key.return_value = sample_person
        
        result = person_service._parse_key_to_person("Jean.0 Dupont")
        
        assert result == sample_person
        mock_repository.get_by_key.assert_called_once_with("Jean", "Dupont", 0)
    
    def test_parse_key_to_person_without_occ(self, person_service, mock_repository, sample_person):
        """Test parsing clé sans occurrence."""
        mock_repository.get_by_key.return_value = sample_person
        
        result = person_service._parse_key_to_person("Jean Dupont")
        
        assert result == sample_person
        mock_repository.get_by_key.assert_called_once_with("Jean", "Dupont", 0)
    
    def test_parse_key_to_person_invalid(self, person_service, mock_repository):
        """Test parsing clé invalide."""
        mock_repository.get_by_key.return_value = None
        
        result = person_service._parse_key_to_person("Invalid Key")
        
        assert result is None
    
    def test_matches_filters_public_only(self, person_service, sample_person):
        """Test filtrage public seulement."""
        criteria = SelectionCriteria(public_only=True)
        
        # Personne publique
        sample_person.public = True
        sample_person.access = AccessLevel.PUBLIC
        assert person_service._matches_filters(sample_person, criteria)
        
        # Personne privée
        sample_person.public = False
        sample_person.access = AccessLevel.PRIVATE
        assert not person_service._matches_filters(sample_person, criteria)
    
    def test_matches_filters_with_events(self, person_service, sample_person):
        """Test filtrage avec événements."""
        criteria = SelectionCriteria(with_events=True)
        
        # Personne sans événements
        sample_person.events = []
        assert not person_service._matches_filters(sample_person, criteria)
        
        # Personne avec événements
        sample_person.events = [Event(event_type="birth", date=Date.from_year(1850))]
        assert person_service._matches_filters(sample_person, criteria)
