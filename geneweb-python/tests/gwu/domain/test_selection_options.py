"""Tests pour les options de sélection avancées."""

import pytest
from pathlib import Path
from geneweb.gwu.adapters.input.gw_file_repository import GwFileRepository
from geneweb.gwu.domain.services.selection_service import SelectionService
from geneweb.gwu.domain.config import SelectionCriteria


class TestSelectionOptions:
    """Tests pour les options de sélection avancées."""
    
    @pytest.fixture
    def galichet_repo(self):
        """Repository pour la base galichet."""
        return GwFileRepository(Path("distribution/bases/galichet.gw"))
    
    @pytest.fixture
    def selection_service(self, galichet_repo):
        """Service de sélection."""
        return SelectionService(galichet_repo.persons, galichet_repo.families)
    
    def test_selection_by_key(self, selection_service):
        """Test de sélection par clé de personne."""
        criteria = SelectionCriteria(keys={"Jean Pierre.0 Galichet"})
        result = selection_service.select_persons(criteria)
        
        assert result.total_selected == 1
        assert len(result.person_ids) == 1
        
        # Vérifier que la personne sélectionnée est bien Jean Pierre
        person = selection_service.person_repository.get_by_key("Jean Pierre", "Galichet", 0)
        assert person is not None
        assert person.person_id in result.person_ids
    
    def test_selection_by_multiple_keys(self, selection_service):
        """Test de sélection par plusieurs clés."""
        criteria = SelectionCriteria(keys={
            "Jean Pierre.0 Galichet",
            "Marie Elisabeth.0 Loche"
        })
        result = selection_service.select_persons(criteria)
        
        assert result.total_selected == 2
        assert len(result.person_ids) == 2
    
    def test_selection_by_surname(self, selection_service):
        """Test de sélection par patronyme."""
        # Pour l'instant, on teste avec une sélection manuelle
        # car notre implémentation n'a pas encore de méthode pour sélectionner par patronyme
        criteria = SelectionCriteria(keys={"Jean Pierre.0 Galichet"})
        result = selection_service.select_persons(criteria)
        
        # Vérifier que la personne sélectionnée a le bon patronyme
        person = selection_service.person_repository.get_by_key("Jean Pierre", "Galichet", 0)
        assert person is not None
        assert person.surname == "Galichet"
    
    def test_selection_ancestry_depth_2(self, selection_service):
        """Test de sélection avec ascendance profondeur 2."""
        criteria = SelectionCriteria(
            keys={"Jean Pierre.0 Galichet"},
            asc_depth=2
        )
        result = selection_service.select_persons(criteria)
        
        # Jean Pierre n'a pas de parents, donc seul lui-même devrait être sélectionné
        assert result.total_selected == 1
        assert len(result.person_ids) == 1
    
    def test_selection_descendants_depth_2(self, selection_service):
        """Test de sélection avec descendance profondeur 2."""
        criteria = SelectionCriteria(
            keys={"Jean Pierre.0 Galichet"},
            desc_depth=2
        )
        result = selection_service.select_persons(criteria)
        
        # Jean Pierre a des descendants, donc plus d'une personne devrait être sélectionnée
        assert result.total_selected > 1
        assert len(result.person_ids) > 1
    
    def test_selection_ancestry_and_descendants_depth_2(self, selection_service):
        """Test de sélection avec ascendance+descendance profondeur 2."""
        criteria = SelectionCriteria(
            keys={"Jean Pierre.0 Galichet"},
            asc_desc_depth=2
        )
        result = selection_service.select_persons(criteria)
        
        # Devrait inclure Jean Pierre + ses descendants
        assert result.total_selected > 1
        assert len(result.person_ids) > 1
    
    def test_selection_isolated_persons(self, selection_service):
        """Test de sélection des personnes isolées."""
        criteria = SelectionCriteria(isolated_only=True)
        result = selection_service.select_persons(criteria)
        
        # Dans la base galichet, il n'y a pas de personnes vraiment isolées
        # car toutes ont soit des parents, soit des conjoints
        assert result.total_selected == 0
        assert len(result.person_ids) == 0
    
    def test_selection_public_persons(self, selection_service):
        """Test de sélection des personnes publiques."""
        criteria = SelectionCriteria(public_only=True)
        result = selection_service.select_persons(criteria)
        
        # Toutes les personnes devraient être publiques par défaut
        assert result.total_selected > 0
        assert len(result.person_ids) > 0
    
    def test_selection_private_persons(self, selection_service):
        """Test de sélection des personnes privées."""
        criteria = SelectionCriteria(private_only=True)
        result = selection_service.select_persons(criteria)
        
        # Il ne devrait pas y avoir de personnes privées dans la base galichet
        assert result.total_selected == 0
        assert len(result.person_ids) == 0
    
    def test_selection_with_events(self, selection_service):
        """Test de sélection des personnes avec événements."""
        criteria = SelectionCriteria(with_events=True)
        result = selection_service.select_persons(criteria)
        
        # Dans la base galichet, les personnes n'ont pas d'événements individuels
        # donc aucune personne ne devrait être sélectionnée
        assert result.total_selected == 0
        assert len(result.person_ids) == 0
    
    def test_selection_with_notes(self, selection_service):
        """Test de sélection des personnes avec notes."""
        criteria = SelectionCriteria(with_notes=True)
        result = selection_service.select_persons(criteria)
        
        # Dans la base galichet, les personnes n'ont pas de notes individuelles
        # donc aucune personne ne devrait être sélectionnée
        assert result.total_selected == 0
        assert len(result.person_ids) == 0
    
    def test_selection_with_sources(self, selection_service):
        """Test de sélection des personnes avec sources."""
        criteria = SelectionCriteria(with_sources=True)
        result = selection_service.select_persons(criteria)
        
        # Dans la base galichet, les personnes n'ont pas de sources individuelles
        # donc aucune personne ne devrait être sélectionnée
        assert result.total_selected == 0
        assert len(result.person_ids) == 0
    
    def test_selection_combined_criteria(self, selection_service):
        """Test de sélection avec critères combinés."""
        criteria = SelectionCriteria(
            keys={"Jean Pierre.0 Galichet"},
            desc_depth=1,
            with_events=False  # Pas d'événements dans galichet
        )
        result = selection_service.select_persons(criteria)
        
        # Devrait inclure Jean Pierre + ses descendants directs
        assert result.total_selected > 1
        assert len(result.person_ids) > 1
    
    def test_selection_empty_criteria(self, selection_service):
        """Test de sélection avec critères vides."""
        criteria = SelectionCriteria()
        result = selection_service.select_persons(criteria)
        
        # Devrait sélectionner toutes les personnes
        assert result.total_selected > 0
        assert len(result.person_ids) > 0
    
    def test_selection_invalid_key(self, selection_service):
        """Test de sélection avec clé invalide."""
        criteria = SelectionCriteria(keys={"Personne.Inexistante.999"})
        result = selection_service.select_persons(criteria)
        
        # Ne devrait sélectionner aucune personne
        assert result.total_selected == 0
        assert len(result.person_ids) == 0
