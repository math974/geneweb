"""Tests pour ExportSeparatedUseCase."""

import pytest
from pathlib import Path
from geneweb.gwu.adapters.input.gw_file_repository import GwFileRepository
from geneweb.gwu.use_cases.export_separated import ExportSeparatedUseCase
from geneweb.gwu.domain.config import ExportRequest, ExportOptions


class TestExportSeparated:
    """Tests pour l'export séparé."""
    
    @pytest.fixture
    def galichet_repo(self):
        """Repository pour la base galichet."""
        return GwFileRepository(Path("distribution/bases/galichet.gw"))
    
    @pytest.fixture
    def export_separated_uc(self, galichet_repo):
        """Use case pour l'export séparé."""
        return ExportSeparatedUseCase(
            galichet_repo.persons,
            galichet_repo.families,
            None  # ConsoleWriter
        )
    
    def test_export_single_person(self, export_separated_uc, tmp_path):
        """Test d'export d'une seule personne."""
        options = ExportOptions(
            output_dir=tmp_path,
            keys=["Jean Pierre.0 Galichet"]
        )
        request = ExportRequest(
            database_path=Path("distribution/bases/galichet.gw"),
            options=options,
            validate=False
        )
        
        result = export_separated_uc.execute(request)
        
        # Dans la base galichet, Jean Pierre.0 Galichet existe
        assert result.success
        assert result.exported_persons >= 1
        assert len(result.output_files) >= 1
        
        # Vérifier que le fichier a été créé
        output_file = Path(result.output_files[0])
        assert output_file.exists()
        
        # Vérifier le contenu
        content = output_file.read_text(encoding="utf-8")
        assert "encoding: utf-8" in content
        assert "Jean Pierre" in content
    
    def test_export_multiple_persons(self, export_separated_uc, tmp_path):
        """Test d'export de plusieurs personnes."""
        options = ExportOptions(
            output_dir=tmp_path,
            keys=["Jean Pierre.0 Galichet", "Marie Elisabeth.0 Loche"]
        )
        request = ExportRequest(
            database_path=Path("distribution/bases/galichet.gw"),
            options=options,
            validate=False
        )
        
        result = export_separated_uc.execute(request)
        
        assert result.success
        assert result.exported_persons >= 1  # Au moins une personne trouvée
        assert len(result.output_files) >= 1
    
    def test_export_with_ancestry(self, export_separated_uc, tmp_path):
        """Test d'export avec ascendance."""
        options = ExportOptions(
            output_dir=tmp_path,
            keys=["Jean Pierre.0 Galichet"],
            asc_depth=2
        )
        request = ExportRequest(
            database_path=Path("distribution/bases/galichet.gw"),
            options=options,
            validate=False
        )
        
        result = export_separated_uc.execute(request)
        
        assert result.success
        # Jean Pierre n'a pas de parents, donc seul lui-même
        assert result.exported_persons >= 1
        assert len(result.output_files) >= 1
    
    def test_export_with_descendants(self, export_separated_uc, tmp_path):
        """Test d'export avec descendance."""
        options = ExportOptions(
            output_dir=tmp_path,
            keys=["Jean Pierre.0 Galichet"],
            desc_depth=2
        )
        request = ExportRequest(
            database_path=Path("distribution/bases/galichet.gw"),
            options=options,
            validate=False
        )
        
        result = export_separated_uc.execute(request)
        
        assert result.success
        # Jean Pierre a des descendants
        assert result.exported_persons >= 1
        assert len(result.output_files) >= 1
    
    def test_export_with_combined_depth(self, export_separated_uc, tmp_path):
        """Test d'export avec ascendance+descendance."""
        options = ExportOptions(
            output_dir=tmp_path,
            keys=["Jean Pierre.0 Galichet"],
            asc_desc_depth=2
        )
        request = ExportRequest(
            database_path=Path("distribution/bases/galichet.gw"),
            options=options,
            validate=False
        )
        
        result = export_separated_uc.execute(request)
        
        assert result.success
        # Devrait inclure Jean Pierre + ses descendants
        assert result.exported_persons >= 1
        assert len(result.output_files) >= 1
    
    def test_export_isolated_persons(self, export_separated_uc, tmp_path):
        """Test d'export des personnes isolées."""
        options = ExportOptions(
            output_dir=tmp_path,
            isolated=True
        )
        request = ExportRequest(
            database_path=Path("distribution/bases/galichet.gw"),
            options=options,
            validate=False
        )
        
        result = export_separated_uc.execute(request)
        
        # Dans la base galichet, il n'y a pas de personnes isolées
        # L'export échoue car aucune personne n'est sélectionnée
        assert not result.success
        assert result.exported_persons == 0
        assert len(result.output_files) == 0
        assert "Aucune personne sélectionnée" in result.error_message
    
    def test_export_with_filters(self, export_separated_uc, tmp_path):
        """Test d'export avec filtres."""
        options = ExportOptions(
            output_dir=tmp_path,
            keys=["Jean Pierre.0 Galichet"],
            no_notes=True,
            no_sources=True,
            no_events=True
        )
        request = ExportRequest(
            database_path=Path("distribution/bases/galichet.gw"),
            options=options,
            validate=False
        )
        
        result = export_separated_uc.execute(request)
        
        assert result.success
        assert result.exported_persons >= 1
        # Peut inclure la personne ET la famille
        assert len(result.output_files) >= 1
        
        # Vérifier que les filtres ont été appliqués
        output_file = Path(result.output_files[0])
        content = output_file.read_text(encoding="utf-8")
        assert "notes " not in content
        assert "#src" not in content
        assert "fevt" not in content
        assert "pevt" not in content
    
    def test_export_invalid_person(self, export_separated_uc, tmp_path):
        """Test d'export avec personne invalide."""
        options = ExportOptions(
            output_dir=tmp_path,
            keys=["Personne.Inexistante.999"]
        )
        request = ExportRequest(
            database_path=Path("distribution/bases/galichet.gw"),
            options=options,
            validate=False
        )
        
        result = export_separated_uc.execute(request)
        
        assert not result.success
        assert result.exported_persons == 0
        assert len(result.output_files) == 0
    
    def test_export_no_keys(self, export_separated_uc, tmp_path):
        """Test d'export sans clés spécifiées."""
        options = ExportOptions(
            output_dir=tmp_path
        )
        request = ExportRequest(
            database_path=Path("distribution/bases/galichet.gw"),
            options=options,
            validate=False
        )
        
        result = export_separated_uc.execute(request)
        
        # Devrait exporter toutes les personnes
        assert result.success
        assert result.exported_persons >= 1
        assert len(result.output_files) >= 1
