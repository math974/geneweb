"""Writer pour la console (affichage des statistiques)."""

from pathlib import Path
from typing import List, Optional


class ConsoleWriter:
    """
    Writer pour l'affichage des statistiques et messages sur la console.
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialise le writer.
        
        Args:
            verbose: Mode verbeux
        """
        self.verbose = verbose
    
    def log_info(self, message: str) -> None:
        """Affiche un message d'information."""
        if self.verbose:
            print(f"[INFO] {message}")
    
    def log_error(self, message: str) -> None:
        """Affiche un message d'erreur."""
        print(f"[ERROR] {message}")
    
    def log_warning(self, message: str) -> None:
        """Affiche un message d'avertissement."""
        print(f"[WARNING] {message}")
    
    def log_debug(self, message: str) -> None:
        """Affiche un message de debug (si mode verbeux)."""
        if self.verbose:
            print(f"[DEBUG] {message}")
    
    
    def print_selection_statistics(
        self,
        selected_persons: int,
        total_persons: int,
        selection_type: str
    ) -> None:
        """
        Affiche les statistiques de sélection.
        
        Args:
            selected_persons: Nombre de personnes sélectionnées
            total_persons: Nombre total de personnes
            selection_type: Type de sélection
        """
        if self.verbose:
            print(f"Sélection: {selected_persons}/{total_persons} personnes ({selection_type})")
    
    def print_progress(self, message: str) -> None:
        """Affiche un message de progression."""
        if self.verbose:
            print(f"[PROGRESS] {message}")
    
    def print_summary(self, message: str) -> None:
        """Affiche un résumé."""
        print(f"\n{message}")
    
    def log_progress(self, current: int, total: int, operation: str) -> None:
        """Affiche un message de progression."""
        if self.verbose:
            percentage = (current / total * 100) if total > 0 else 0
            print(f"[PROGRESS] {operation}: {current}/{total} ({percentage:.1f}%)")
    
    def print_export_statistics(
        self,
        exported_persons: int,
        exported_families: int,
        exported_events: int,
        output_files: List[Path],
        processing_time: float,
        **kwargs
    ) -> None:
        """
        Affiche les statistiques d'export.
        
        Args:
            exported_persons: Nombre de personnes exportées
            exported_families: Nombre de familles exportées
            exported_events: Nombre d'événements exportés
            output_files: Liste des fichiers générés
            processing_time: Temps de traitement en secondes
            **kwargs: Arguments supplémentaires (persons_count, etc.)
        """
        print()
        print("=" * 50)
        print("STATISTIQUES D'EXPORT")
        print("=" * 50)
        print(f"Personnes exportées: {exported_persons}")
        print(f"Familles exportées: {exported_families}")
        print(f"Événements exportés: {exported_events}")
        print(f"Fichiers générés: {len(output_files)}")
        print(f"Temps de traitement: {processing_time:.3f}s")
        
        if output_files:
            print()
            print("Fichiers générés:")
            for file_path in output_files:
                print(f"  - {file_path}")
        
        print("=" * 50)
    
    def print_selection_summary(
        self,
        selected_persons: int,
        total_persons: int,
        selection_type: str,
        **kwargs
    ) -> None:
        """
        Affiche un résumé de sélection.
        
        Args:
            selected_persons: Nombre de personnes sélectionnées
            total_persons: Nombre total de personnes
            selection_type: Type de sélection
            **kwargs: Arguments supplémentaires
        """
        if self.verbose:
            print(f"Sélection: {selected_persons}/{total_persons} personnes ({selection_type})")
    
    def print_validation_errors(self, errors: List[str]) -> None:
        """Affiche les erreurs de validation."""
        if errors:
            print("\n[ERROR] Erreurs de validation:")
            for error in errors:
                print(f"  - {error}")
    
    def print_export_start(self, output_file: str) -> None:
        """Affiche le début de l'export."""
        if self.verbose:
            print(f"[INFO] Début de l'export vers: {output_file}")
    
    def print_export_complete(self, success: bool, message: Optional[str] = None) -> None:
        """Affiche la fin de l'export."""
        if success:
            print("[INFO] Export terminé avec succès")
        else:
            print(f"[ERROR] Export échoué: {message or 'Erreur inconnue'}")