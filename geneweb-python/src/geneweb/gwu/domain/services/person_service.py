"""Service pour la gestion des personnes."""

from typing import List, Optional, Set, Iterator
from dataclasses import dataclass

from geneweb.common.types import PersonId, Sex, AccessLevel
from geneweb.gwu.domain.entities import Person
from geneweb.gwu.domain.repositories import PersonRepository
from geneweb.gwu.domain.config import SelectionCriteria


@dataclass
class PersonSearchResult:
    """Résultat de recherche de personnes."""
    
    persons: List[Person]
    total_count: int
    filtered_count: int
    
    def __len__(self) -> int:
        """Retourne le nombre de personnes trouvées."""
        return len(self.persons)


class PersonService:
    """
    Service pour la gestion des personnes.
    
    Fournit la logique métier pour :
    - Recherche et filtrage des personnes
    - Gestion des relations familiales
    - Validation des données
    """
    
    def __init__(self, person_repository: PersonRepository):
        """
        Initialise le service.
        
        Args:
            person_repository: Repository pour accéder aux personnes
        """
        self.person_repository = person_repository
    
    def get_person_by_id(self, person_id: PersonId) -> Optional[Person]:
        """
        Récupère une personne par son ID.
        
        Args:
            person_id: ID de la personne
        
        Returns:
            La personne ou None si non trouvée
        """
        return self.person_repository.get_by_id(person_id)
    
    def get_person_by_key(
        self, first_name: str, surname: str, occ: int
    ) -> Optional[Person]:
        """
        Récupère une personne par sa clé (Prénom.occ NOM).
        
        Args:
            first_name: Prénom
            surname: Nom de famille
            occ: Occurrence
        
        Returns:
            La personne ou None si non trouvée
        """
        return self.person_repository.get_by_key(first_name, surname, occ)
    
    def search_persons(
        self, 
        search_term: str, 
        limit: Optional[int] = None
    ) -> PersonSearchResult:
        """
        Recherche des personnes par nom.
        
        Args:
            search_term: Terme de recherche
            limit: Limite du nombre de résultats
        
        Returns:
            Résultat de recherche
        """
        persons = self.person_repository.search_by_name(search_term)
        
        if limit:
            persons = persons[:limit]
        
        return PersonSearchResult(
            persons=persons,
            total_count=len(persons),
            filtered_count=len(persons)
        )
    
    def get_all_persons(self) -> Iterator[Person]:
        """
        Récupère toutes les personnes.
        
        Returns:
            Itérateur sur les personnes
        """
        return self.person_repository.get_all()
    
    def get_persons_by_criteria(
        self, 
        criteria: SelectionCriteria
    ) -> PersonSearchResult:
        """
        Récupère les personnes selon des critères de sélection.
        
        Args:
            criteria: Critères de sélection
        
        Returns:
            Résultat de recherche
        """
        if criteria.is_empty():
            # Pas de critères = toutes les personnes
            all_persons = list(self.person_repository.get_all())
            return PersonSearchResult(
                persons=all_persons,
                total_count=len(all_persons),
                filtered_count=len(all_persons)
            )
        
        selected_persons = set()
        
        # Sélection par clés
        if criteria.keys:
            for key in criteria.keys:
                person = self._parse_key_to_person(key)
                if person:
                    selected_persons.add(person.person_id)
        
        # Sélection par profondeur (déléguée à FamilyService)
        if (criteria.asc_depth is not None or 
            criteria.desc_depth is not None or 
            criteria.asc_desc_depth is not None):
            # Cette logique sera implémentée dans FamilyService
            # Pour l'instant, on récupère toutes les personnes
            all_persons = list(self.person_repository.get_all())
            for person in all_persons:
                selected_persons.add(person.person_id)
        
        # Sélection personnes isolées
        if criteria.isolated_only:
            isolated = list(self.person_repository.get_isolated_persons())
            for person in isolated:
                selected_persons.add(person.person_id)
        
        # Si pas de sélection spécifique, prendre toutes les personnes
        if not selected_persons:
            all_persons = list(self.person_repository.get_all())
            for person in all_persons:
                selected_persons.add(person.person_id)
        
        # Appliquer les filtres
        filtered_persons = []
        for person_id in selected_persons:
            person = self.person_repository.get_by_id(person_id)
            if person and self._matches_filters(person, criteria):
                filtered_persons.append(person)
        
        return PersonSearchResult(
            persons=filtered_persons,
            total_count=len(selected_persons),
            filtered_count=len(filtered_persons)
        )
    
    def get_persons_by_sex(self, sex: Sex) -> List[Person]:
        """
        Récupère les personnes par sexe.
        
        Args:
            sex: Sexe recherché
        
        Returns:
            Liste des personnes
        """
        persons = []
        for person in self.person_repository.get_all():
            if person.sex == sex:
                persons.append(person)
        return persons
    
    def get_persons_by_access_level(self, access_level: AccessLevel) -> List[Person]:
        """
        Récupère les personnes par niveau d'accès.
        
        Args:
            access_level: Niveau d'accès recherché
        
        Returns:
            Liste des personnes
        """
        persons = []
        for person in self.person_repository.get_all():
            if person.access == access_level:
                persons.append(person)
        return persons
    
    def get_public_persons(self) -> List[Person]:
        """
        Récupère les personnes publiques.
        
        Returns:
            Liste des personnes publiques
        """
        return self.get_persons_by_access_level(AccessLevel.PUBLIC)
    
    def get_private_persons(self) -> List[Person]:
        """
        Récupère les personnes privées.
        
        Returns:
            Liste des personnes privées
        """
        return self.get_persons_by_access_level(AccessLevel.PRIVATE)
    
    def get_persons_with_events(self) -> List[Person]:
        """
        Récupère les personnes ayant des événements.
        
        Returns:
            Liste des personnes avec événements
        """
        persons = []
        for person in self.person_repository.get_all():
            if person.has_events():
                persons.append(person)
        return persons
    
    def get_persons_with_notes(self) -> List[Person]:
        """
        Récupère les personnes ayant des notes.
        
        Returns:
            Liste des personnes avec notes
        """
        persons = []
        for person in self.person_repository.get_all():
            if person.has_notes():
                persons.append(person)
        return persons
    
    def get_persons_with_sources(self) -> List[Person]:
        """
        Récupère les personnes ayant des sources.
        
        Returns:
            Liste des personnes avec sources
        """
        persons = []
        for person in self.person_repository.get_all():
            if person.has_sources():
                persons.append(person)
        return persons
    
    def get_person_count(self) -> int:
        """
        Retourne le nombre total de personnes.
        
        Returns:
            Nombre de personnes
        """
        return self.person_repository.get_count()
    
    def validate_person(self, person: Person) -> List[str]:
        """
        Valide une personne et retourne les erreurs.
        
        Args:
            person: Personne à valider
        
        Returns:
            Liste des erreurs de validation
        """
        errors = []
        
        # Validation des champs obligatoires
        if not person.first_name or not person.first_name.strip():
            errors.append("Le prénom est obligatoire")
        
        if not person.surname or not person.surname.strip():
            errors.append("Le nom de famille est obligatoire")
        
        if person.occ < 0:
            errors.append("L'occurrence ne peut pas être négative")
        
        # Validation des relations
        if person.parents and not self.person_repository.get_by_id(person.parents):
            errors.append(f"Famille parent non trouvée: {person.parents}")
        
        for family_id in person.spouses:
            if not self.person_repository.get_by_id(family_id):
                errors.append(f"Famille conjoint non trouvée: {family_id}")
        
        return errors
    
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
            parts = key.split()
            if len(parts) < 2:
                return None
            
            first_name_with_occ = parts[0]
            surname = parts[1]
            
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
    
    def _matches_filters(self, person: Person, criteria: SelectionCriteria) -> bool:
        """
        Vérifie si une personne correspond aux filtres.
        
        Args:
            person: Personne à vérifier
            criteria: Critères de filtrage
        
        Returns:
            True si la personne correspond
        """
        # Filtre d'accès
        if criteria.public_only and not person.is_public():
            return False
        
        if criteria.private_only and person.is_public():
            return False
        
        # Filtre de contenu
        if criteria.with_events and not person.has_events():
            return False
        
        if criteria.with_notes and not person.has_notes():
            return False
        
        if criteria.with_sources and not person.has_sources():
            return False
        
        return True
