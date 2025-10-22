"""Use case pour l'export de base de données généalogique."""

from typing import Optional, Set, List
from pathlib import Path
import time

from geneweb.common.types import PersonId, FamilyId
from geneweb.gwu.domain.repositories import PersonRepository, FamilyRepository
from geneweb.gwu.domain.config import ExportRequest, ExportResult, ExportOptions
from geneweb.gwu.domain.services.person_service import PersonService
from geneweb.gwu.domain.services.family_service import FamilyService
from geneweb.gwu.domain.services.selection_service import SelectionService
from geneweb.gwu.adapters.output.gw_writer import GwWriter, GwWriterOptions


class ExportDatabaseUseCase:
    """
    Use case: Exporter une base de données généalogique.
    
    Orchestre l'export complet d'une base de données selon les options gwu.
    """
    
    def __init__(
        self,
        person_repository: PersonRepository,
        family_repository: FamilyRepository,
        selection_service: SelectionService,
        database: Optional[object] = None
    ):
        """
        Initialise le use case.
        
        Args:
            person_repository: Repository pour accéder aux personnes
            family_repository: Repository pour accéder aux familles
            selection_service: Service de sélection
            database: Base de données complète (optionnel)
        """
        self.person_repository = person_repository
        self.family_repository = family_repository
        self.selection_service = selection_service
        self.database = database
        self.person_service = PersonService(person_repository)
        self.family_service = FamilyService(person_repository, family_repository)
    
    def execute(self, request: ExportRequest) -> ExportResult:
        """
        Exécute l'export avec les options données.
        
        Args:
            request: Requête d'export (options, filtres, etc.)
        
        Returns:
            ExportResult: Résultat de l'export (succès, stats, etc.)
        """
        start_time = time.time()
        
        try:
            # 1. Valider la requête
            if request.validate:
                self._validate_request(request)
            
            # 2. Sélectionner les personnes à exporter
            selected_persons = self._select_persons(request)
            
            # 3. Sélectionner les familles à exporter
            selected_families = self._select_families(selected_persons)
            
            # 4. Appliquer les filtres d'export
            filtered_persons = self._apply_export_filters(selected_persons, request.options)
            filtered_families = self._apply_export_filters_families(selected_families, request.options)
            
            # 5. Calculer les statistiques
            exported_events = self._count_events(filtered_persons, filtered_families)
            
            # 6. Convertir les IDs en objets
            person_objects = []
            for person_id in filtered_persons:
                person = self.person_repository.get_by_id(person_id)
                if person:
                    person_objects.append(person)
            
            # Respecter l'ordre des familles du repository
            family_objects = []
            all_families = list(self.family_repository.get_all())
            for family in all_families:
                if family.family_id in filtered_families:
                    family_objects.append(family)
            
            # Récupérer toutes les personnes pour les familles (père et mère)
            all_person_objects = list(self.person_repository.get_all())
            
            # 7. Écrire les fichiers de sortie
            output_files = []
            if request.output_file:
                self._write_output_file(request.output_file, person_objects, family_objects, request.options, self.database, all_person_objects)
                output_files.append(request.output_file)
            elif request.output_dir:
                # Pour l'instant, on ne génère qu'un seul fichier
                output_file = request.output_dir / "export.gw"
                self._write_output_file(output_file, person_objects, family_objects, request.options, self.database, all_person_objects)
                output_files.append(output_file)
            
            # 7. Calculer le temps de traitement
            processing_time = time.time() - start_time
            
            # 8. Créer le résultat
            result = ExportResult(
                success=True,
                exported_persons=len(filtered_persons),
                exported_families=len(filtered_families),
                exported_events=exported_events,
                output_files=output_files,
                processing_time=processing_time
            )
            
            return result
        
        except Exception as e:
            processing_time = time.time() - start_time
            return ExportResult(
                success=False,
                error_message=str(e),
                processing_time=processing_time
            )
    
    def _validate_request(self, request: ExportRequest) -> None:
        """
        Valide la requête d'export.
        
        Args:
            request: Requête à valider
        
        Raises:
            ValueError: Si la requête est invalide
        """
        # Validation de la base de données
        if not request.database_path.exists():
            raise ValueError(f"Base de données non trouvée: {request.database_path}")
        
        # Validation des options de sortie
        if request.output_file and request.output_dir:
            raise ValueError("output_file et output_dir sont mutuellement exclusifs")
        
        # Validation des options d'export
        if request.options.asc_depth is not None and request.options.asc_depth < 0:
            raise ValueError("asc_depth doit être >= 0")
        
        if request.options.desc_depth is not None and request.options.desc_depth < 0:
            raise ValueError("desc_depth doit être >= 0")
        
        if request.options.asc_desc_depth is not None and request.options.asc_desc_depth < 0:
            raise ValueError("asc_desc_depth doit être >= 0")
    
    def _select_persons(self, request: ExportRequest) -> Set[PersonId]:
        """
        Sélectionne les personnes à exporter.
        
        Args:
            request: Requête d'export
        
        Returns:
            Set des IDs des personnes sélectionnées
        """
        if request.selection:
            # Utiliser les critères de sélection spécifiés
            selection_result = self.selection_service.select_persons(request.selection)
            return selection_result.person_ids
        else:
            # Utiliser les options d'export pour la sélection
            selection_result = self.selection_service.select_persons_from_options(request.options)
            return selection_result.person_ids
    
    def _select_families(self, person_ids: Set[PersonId]) -> Set[str]:
        """
        Sélectionne les familles à exporter basées sur les personnes sélectionnées.
        
        Args:
            person_ids: IDs des personnes sélectionnées
        
        Returns:
            Set des IDs des familles sélectionnées
        """
        family_ids = set()
        
        for person_id in person_ids:
            person = self.person_repository.get_by_id(person_id)
            if not person:
                continue
            
            # Ajouter la famille des parents
            if person.parents:
                family_ids.add(person.parents)
            
            # Ajouter les familles où cette personne est parent
            families = self.family_repository.get_families_of_person(person_id)
            for family in families:
                family_ids.add(family.family_id)
        
        return family_ids
    
    def _apply_export_filters(
        self, 
        person_ids: Set[PersonId], 
        options: ExportOptions
    ) -> Set[PersonId]:
        """
        Applique les filtres d'export aux personnes.
        
        Args:
            person_ids: IDs des personnes à filtrer
            options: Options d'export
        
        Returns:
            Set des IDs des personnes filtrées
        """
        filtered_ids = set()
        
        for person_id in person_ids:
            person = self.person_repository.get_by_id(person_id)
            if not person:
                continue
            
            # Filtre public/privé
            if options.filter_public and not person.is_public():
                continue
            
            if options.filter_private and person.is_public():
                continue
            
            filtered_ids.add(person_id)
        
        return filtered_ids
    
    def _apply_export_filters_families(
        self, 
        family_ids: Set[str], 
        options: ExportOptions
    ) -> Set[str]:
        """
        Applique les filtres d'export aux familles.
        
        Args:
            family_ids: IDs des familles à filtrer
            options: Options d'export
        
        Returns:
            Set des IDs des familles filtrées
        """
        # Pour l'instant, pas de filtres spécifiques aux familles
        # TODO: Implémenter les filtres de familles si nécessaire
        return family_ids
    
    def _count_events(
        self, 
        person_ids: Set[PersonId], 
        family_ids: Set[str]
    ) -> int:
        """
        Compte le nombre total d'événements.
        
        Args:
            person_ids: IDs des personnes
            family_ids: IDs des familles
        
        Returns:
            Nombre total d'événements
        """
        event_count = 0
        
        # Compter les événements des personnes
        for person_id in person_ids:
            person = self.person_repository.get_by_id(person_id)
            if not person:
                continue
            
            # Événements principaux
            if person.birth:
                event_count += 1
            if person.baptism:
                event_count += 1
            if person.death:
                event_count += 1
            if person.burial:
                event_count += 1
            if person.cremation:
                event_count += 1
            
            # Événements additionnels
            event_count += len(person.events)
        
        # Compter les événements des familles
        for family_id in family_ids:
            family = self.family_repository.get_by_id(family_id)
            if not family:
                continue
            
            # Événements d'union
            if family.marriage:
                event_count += 1
            if family.marriage_bann:
                event_count += 1
            if family.marriage_contract:
                event_count += 1
            if family.marriage_license:
                event_count += 1
            if family.engagement:
                event_count += 1
            
            # Événements de séparation
            if family.divorce:
                event_count += 1
            if family.separated:
                event_count += 1
            if family.annulment:
                event_count += 1
            
            # Événements additionnels
            event_count += len(family.events)
        
        return event_count
    
    def get_export_statistics(self, request: ExportRequest) -> dict:
        """
        Retourne les statistiques d'export sans exécuter l'export.
        
        Args:
            request: Requête d'export
        
        Returns:
            Dictionnaire avec les statistiques
        """
        # Sélectionner les personnes
        selected_persons = self._select_persons(request)
        
        # Sélectionner les familles
        selected_families = self._select_families(selected_persons)
        
        # Appliquer les filtres
        filtered_persons = self._apply_export_filters(selected_persons, request.options)
        filtered_families = self._apply_export_filters_families(selected_families, request.options)
        
        # Compter les événements
        event_count = self._count_events(filtered_persons, filtered_families)
        
        return {
            "total_persons": len(selected_persons),
            "filtered_persons": len(filtered_persons),
            "total_families": len(selected_families),
            "filtered_families": len(filtered_families),
            "total_events": event_count,
            "selection_type": self.selection_service._get_selection_type(
                self.selection_service._options_to_criteria(request.options)
            )
        }
    
    def _write_output_file(
        self,
        output_file: Path,
        persons: List,
        families: List,
        options: ExportOptions,
        database: Optional[object] = None,
        all_persons: Optional[List] = None
    ) -> None:
        """
        Écrit les données exportées dans un fichier .gw.
        
        Args:
            output_file: Fichier de sortie
            persons: Liste des personnes à exporter
            families: Liste des familles à exporter
            options: Options d'export
            database: Base de données complète (optionnel)
        """
        # Créer les options du writer
        writer_options = GwWriterOptions(
            encoding=options.encoding,
            gw_plus=options.gw_plus,
            old_gw=options.old_gw,
            no_notes=options.no_notes,
            no_sources=options.no_sources,
            no_events=options.no_events
        )
        
        # Créer le writer et écrire
        writer = GwWriter(writer_options)
        # Utiliser toutes les personnes pour les familles (père et mère)
        all_persons_for_families = all_persons if all_persons is not None else persons
        writer.write_database(persons, families, output_file, database=self.database, all_persons=all_persons_for_families)
