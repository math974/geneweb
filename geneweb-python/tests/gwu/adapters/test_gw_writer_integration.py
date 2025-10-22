"""Tests d'intégration pour GwWriter."""

import pytest
from pathlib import Path
from geneweb.gwu.adapters.input.gw_file_repository import GwFileRepository
from geneweb.gwu.adapters.output.gw_writer import GwWriter, GwWriterOptions
from geneweb.gwu.domain.config import ExportOptions


class TestGwWriterIntegration:
    """Tests d'intégration pour GwWriter avec la base galichet."""
    
    @pytest.fixture
    def galichet_repo(self):
        """Repository pour la base galichet."""
        return GwFileRepository(Path("distribution/bases/galichet.gw"))
    
    @pytest.fixture
    def writer_options(self):
        """Options par défaut pour le writer."""
        return GwWriterOptions()
    
    def test_write_galichet_database(self, galichet_repo, writer_options, tmp_path):
        """Test d'écriture de la base galichet complète."""
        # Récupérer les données
        persons = list(galichet_repo.persons.get_all())
        families = list(galichet_repo.families.get_all())
        
        # Créer le writer et écrire
        writer = GwWriter(writer_options)
        output_file = tmp_path / "galichet_test.gw"
        writer.write_database(persons, families, output_file)
        
        # Vérifier que le fichier a été créé
        assert output_file.exists()
        
        # Vérifier le contenu
        content = output_file.read_text(encoding="utf-8")
        assert "encoding: utf-8" in content
        assert "fam " in content
        assert "beg" in content
        assert "end" in content
        
        # Vérifier le nombre de familles
        fam_count = content.count("fam ")
        assert fam_count > 0
        
        # Vérifier le nombre de blocs beg/end
        beg_count = content.count("beg")
        end_count = content.count("end")
        assert beg_count == end_count
    
    def test_write_with_gwplus(self, galichet_repo, tmp_path):
        """Test d'écriture avec l'option gwplus."""
        persons = list(galichet_repo.persons.get_all())
        families = list(galichet_repo.families.get_all())
        
        options = GwWriterOptions(gw_plus=True)
        writer = GwWriter(options)
        output_file = tmp_path / "galichet_gwplus.gw"
        writer.write_database(persons, families, output_file)
        
        content = output_file.read_text(encoding="utf-8")
        assert "encoding: utf-8" in content
        assert "gwplus" in content
    
    def test_write_without_events(self, galichet_repo, tmp_path):
        """Test d'écriture sans événements."""
        persons = list(galichet_repo.persons.get_all())
        families = list(galichet_repo.families.get_all())
        
        options = GwWriterOptions(no_events=True)
        writer = GwWriter(options)
        output_file = tmp_path / "galichet_no_events.gw"
        writer.write_database(persons, families, output_file)
        
        content = output_file.read_text(encoding="utf-8")
        assert "encoding: utf-8" in content
        assert "fevt" not in content
        assert "pevt" not in content
    
    def test_write_without_notes(self, galichet_repo, tmp_path):
        """Test d'écriture sans notes."""
        persons = list(galichet_repo.persons.get_all())
        families = list(galichet_repo.families.get_all())
        
        options = GwWriterOptions(no_notes=True)
        writer = GwWriter(options)
        output_file = tmp_path / "galichet_no_notes.gw"
        writer.write_database(persons, families, output_file)
        
        content = output_file.read_text(encoding="utf-8")
        assert "encoding: utf-8" in content
        assert "notes " not in content
    
    def test_write_without_sources(self, galichet_repo, tmp_path):
        """Test d'écriture sans sources."""
        persons = list(galichet_repo.persons.get_all())
        families = list(galichet_repo.families.get_all())
        
        options = GwWriterOptions(no_sources=True)
        writer = GwWriter(options)
        output_file = tmp_path / "galichet_no_sources.gw"
        writer.write_database(persons, families, output_file)
        
        content = output_file.read_text(encoding="utf-8")
        assert "encoding: utf-8" in content
        assert "#src" not in content
        assert "src " not in content
    
    def test_write_old_gw_format(self, galichet_repo, tmp_path):
        """Test d'écriture en format ancien."""
        persons = list(galichet_repo.persons.get_all())
        families = list(galichet_repo.families.get_all())
        
        options = GwWriterOptions(old_gw=True)
        writer = GwWriter(options)
        output_file = tmp_path / "galichet_old_gw.gw"
        writer.write_database(persons, families, output_file)
        
        content = output_file.read_text(encoding="utf-8")
        assert "encoding: utf-8" in content
        # Le format ancien pourrait avoir des différences spécifiques
        # Pour l'instant, on vérifie juste que le fichier est créé
        assert len(content) > 0
    
    def test_write_encoding_utf8(self, galichet_repo, tmp_path):
        """Test d'écriture avec encodage UTF-8."""
        persons = list(galichet_repo.persons.get_all())
        families = list(galichet_repo.families.get_all())
        
        options = GwWriterOptions(encoding="UTF-8")
        writer = GwWriter(options)
        output_file = tmp_path / "galichet_utf8.gw"
        writer.write_database(persons, families, output_file)
        
        content = output_file.read_text(encoding="utf-8")
        assert "encoding: utf-8" in content
    
    def test_write_encoding_ascii(self, galichet_repo, tmp_path):
        """Test d'écriture avec encodage ASCII."""
        persons = list(galichet_repo.persons.get_all())
        families = list(galichet_repo.families.get_all())
        
        options = GwWriterOptions(encoding="ASCII")
        writer = GwWriter(options)
        output_file = tmp_path / "galichet_ascii.gw"
        writer.write_database(persons, families, output_file)
        
        content = output_file.read_text(encoding="ascii")
        assert "encoding: ascii" in content
