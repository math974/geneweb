"""
Tests fonctionnels pour l'export GW.
"""

import pytest
import tempfile
import os
from pathlib import Path
from geneweb.gwu.adapters.input.gw_file_repository import GwFilePersonRepository, GwFileFamilyRepository
from geneweb.gwu.adapters.output.gw_writer_clean import GwWriterClean
from geneweb.gwu.adapters.output.gw_writer import GwWriterOptions


class TestGwExport:
    """Tests fonctionnels pour l'export GW."""
    
    def test_export_simple_person(self, sample_person, gw_writer_options):
        """Test d'export d'une personne simple."""
        writer = GwWriterClean(gw_writer_options)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_file = f.name
        
        try:
            with open(temp_file, 'w') as f:
                writer.write_database(f, [], [sample_person])
            
            # Vérifier que le fichier a été créé
            assert os.path.exists(temp_file)
            
            # Vérifier le contenu
            with open(temp_file, 'r') as f:
                content = f.read()
            
            # Vérifier la présence des sections principales
            assert "#gwplus" in content
            assert "#encoding" in content
            assert "#charset" in content
            assert "#version" in content
            assert "#base" in content
            
            # Vérifier la présence des notes de la personne
            assert "notes Dupont Jean" in content
            assert "Notes de test pour Jean Dupont" in content
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_export_simple_family(self, sample_family, sample_persons, gw_writer_options):
        """Test d'export d'une famille simple."""
        writer = GwWriterClean(gw_writer_options)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_file = f.name
        
        try:
            with open(temp_file, 'w') as f:
                writer.write_database(f, [sample_family], sample_persons)
            
            # Vérifier que le fichier a été créé
            assert os.path.exists(temp_file)
            
            # Vérifier le contenu
            with open(temp_file, 'r') as f:
                content = f.read()
            
            # Vérifier la présence des sections principales
            assert "#gwplus" in content
            assert "#encoding" in content
            assert "#charset" in content
            assert "#version" in content
            assert "#base" in content
            
            # Vérifier la présence de la famille
            assert "fam" in content
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_export_with_events(self, gw_writer_options):
        """Test d'export avec événements."""
        # Créer une personne avec événements
        person = Person(
            id="P1", surname="Dupont", first_name="Jean", occ=0,
            birth=Date(1980, 1, 15), death=Date(2020, 12, 31),
            notes="Notes avec événements", events=[]
        )
        
        writer = GwWriterClean(gw_writer_options)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_file = f.name
        
        try:
            with open(temp_file, 'w') as f:
                writer.write_database(f, [], [person])
            
            # Vérifier le contenu
            with open(temp_file, 'r') as f:
                content = f.read()
            
            # Vérifier la présence des événements
            assert "pevt Dupont Jean" in content
            assert "#birt 15/1/1980" in content
            assert "#deat 31/12/2020" in content
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_export_with_notes(self, gw_writer_options):
        """Test d'export avec notes."""
        # Créer une personne avec notes
        person = Person(
            id="P1", surname="Dupont", first_name="Jean", occ=0,
            birth=None, death=None, notes="Notes détaillées avec [[[liens]]]",
            events=[]
        )
        
        writer = GwWriterClean(gw_writer_options)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_file = f.name
        
        try:
            with open(temp_file, 'w') as f:
                writer.write_database(f, [], [person])
            
            # Vérifier le contenu
            with open(temp_file, 'r') as f:
                content = f.read()
            
            # Vérifier la présence des notes
            assert "notes Dupont Jean" in content
            assert "beg" in content
            assert "Notes détaillées avec [[[liens]]]" in content
            assert "end notes" in content
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_export_with_family_notes(self, gw_writer_options):
        """Test d'export avec notes de famille."""
        # Créer une famille avec notes
        family = Family(
            id="F1", father_id="P1", mother_id="P2", children_ids=["P3"],
            marriage=Event("marr", Date(2000, 6, 15)),
            notes="Notes de famille avec [[[liens]]]"
        )
        
        writer = GwWriterClean(gw_writer_options)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_file = f.name
        
        try:
            with open(temp_file, 'w') as f:
                writer.write_database(f, [family], [])
            
            # Vérifier le contenu
            with open(temp_file, 'r') as f:
                content = f.read()
            
            # Vérifier la présence des notes de famille
            assert "fam" in content
            assert "Notes de famille avec [[[liens]]]" in content
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_export_empty_database(self, gw_writer_options):
        """Test d'export d'une base de données vide."""
        writer = GwWriterClean(gw_writer_options)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_file = f.name
        
        try:
            with open(temp_file, 'w') as f:
                writer.write_database(f, [], [])
            
            # Vérifier que le fichier a été créé
            assert os.path.exists(temp_file)
            
            # Vérifier le contenu
            with open(temp_file, 'r') as f:
                content = f.read()
            
            # Vérifier la présence des sections principales
            assert "#gwplus" in content
            assert "#encoding" in content
            assert "#charset" in content
            assert "#version" in content
            assert "#base" in content
            
            # Vérifier l'absence de données
            assert "fam " not in content
            assert "pevt " not in content
            assert "notes " not in content
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
