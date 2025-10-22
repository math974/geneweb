"""
Tests unitaires pour les gestionnaires GW.
"""

import pytest
from geneweb.gwu.adapters.output.gw_notes_manager import GwNotesManager
from geneweb.gwu.adapters.output.gw_pevents_manager import GwPeventsManager
from geneweb.gwu.adapters.output.gw_page_ext_manager_enhanced import GwPageExtManagerEnhanced
from geneweb.gwu.adapters.output.gw_header_manager import GwHeaderManager
from geneweb.gwu.adapters.output.gw_family_manager import GwFamilyManager
from geneweb.gwu.adapters.output.gw_writer import GwWriterOptions


class TestGwNotesManager:
    """Tests pour GwNotesManager."""
    
    def test_init(self):
        """Test de l'initialisation."""
        manager = GwNotesManager(GwWriterOptions())
        assert manager is not None
    
    def test_get_ordered_persons_with_notes(self, sample_persons, sample_families):
        """Test de l'ordre des personnes avec notes."""
        manager = GwNotesManager(GwWriterOptions())
        
        # Toutes les personnes ont des notes dans les fixtures
        ordered_persons = manager.get_ordered_persons_with_notes(sample_families, sample_persons)
        
        assert len(ordered_persons) == len(sample_persons)
        assert all(person.has_notes() for person in ordered_persons)
    
    def test_process_person_notes(self, sample_person):
        """Test du traitement des notes d'une personne."""
        manager = GwNotesManager(GwWriterOptions())
        
        processed_notes = manager.process_person_notes(sample_person)
        
        assert isinstance(processed_notes, list)
        assert len(processed_notes) > 0
        assert all(isinstance(note, str) for note in processed_notes)


class TestGwPeventsManager:
    """Tests pour GwPeventsManager."""
    
    def test_init(self):
        """Test de l'initialisation."""
        manager = GwPeventsManager(GwWriterOptions())
        assert manager is not None
    
    def test_get_persons_with_pevents(self, sample_persons, sample_families):
        """Test de la récupération des personnes avec événements."""
        manager = GwPeventsManager(GwWriterOptions())
        
        persons_with_pevents = manager.get_ordered_persons_with_pevents(sample_families, sample_persons)
        
        assert isinstance(persons_with_pevents, list)
        # Toutes les personnes de test ont des événements (birth)
        assert len(persons_with_pevents) == len(sample_persons)
    
    def test_format_pevent_person(self, sample_person):
        """Test du formatage d'une personne pevt."""
        manager = GwPeventsManager(GwWriterOptions())
        
        formatted = manager.format_person_pevents(sample_person)
        
        assert isinstance(formatted, list)
        assert len(formatted) > 0
        assert all(isinstance(line, str) for line in formatted)


class TestGwPageExtManagerEnhanced:
    """Tests pour GwPageExtManagerEnhanced."""
    
    def test_init(self):
        """Test de l'initialisation."""
        manager = GwPageExtManagerEnhanced()
        assert manager is not None
    
    def test_collect_page_ext_files(self, sample_persons, sample_families):
        """Test de la collecte des fichiers page-ext."""
        manager = GwPageExtManagerEnhanced()
        
        files = manager.collect_page_ext_files(sample_families, sample_persons)
        
        assert isinstance(files, list)
        # Les fichiers de test devraient être collectés
        assert len(files) > 0
    
    def test_format_page_ext_section(self):
        """Test du formatage d'une section page-ext."""
        manager = GwPageExtManagerEnhanced()
        
        file_name = "test.txt"
        content = "Contenu de test"
        
        formatted = manager.format_page_ext_section(file_name, content)
        
        assert isinstance(formatted, list)
        assert len(formatted) > 0
        assert all(isinstance(line, str) for line in formatted)


class TestGwHeaderManager:
    """Tests pour GwHeaderManager."""
    
    def test_init(self):
        """Test de l'initialisation."""
        manager = GwHeaderManager(GwWriterOptions())
        assert manager is not None
    
    def test_generate_header(self):
        """Test de la génération de l'en-tête."""
        manager = GwHeaderManager(GwWriterOptions())
        
        header = manager.get_header_info()
        
        assert isinstance(header, dict)
        assert 'encoding' in header
        assert 'has_encoding' in header
        assert 'has_gwplus' in header
        
        # Vérifier les valeurs
        assert header['encoding'] == 'UTF-8'
        assert isinstance(header['has_encoding'], bool)
        assert isinstance(header['has_gwplus'], bool)


class TestGwFamilyManager:
    """Tests pour GwFamilyManager."""
    
    def test_init(self):
        """Test de l'initialisation."""
        manager = GwFamilyManager(GwWriterOptions())
        assert manager is not None
    
    def test_get_isolated_families(self, sample_persons, sample_families):
        """Test de la récupération des familles isolées."""
        manager = GwFamilyManager(GwWriterOptions())
        
        all_families = manager.get_all_families(sample_families, sample_persons)
        
        assert isinstance(all_families, list)
        # Toutes les familles de test devraient être présentes
        assert len(all_families) >= len(sample_families)
    
    def test_format_family(self, sample_family, sample_persons):
        """Test du formatage d'une famille."""
        manager = GwFamilyManager(GwWriterOptions())
        
        formatted = manager.format_family_section(sample_family, sample_persons)
        
        assert isinstance(formatted, list)
        assert len(formatted) > 0
        assert all(isinstance(line, str) for line in formatted)
