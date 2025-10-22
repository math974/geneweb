"""Tests unitaires pour ExportDatabaseUseCase."""

import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path
from typing import List, Set

from geneweb.common.types import Sex, PersonId
from geneweb.gwu.domain.entities import Person, Family, Event, Date
from geneweb.gwu.domain.repositories import PersonRepository, FamilyRepository
from geneweb.gwu.domain.services.selection_service import SelectionService
from geneweb.gwu.use_cases.export_database import ExportDatabaseUseCase
from geneweb.gwu.domain.config import ExportRequest, ExportResult, ExportOptions, SelectionCriteria


class TestExportDatabaseUseCase:
    """Tests du ExportDatabaseUseCase."""
    
    @pytest.fixture
    def mock_person_repo(self):
        """Mock du PersonRepository."""
        return Mock(spec=PersonRepository)
    
    @pytest.fixture
    def mock_family_repo(self):
        """Mock du FamilyRepository."""
        return Mock(spec=FamilyRepository)
    
    @pytest.fixture
    def mock_selection_service(self):
        """Mock du SelectionService."""
        return Mock(spec=SelectionService)
    
    @pytest.fixture
    def export_use_case(self, mock_person_repo, mock_family_repo, mock_selection_service):
        """Instance de ExportDatabaseUseCase avec mocks."""
        return ExportDatabaseUseCase(mock_person_repo, mock_family_repo, mock_selection_service)
    
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
                birth=Event(event_type="birth", date=Date.from_year(1850)),
                death=Event(event_type="death", date=Date.from_year(1920))
            ),
            Person(
                person_id="P2",
                first_name="Marie",
                surname="Martin",
                occ=0,
                sex=Sex.FEMALE,
                birth=Event(event_type="birth", date=Date.from_year(1855))
            )
        ]
    
    @pytest.fixture
    def sample_families(self):
        """Familles d'exemple pour les tests."""
        return [
            Family(
                family_id="F1",
                father_id="P1",
                mother_id="P2",
                children=["P3"],
                marriage=Event(event_type="marriage", date=Date.from_year(1875))
            )
        ]
    
    @pytest.fixture
    def valid_request(self):
        """Requête d'export valide."""
        return ExportRequest(
            database_path=Path("test.gwb"),
            options=ExportOptions(),
            output_file=Path("output.gw"),
            validate=False  # Désactiver la validation pour les tests
        )
    
    def test_execute_success(self, export_use_case, mock_selection_service, mock_person_repo, mock_family_repo, valid_request, sample_persons, sample_families):
        """Test exécution - succès."""
        # Configuration des mocks
        mock_selection_service.select_persons_from_options.return_value = Mock(person_ids={"P1", "P2"})
        mock_person_repo.get_by_id.side_effect = lambda pid: next((p for p in sample_persons if p.person_id == pid), None)
        mock_family_repo.get_by_id.side_effect = lambda fid: next((f for f in sample_families if f.family_id == fid), None)
        mock_family_repo.get_families_of_person.return_value = sample_families
        
        result = export_use_case.execute(valid_request)
        
        assert isinstance(result, ExportResult)
        assert result.success is True
        assert result.exported_persons == 2
        assert result.exported_families == 1
        assert result.exported_events > 0
        assert result.processing_time > 0
        assert result.error_message is None
    
    def test_execute_with_selection_criteria(self, export_use_case, mock_selection_service, mock_person_repo, mock_family_repo, sample_persons, sample_families):
        """Test exécution avec critères de sélection."""
        # Configuration des mocks
        mock_selection_service.select_persons.return_value = Mock(person_ids={"P1"})
        mock_person_repo.get_by_id.side_effect = lambda pid: next((p for p in sample_persons if p.person_id == pid), None)
        mock_family_repo.get_by_id.side_effect = lambda fid: next((f for f in sample_families if f.family_id == fid), None)
        mock_family_repo.get_families_of_person.return_value = sample_families
        
        request = ExportRequest(
            database_path=Path("test.gwb"),
            options=ExportOptions(),
            selection=SelectionCriteria(keys={"Jean.0 Dupont"}),
            validate=False
        )
        
        result = export_use_case.execute(request)
        
        assert result.success is True
        assert result.exported_persons == 1
        mock_selection_service.select_persons.assert_called_once()
    
    def test_execute_with_options_selection(self, export_use_case, mock_selection_service, mock_person_repo, mock_family_repo, sample_persons, sample_families):
        """Test exécution avec sélection par options."""
        # Configuration des mocks
        mock_selection_service.select_persons_from_options.return_value = Mock(person_ids={"P1", "P2"})
        mock_person_repo.get_by_id.side_effect = lambda pid: next((p for p in sample_persons if p.person_id == pid), None)
        mock_family_repo.get_by_id.side_effect = lambda fid: next((f for f in sample_families if f.family_id == fid), None)
        mock_family_repo.get_families_of_person.return_value = sample_families
        
        request = ExportRequest(
            database_path=Path("test.gwb"),
            options=ExportOptions(keys=["Jean.0 Dupont", "Marie.0 Martin"]),
            validate=False
        )
        
        result = export_use_case.execute(request)
        
        assert result.success is True
        assert result.exported_persons == 2
        mock_selection_service.select_persons_from_options.assert_called_once()
    
    def test_execute_validation_error(self, export_use_case, valid_request):
        """Test exécution avec erreur de validation."""
        # Modifier la requête pour qu'elle soit invalide
        valid_request.database_path = Path("nonexistent.gwb")
        valid_request.validate = True  # Activer la validation

        result = export_use_case.execute(valid_request)

        assert result.success is False
        assert result.error_message is not None
        assert "Base de données non trouvée" in result.error_message
    
    def test_execute_exception(self, export_use_case, mock_selection_service, valid_request):
        """Test exécution avec exception."""
        # Faire lever une exception
        mock_selection_service.select_persons_from_options.side_effect = Exception("Test error")

        result = export_use_case.execute(valid_request)

        assert result.success is False
        assert result.error_message == "Test error"
    
    def test_validate_request_success(self, export_use_case, valid_request):
        """Test validation requête - succès."""
        # Mock pour que le fichier existe
        valid_request.database_path = Mock()
        valid_request.database_path.exists.return_value = True
        
        # Ne devrait pas lever d'exception
        export_use_case._validate_request(valid_request)
    
    def test_validate_request_database_not_found(self, export_use_case, valid_request):
        """Test validation requête - base non trouvée."""
        # Mock pour que le fichier n'existe pas
        valid_request.database_path = Mock()
        valid_request.database_path.exists.return_value = False
        
        with pytest.raises(ValueError, match="Base de données non trouvée"):
            export_use_case._validate_request(valid_request)
    
    def test_validate_request_invalid_options(self, export_use_case, valid_request):
        """Test validation requête - options invalides."""
        valid_request.database_path = Mock()
        valid_request.database_path.exists.return_value = True
        valid_request.options.asc_depth = -1  # Invalide
        
        with pytest.raises(ValueError, match="asc_depth doit être >= 0"):
            export_use_case._validate_request(valid_request)
    
    def test_select_persons_with_criteria(self, export_use_case, mock_selection_service, valid_request):
        """Test sélection des personnes avec critères."""
        mock_selection_service.select_persons.return_value = Mock(person_ids={"P1", "P2"})

        criteria = SelectionCriteria(keys={"Jean.0 Dupont"})
        valid_request.selection = criteria

        result = export_use_case._select_persons(valid_request)

        assert result == {"P1", "P2"}
        mock_selection_service.select_persons.assert_called_once_with(criteria)
    
    def test_select_persons_without_criteria(self, export_use_case, mock_selection_service, valid_request):
        """Test sélection des personnes sans critères."""
        mock_selection_service.select_persons_from_options.return_value = Mock(person_ids={"P1", "P2"})
        
        result = export_use_case._select_persons(valid_request)
        
        assert result == {"P1", "P2"}
        mock_selection_service.select_persons_from_options.assert_called_once_with(valid_request.options)
    
    def test_select_families(self, export_use_case, mock_person_repo, mock_family_repo, sample_persons, sample_families):
        """Test sélection des familles."""
        def mock_get_by_id(person_id):
            for person in sample_persons:
                if person.person_id == person_id:
                    return person
            return None
        
        mock_person_repo.get_by_id.side_effect = mock_get_by_id
        mock_family_repo.get_families_of_person.return_value = sample_families
        
        person_ids = {"P1", "P2"}
        result = export_use_case._select_families(person_ids)
        
        # P1 et P2 devraient avoir des familles
        assert len(result) > 0
    
    def test_apply_export_filters_public_only(self, export_use_case, mock_person_repo, sample_persons):
        """Test application des filtres d'export - public seulement."""
        def mock_get_by_id(person_id):
            for person in sample_persons:
                if person.person_id == person_id:
                    return person
            return None
        
        mock_person_repo.get_by_id.side_effect = mock_get_by_id
        
        person_ids = {"P1", "P2"}
        options = ExportOptions(filter_public=True)
        
        result = export_use_case._apply_export_filters(person_ids, options)
        
        # Toutes les personnes de l'exemple sont publiques
        assert len(result) == 2
        assert "P1" in result
        assert "P2" in result
    
    def test_count_events(self, export_use_case, mock_person_repo, mock_family_repo, sample_persons, sample_families):
        """Test comptage des événements."""
        def mock_get_by_id(person_id):
            for person in sample_persons:
                if person.person_id == person_id:
                    return person
            return None
        
        def mock_get_family_by_id(family_id):
            for family in sample_families:
                if family.family_id == family_id:
                    return family
            return None
        
        mock_person_repo.get_by_id.side_effect = mock_get_by_id
        mock_family_repo.get_by_id.side_effect = mock_get_family_by_id
        
        person_ids = {"P1", "P2"}
        family_ids = {"F1"}
        
        result = export_use_case._count_events(person_ids, family_ids)
        
        # P1 a birth et death, P2 a birth, F1 a marriage
        assert result >= 4
    
    def test_get_export_statistics(self, export_use_case, mock_selection_service, mock_person_repo, mock_family_repo, sample_persons, sample_families):
        """Test récupération des statistiques d'export."""
        # Configuration des mocks
        mock_selection_service.select_persons_from_options.return_value = Mock(person_ids={"P1", "P2"})
        mock_person_repo.get_by_id.side_effect = lambda pid: next((p for p in sample_persons if p.person_id == pid), None)
        mock_family_repo.get_by_id.side_effect = lambda fid: next((f for f in sample_families if f.family_id == fid), None)
        mock_family_repo.get_families_of_person.return_value = sample_families
        
        request = ExportRequest(
            database_path=Path("test.gwb"),
            options=ExportOptions(),
            validate=False
        )
        
        stats = export_use_case.get_export_statistics(request)
        
        assert isinstance(stats, dict)
        assert "total_persons" in stats
        assert "filtered_persons" in stats
        assert "total_families" in stats
        assert "filtered_families" in stats
        assert "total_events" in stats
        assert "selection_type" in stats
        assert stats["total_persons"] == 2
        assert stats["filtered_persons"] == 2
