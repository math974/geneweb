"""Tests pour ConsoleWriter."""

import pytest
from io import StringIO
import sys
from contextlib import redirect_stdout

from geneweb.gwu.adapters.output.console_writer import ConsoleWriter


class TestConsoleWriter:
    """Tests pour ConsoleWriter."""

    def test_log_info_verbose(self):
        """Test log info en mode verbose."""
        writer = ConsoleWriter(verbose=True)
        
        with redirect_stdout(StringIO()) as f:
            writer.log_info("Test message")
        
        output = f.getvalue()
        assert "[INFO] Test message" in output

    def test_log_info_not_verbose(self):
        """Test log info en mode non-verbose."""
        writer = ConsoleWriter(verbose=False)
        
        with redirect_stdout(StringIO()) as f:
            writer.log_info("Test message")
        
        output = f.getvalue()
        assert output == ""

    def test_log_warning(self):
        """Test log warning."""
        writer = ConsoleWriter()
        
        with redirect_stdout(StringIO()) as f:
            writer.log_warning("Test warning")
        
        output = f.getvalue()
        assert "[WARNING] Test warning" in output

    def test_log_error(self):
        """Test log error."""
        writer = ConsoleWriter()
        
        with redirect_stdout(StringIO()) as f:
            writer.log_error("Test error")
        
        output = f.getvalue()
        assert "[ERROR] Test error" in output

    def test_log_progress(self):
        """Test log progress."""
        writer = ConsoleWriter(verbose=True)
        
        with redirect_stdout(StringIO()) as f:
            writer.log_progress(5, 10, "Test operation")
        
        output = f.getvalue()
        assert "[PROGRESS] Test operation: 5/10 (50.0%)" in output

    def test_print_export_statistics(self):
        """Test affichage des statistiques d'export."""
        writer = ConsoleWriter()
        
        with redirect_stdout(StringIO()) as f:
            writer.print_export_statistics(
                exported_persons=10,
                exported_families=5,
                exported_events=25,
                output_files=["file1.gw", "file2.gw"],
                processing_time=1.5
            )
        
        output = f.getvalue()
        assert "STATISTIQUES D'EXPORT" in output
        assert "Personnes exportées: 10" in output
        assert "Familles exportées: 5" in output
        assert "Événements exportés: 25" in output
        assert "Fichiers générés: 2" in output
        assert "Temps de traitement: 1.500s" in output
        assert "file1.gw" in output
        assert "file2.gw" in output

    def test_print_selection_summary(self):
        """Test affichage du résumé de sélection."""
        writer = ConsoleWriter(verbose=True)
        
        with redirect_stdout(StringIO()) as f:
            writer.print_selection_summary(
                selected_persons=2,
                total_persons=100,
                selection_type="keys"
            )
        
        output = f.getvalue()
        assert "Sélection: 2/100 personnes (keys)" in output

    def test_print_validation_errors(self):
        """Test affichage des erreurs de validation."""
        writer = ConsoleWriter()
        
        with redirect_stdout(StringIO()) as f:
            writer.print_validation_errors(["Erreur 1", "Erreur 2"])
        
        output = f.getvalue()
        assert "Erreurs de validation:" in output
        assert "Erreur 1" in output
        assert "Erreur 2" in output

    def test_print_export_start(self):
        """Test affichage du début d'export."""
        writer = ConsoleWriter(verbose=True)
        
        with redirect_stdout(StringIO()) as f:
            writer.print_export_start("output.gw")
        
        output = f.getvalue()
        assert "Début de l'export vers: output.gw" in output

    def test_print_export_complete_success(self):
        """Test affichage de fin d'export (succès)."""
        writer = ConsoleWriter()
        
        with redirect_stdout(StringIO()) as f:
            writer.print_export_complete(success=True)
        
        output = f.getvalue()
        assert "Export terminé avec succès" in output

    def test_print_export_complete_failure(self):
        """Test affichage de fin d'export (échec)."""
        writer = ConsoleWriter()
        
        with redirect_stdout(StringIO()) as f:
            writer.print_export_complete(success=False, message="Test error")
        
        output = f.getvalue()
        assert "Export échoué" in output
        assert "Test error" in output
