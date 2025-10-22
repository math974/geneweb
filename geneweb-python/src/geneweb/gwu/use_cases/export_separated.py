"""Use case pour export séparé."""

from pathlib import Path
from typing import Set, List, Optional

from geneweb.common.types import PersonId, FamilyId
from geneweb.gwu.domain.entities import Person, Family
from geneweb.gwu.domain.config import ExportRequest, ExportResult
from geneweb.gwu.domain.repositories import PersonRepository, FamilyRepository
from geneweb.gwu.domain.services.selection_service import SelectionService
from geneweb.gwu.adapters.output.separated_writer import SeparatedWriter
from geneweb.gwu.adapters.output.console_writer import ConsoleWriter


class ExportSeparatedUseCase:
    """
    Use case: Exporter avec séparation.
    
    Exporte les données en fichiers séparés par personne ou par famille
    selon les options spécifiées.
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
        Exécute l'export avec séparation.
        
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
            
            # 4. Déterminer le répertoire de sortie
            if request.options.output_dir:
                output_dir = request.options.output_dir
            else:
                output_dir = Path("separated_export")
            
            # 5. Exporter avec séparation
            writer = SeparatedWriter(request.options, self.console_writer)
            output_files = writer.write_separated(
                output_dir,
                persons,
                families,
                selected_person_ids,
                selected_family_ids
            )
            
            # 6. Statistiques
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
                error_message=f"Erreur lors de l'export séparé: {str(e)}"
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
