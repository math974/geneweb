"""Interface CLI principale pour GWU."""

import argparse
import sys
from pathlib import Path
from typing import Optional, List

from geneweb.gwu.domain.config import ExportOptions, ExportRequest
from geneweb.gwu.adapters.input.gw_file_repository import GwFileRepository
from geneweb.gwu.adapters.output.console_writer import ConsoleWriter
from geneweb.gwu.use_cases.export_database import ExportDatabaseUseCase
from geneweb.gwu.use_cases.export_selection import ExportSelectionUseCase
from geneweb.gwu.use_cases.export_separated import ExportSeparatedUseCase
from geneweb.gwu.use_cases.export_to_directory import ExportToDirectoryUseCase


class GwuCLI:
    """
    Interface CLI pour GWU.
    
    Gère le parsing des arguments, la configuration,
    et l'orchestration des use cases.
    """

    def __init__(self):
        """Initialise l'interface CLI."""
        self.parser = self._create_parser()
        self.console_writer = ConsoleWriter(verbose=False)

    def run(self, args: Optional[List[str]] = None) -> int:
        """
        Exécute l'interface CLI.
        
        Args:
            args: Arguments de la ligne de commande (None pour sys.argv)
            
        Returns:
            Code de sortie (0 = succès, 1 = erreur)
        """
        try:
            # Parser les arguments
            parsed_args = self.parser.parse_args(args)
            
            # Configurer le mode verbose
            self.console_writer.verbose = parsed_args.verbose
            
            # Valider les arguments
            if not self._validate_args(parsed_args):
                return 1
            
            # Créer les options d'export
            options = self._create_export_options(parsed_args)
            
            # Charger la base de données
            if not parsed_args.database_path.exists():
                self.console_writer.log_error(f"Base de données non trouvée: {parsed_args.database_path}")
                return 1
            
            # Créer les repositories
            repository = GwFileRepository(parsed_args.database_path)
            
            # Créer les services
            from geneweb.gwu.domain.services.selection_service import SelectionService
            selection_service = SelectionService(repository.persons, repository.families)
            
            # Créer les use cases
            export_database_uc = ExportDatabaseUseCase(
                repository.persons,
                repository.families,
                selection_service,
                repository.database
            )
            
            export_selection_uc = ExportSelectionUseCase(
                repository.persons,
                repository.families,
                self.console_writer
            )
            
            export_separated_uc = ExportSeparatedUseCase(
                repository.persons,
                repository.families,
                self.console_writer
            )
            
            export_directory_uc = ExportToDirectoryUseCase(
                repository.persons,
                repository.families,
                self.console_writer
            )
            
            # Créer les critères de sélection si nécessaire
            selection = None
            if parsed_args.key:
                from geneweb.gwu.domain.config import SelectionCriteria
                selection = SelectionCriteria(keys=set(parsed_args.key))
            elif parsed_args.separate_persons:
                from geneweb.gwu.domain.config import SelectionCriteria
                selection = SelectionCriteria(keys={parsed_args.separate_persons})
            
            # Créer la requête d'export
            request = ExportRequest(
                database_path=parsed_args.database_path,
                options=options,
                output_file=parsed_args.output,
                output_dir=parsed_args.odir,
                selection=selection,
                validate=True
            )
            
            # Exécuter l'export approprié
            if parsed_args.separate_persons:
                result = export_separated_uc.execute(request)
            elif parsed_args.odir:
                result = export_directory_uc.execute(request)
            else:
                result = export_database_uc.execute(request)
            
            # Afficher le résultat
            if result.success:
                self.console_writer.print_export_statistics(
                    result.exported_persons,
                    result.exported_families,
                    result.exported_events,
                    result.output_files,
                    result.processing_time
                )
                return 0
            else:
                self.console_writer.log_error(result.error_message or "Export échoué")
                return 1
                
        except KeyboardInterrupt:
            self.console_writer.log_info("Export interrompu par l'utilisateur")
            return 1
        except Exception as e:
            self.console_writer.log_error(f"Erreur inattendue: {str(e)}")
            return 1

    def _create_parser(self) -> argparse.ArgumentParser:
        """Crée le parser d'arguments."""
        parser = argparse.ArgumentParser(
            description="GWU - GeneWeb Unweb (Version Python)",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # Arguments obligatoires
        parser.add_argument(
            "database_path",
            type=Path,
            help="Chemin vers la base de données .gwb"
        )
        
        # Options de sortie
        output_group = parser.add_argument_group("Options de sortie")
        output_group.add_argument(
            "-o", "--output",
            type=Path,
            help="Fichier de sortie"
        )
        output_group.add_argument(
            "--odir",
            type=Path,
            help="Répertoire de sortie"
        )
        output_group.add_argument(
            "-sep", "--separate-persons",
            nargs="?",
            const="",
            help="Séparer les personnes en fichiers individuels (optionnel: clé de personne)"
        )
        
        # Options de sélection
        selection_group = parser.add_argument_group("Options de sélection")
        selection_group.add_argument(
            "-k", "--key",
            action="append",
            help="Clé de personne (Prénom.occ NOM)"
        )
        selection_group.add_argument(
            "-a", "--asc",
            type=int,
            help="Profondeur d'ascendance"
        )
        selection_group.add_argument(
            "-d", "--desc",
            type=int,
            help="Profondeur de descendance"
        )
        selection_group.add_argument(
            "-ad",
            type=int,
            help="Profondeur ascendance+descendance"
        )
        selection_group.add_argument(
            "--parentship",
            action="store_true",
            help="Sélection par liens de parenté"
        )
        selection_group.add_argument(
            "--isolated",
            action="store_true",
            help="Inclure personnes isolées"
        )
        
        # Options de filtrage
        filter_group = parser.add_argument_group("Options de filtrage")
        filter_group.add_argument(
            "-p", "--public",
            action="store_true",
            help="Afficher seulement les personnes publiques"
        )
        filter_group.add_argument(
            "-P", "--private",
            action="store_true",
            help="Afficher seulement les personnes privées"
        )
        filter_group.add_argument(
            "--no-notes",
            action="store_true",
            help="Ne pas inclure les notes"
        )
        filter_group.add_argument(
            "--no-src",
            action="store_true",
            help="Ne pas inclure les sources"
        )
        filter_group.add_argument(
            "--no-evt",
            action="store_true",
            help="Ne pas inclure les événements"
        )
        
        # Options de format
        format_group = parser.add_argument_group("Options de format")
        format_group.add_argument(
            "--gwplus",
            action="store_true",
            help="Utiliser le format gwplus"
        )
        format_group.add_argument(
            "-enc", "--encoding",
            default="UTF-8",
            help="Encodage de sortie (défaut: UTF-8)"
        )
        format_group.add_argument(
            "--old-gw",
            action="store_true",
            help="Utiliser le format .gw ancien"
        )
        
        # Options générales
        general_group = parser.add_argument_group("Options générales")
        general_group.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="Mode verbeux"
        )
        general_group.add_argument(
            "--version",
            action="version",
            version="GWU Python 1.0.0"
        )
        
        return parser

    def _validate_args(self, args) -> bool:
        """Valide les arguments."""
        # Vérifier les options mutuellement exclusives
        if args.public and args.private:
            self.console_writer.log_error("Les options --public et --private sont mutuellement exclusives")
            return False
        
        if args.output and args.odir:
            self.console_writer.log_error("Les options --output et --odir sont mutuellement exclusives")
            return False
        
        # Vérifier les profondeurs
        if args.asc is not None and args.asc < 0:
            self.console_writer.log_error("La profondeur d'ascendance doit être >= 0")
            return False
        
        if args.desc is not None and args.desc < 0:
            self.console_writer.log_error("La profondeur de descendance doit être >= 0")
            return False
        
        if args.ad is not None and args.ad < 0:
            self.console_writer.log_error("La profondeur combinée doit être >= 0")
            return False
        
        return True

    def _create_export_options(self, args) -> ExportOptions:
        """Crée les options d'export à partir des arguments."""
        return ExportOptions(
            output_file=args.output,
            output_dir=args.odir,
            keys=args.key or [],
            asc_depth=args.asc,
            desc_depth=args.desc,
            asc_desc_depth=args.ad,
            parentship=args.parentship,
            isolated=args.isolated,
            separate_persons=[args.separate_persons] if args.separate_persons else [],
            filter_public=args.public,
            filter_private=args.private,
            no_notes=args.no_notes,
            no_sources=args.no_src,
            no_events=args.no_evt,
            # Forcer gwplus par défaut (désactivé uniquement avec --old-gw)
            gw_plus=(not args.old_gw),
            encoding=args.encoding,
            old_gw=args.old_gw
        )
