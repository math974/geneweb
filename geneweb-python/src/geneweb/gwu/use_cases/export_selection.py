"""Use case pour export avec sélection."""

from pathlib import Path
from typing import Set, List, Optional

from geneweb.common.types import PersonId, FamilyId
from geneweb.gwu.domain.entities import Person, Family
from geneweb.gwu.domain.config import ExportRequest, ExportResult, SelectionCriteria
from geneweb.gwu.domain.repositories import PersonRepository, FamilyRepository
from geneweb.gwu.domain.services.selection_service import SelectionService
from geneweb.gwu.adapters.output.gw_file_writer import GwFileWriter
from geneweb.gwu.adapters.output.console_writer import ConsoleWriter


class ExportSelectionUseCase:
    """
    Use case: Exporter avec sélection personnalisée.
    
    Permet d'exporter des données avec des critères de sélection
    spécifiques et des options d'export avancées.
    """

    def __init__(
        self,
        person_repository: PersonRepository,
        family_repository: FamilyRepository,
        console_writer: Optional[ConsoleWriter] = None
    ):
        """
        Initialise le use case.
        
        Args:
            person_repository: Repository pour accéder aux personnes
            family_repository: Repository pour accéder aux familles
            console_writer: Writer console pour logs
        """
        self.person_repository = person_repository
        self.family_repository = family_repository
        self.selection_service = SelectionService(person_repository, family_repository)
        self.console_writer = console_writer or ConsoleWriter()

    def execute(self, request: ExportRequest) -> ExportResult:
        """
        Exécute l'export avec sélection.
        
        Args:
            request: Requête d'export
            
        Returns:
            Résultat de l'export
        """
        try:
            # 1. Sélectionner les personnes
            if request.selection:
                selection_result = self.selection_service.select_persons(request.selection)
            else:
                selection_result = self.selection_service.select_persons_from_options(request.options)
            
            selected_person_ids = selection_result.person_ids
            
            if not selected_person_ids:
                return ExportResult(
                    success=False,
                    exported_persons=0,
                    error_message="Aucune personne sélectionnée pour l'export"
                )
            
            # 2. Sélectionner les familles associées
            selected_family_ids = self._select_related_families(selected_person_ids)
            
            # 3. Récupérer les données
            persons = [self.person_repository.get_by_id(pid) for pid in selected_person_ids]
            persons = [p for p in persons if p is not None]
            
            families = [self.family_repository.get_by_id(fid) for fid in selected_family_ids]
            families = [f for f in families if f is not None]
            
            # 4. Exporter
            if request.options.output_dir:
                # Export vers répertoire
                from geneweb.gwu.adapters.output.directory_writer import DirectoryWriter
                writer = DirectoryWriter(request.options, self.console_writer)
                output_files = writer.write_to_directory(
                    request.options.output_dir,
                    persons,
                    families,
                    selected_person_ids,
                    selected_family_ids
                )
            else:
                # Export vers fichier unique
                writer = GwFileWriter(request.options)
                output_file = request.options.output_file or Path("output.gw")
                writer.write_database(
                    output_file,
                    persons,
                    families,
                    selected_person_ids,
                    selected_family_ids
                )
                output_files = [str(output_file)]
            
            # 5. Statistiques
            events_count = sum(len(p.events) for p in persons) + sum(len(f.events) for f in families)
            
            return ExportResult(
                success=True,
                exported_persons=len(persons),
                exported_families=len(families),
                exported_events=events_count,
                output_files=output_files
            )
            
        except Exception as e:
            return ExportResult(
                success=False,
                exported_persons=0,
                error_message=f"Erreur lors de l'export: {str(e)}"
            )

    def _select_related_families(self, person_ids: Set[PersonId]) -> Set[FamilyId]:
        """Sélectionne les familles liées aux personnes."""
        family_ids = set()
        
        for person_id in person_ids:
            # Familles où la personne est parent
            families_as_parent = self.family_repository.get_families_of_person(person_id)
            for family in families_as_parent:
                family_ids.add(family.family_id)
            
            # Famille des parents de la personne
            person = self.person_repository.get_by_id(person_id)
            if person and person.parents:
                family_ids.add(person.parents)
        
        return family_ids
