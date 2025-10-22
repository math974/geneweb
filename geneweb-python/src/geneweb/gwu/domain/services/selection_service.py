"""Service pour la sélection et le filtrage des personnes."""

from typing import List, Optional, Set, Iterator
from dataclasses import dataclass

from geneweb.common.types import PersonId
from geneweb.gwu.domain.entities import Person
from geneweb.gwu.domain.repositories import PersonRepository, FamilyRepository
from geneweb.gwu.domain.config import SelectionCriteria, ExportOptions
from geneweb.gwu.domain.services.person_service import PersonService
from geneweb.gwu.domain.services.family_service import FamilyService


@dataclass
class SelectionResult:
    """Résultat de sélection."""
    
    person_ids: Set[PersonId]
    total_selected: int
    selection_type: str
    
    def __len__(self) -> int:
        """Retourne le nombre de personnes sélectionnées."""
        return len(self.person_ids)
    
    def get_persons(self, person_service: PersonService) -> List[Person]:
        """
        Récupère les personnes sélectionnées.
        
        Args:
            person_service: Service pour récupérer les personnes
        
        Returns:
            Liste des personnes
        """
        persons = []
        for person_id in self.person_ids:
            person = person_service.get_person_by_id(person_id)
            if person:
                persons.append(person)
        return persons


class SelectionService:
    """
    Service pour la sélection et le filtrage des personnes.
    
    Implémente la logique de sélection selon les options gwu :
    - Sélection par clé (-k)
    - Sélection ascendance/descendance (-a, -d, -ad)
    - Sélection par parenté (--parentship)
    - Sélection personnes isolées (--isolated)
    """
    
    def __init__(
        self,
        person_repository: PersonRepository,
        family_repository: FamilyRepository
    ):
        """
        Initialise le service.
        
        Args:
            person_repository: Repository pour accéder aux personnes
            family_repository: Repository pour accéder aux familles
        """
        self.person_repository = person_repository
        self.family_repository = family_repository
        self.person_service = PersonService(person_repository)
        self.family_service = FamilyService(person_repository, family_repository)
    
    def select_persons(
        self, 
        criteria: SelectionCriteria
    ) -> SelectionResult:
        """
        Sélectionne les personnes selon les critères.
        
        Args:
            criteria: Critères de sélection
        
        Returns:
            Résultat de sélection
        """
        if criteria.is_empty():
            # Pas de critères = toutes les personnes
            all_persons = list(self.person_repository.get_all())
            person_ids = {p.person_id for p in all_persons}
            return SelectionResult(
                person_ids=person_ids,
                total_selected=len(person_ids),
                selection_type="all"
            )
        
        selected_ids = set()
        
        # Sélection par clés
        if criteria.keys:
            key_ids = self._select_by_keys(criteria.keys)
            selected_ids.update(key_ids)
        
        # Sélection par profondeur
        if (criteria.asc_depth is not None or 
            criteria.desc_depth is not None or 
            criteria.asc_desc_depth is not None):
            depth_ids = self._select_by_depth(criteria)
            selected_ids.update(depth_ids)
        
        # Sélection par parenté
        if criteria.parentship:
            parentship_ids = self._select_by_parentship(criteria)
            selected_ids.update(parentship_ids)
        
        # Sélection personnes isolées
        if criteria.isolated_only:
            isolated_ids = self._select_isolated_persons()
            selected_ids.update(isolated_ids)
        
        # Si pas de sélection spécifique, prendre toutes les personnes
        # Sauf si on a spécifiquement demandé les personnes isolées ou des clés spécifiques
        if not selected_ids and not criteria.isolated_only and not criteria.keys:
            all_persons = list(self.person_repository.get_all())
            selected_ids = {p.person_id for p in all_persons}
        
        # Appliquer les filtres
        filtered_ids = self._apply_filters(selected_ids, criteria)
        
        return SelectionResult(
            person_ids=filtered_ids,
            total_selected=len(filtered_ids),
            selection_type=self._get_selection_type(criteria)
        )
    
    def select_persons_from_options(
        self, 
        options: ExportOptions
    ) -> SelectionResult:
        """
        Sélectionne les personnes à partir des options d'export.
        
        Args:
            options: Options d'export gwu
        
        Returns:
            Résultat de sélection
        """
        # Convertir les options en critères
        criteria = self._options_to_criteria(options)
        return self.select_persons(criteria)
    
    def _select_by_keys(self, keys: Set[str]) -> Set[PersonId]:
        """
        Sélectionne les personnes par clés.
        
        Args:
            keys: Set des clés (Prénom.occ NOM)
        
        Returns:
            Set des IDs des personnes sélectionnées
        """
        selected_ids = set()
        
        for key in keys:
            person = self._parse_key_to_person(key)
            if person:
                selected_ids.add(person.person_id)
        
        return selected_ids
    
    def _select_by_depth(self, criteria: SelectionCriteria) -> Set[PersonId]:
        """
        Sélectionne les personnes par profondeur d'ascendance/descendance.
        
        Args:
            criteria: Critères de sélection
        
        Returns:
            Set des IDs des personnes sélectionnées
        """
        selected_ids = set()
        
        # Si on a des clés, utiliser ces personnes comme racines
        if criteria.keys:
            root_person_ids = self._select_by_keys(criteria.keys)
        else:
            # Sinon, utiliser toutes les personnes comme racines possibles
            root_person_ids = {p.person_id for p in self.person_repository.get_all()}
        
        for person_id in root_person_ids:
            # Calculer ascendance et descendance
            if criteria.asc_desc_depth is not None:
                # Profondeur combinée
                related_ids = self.family_service.get_ancestors_and_descendants(
                    person_id, 
                    criteria.asc_desc_depth, 
                    criteria.asc_desc_depth
                )
            else:
                # Profondeurs séparées
                asc_depth = criteria.asc_depth or 0
                desc_depth = criteria.desc_depth or 0
                related_ids = self.family_service.get_ancestors_and_descendants(
                    person_id, 
                    asc_depth, 
                    desc_depth
                )
            
            selected_ids.update(related_ids)
        
        return selected_ids
    
    def _select_by_keys(self, keys: Set[str]) -> Set[PersonId]:
        """
        Sélectionne les personnes par leurs clés.
        
        Args:
            keys: Set des clés de personnes (format: "Prénom.occ NOM")
        
        Returns:
            Set des IDs des personnes sélectionnées
        """
        selected_ids = set()
        
        for key in keys:
            person = self._parse_key_to_person(key)
            if person:
                selected_ids.add(person.person_id)
        
        return selected_ids
    
    def _select_by_parentship(self, criteria: SelectionCriteria) -> Set[PersonId]:
        """
        Sélectionne les personnes impliquées dans le calcul de parenté.
        
        Args:
            criteria: Critères de sélection
        
        Returns:
            Set des IDs des personnes sélectionnées
        """
        selected_ids = set()
        
        if not criteria.keys or len(criteria.keys) < 2:
            # Pas assez de clés pour calculer la parenté
            return selected_ids
        
        # Prendre les deux premières clés pour le calcul de parenté
        key_list = list(criteria.keys)
        person1 = self._parse_key_to_person(key_list[0])
        person2 = self._parse_key_to_person(key_list[1])
        
        if person1 and person2:
            related_ids = self.family_service.get_related_persons(
                person1.person_id, 
                person2.person_id
            )
            selected_ids.update(related_ids)
        
        return selected_ids
    
    def _select_isolated_persons(self) -> Set[PersonId]:
        """
        Sélectionne les personnes isolées.
        
        Returns:
            Set des IDs des personnes isolées
        """
        isolated_persons = list(self.person_repository.get_isolated_persons())
        return {p.person_id for p in isolated_persons}
    
    def _apply_filters(
        self, 
        person_ids: Set[PersonId], 
        criteria: SelectionCriteria
    ) -> Set[PersonId]:
        """
        Applique les filtres aux personnes sélectionnées.
        
        Args:
            person_ids: IDs des personnes à filtrer
            criteria: Critères de filtrage
        
        Returns:
            Set des IDs des personnes filtrées
        """
        filtered_ids = set()
        
        for person_id in person_ids:
            person = self.person_repository.get_by_id(person_id)
            if not person:
                continue
            
            # Filtre d'accès
            if criteria.public_only and not person.is_public():
                continue
            
            if criteria.private_only and person.is_public():
                continue
            
            # Filtre de contenu
            if criteria.with_events and not person.has_events():
                continue
            
            if criteria.with_notes and not person.has_notes():
                continue
            
            if criteria.with_sources and not person.has_sources():
                continue
            
            filtered_ids.add(person_id)
        
        return filtered_ids
    
    def _options_to_criteria(self, options: ExportOptions) -> SelectionCriteria:
        """
        Convertit les options d'export en critères de sélection.
        
        Args:
            options: Options d'export
        
        Returns:
            Critères de sélection
        """
        return SelectionCriteria(
            keys=set(options.keys) if options.keys is not None else set(),
            asc_depth=options.asc_depth,
            desc_depth=options.desc_depth,
            asc_desc_depth=options.asc_desc_depth,
            parentship=options.parentship,
            isolated_only=options.isolated,
            public_only=options.filter_public,
            private_only=options.filter_private,
            with_events=not options.no_events if options.no_events else False,  # Inverser no_events
            with_notes=not options.no_notes if options.no_notes else False,  # Inverser no_notes
            with_sources=not options.no_sources if options.no_sources else False  # Inverser no_sources
        )
    
    def _parse_key_to_person(self, key: str) -> Optional[Person]:
        """
        Parse une clé (Prénom.occ NOM) et retourne la personne.
        
        Args:
            key: Clé au format "Prénom.occ NOM"
        
        Returns:
            Personne ou None si non trouvée
        """
        try:
            # Séparer prénom.occ et nom
            # Le format est "Prénom.occ NOM" où le prénom peut contenir des espaces
            # On cherche le dernier espace pour séparer prénom.occ et nom
            last_space_index = key.rfind(' ')
            if last_space_index == -1:
                return None
            
            first_name_with_occ = key[:last_space_index]
            surname = key[last_space_index + 1:]
            
            # Séparer prénom et occurrence
            if "." in first_name_with_occ:
                name_parts = first_name_with_occ.split(".")
                first_name = name_parts[0]
                try:
                    occ = int(name_parts[1])
                except (ValueError, IndexError):
                    occ = 0
            else:
                first_name = first_name_with_occ
                occ = 0
            
            return self.person_repository.get_by_key(first_name, surname, occ)
        
        except Exception:
            return None
    
    def _get_selection_type(self, criteria: SelectionCriteria) -> str:
        """
        Détermine le type de sélection utilisé.
        
        Args:
            criteria: Critères de sélection
        
        Returns:
            Type de sélection
        """
        if criteria.keys:
            if criteria.parentship:
                return "parentship"
            elif criteria.asc_depth is not None or criteria.desc_depth is not None:
                return "ancestry_descendants"
            else:
                return "keys"
        elif criteria.isolated_only:
            return "isolated"
        elif criteria.asc_depth is not None or criteria.desc_depth is not None:
            return "ancestry_descendants"
        else:
            return "all"
