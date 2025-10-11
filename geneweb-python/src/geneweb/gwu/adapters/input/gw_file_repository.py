"""Repository pour fichiers .gw (implémentation des interfaces du domaine)."""

from pathlib import Path
from typing import Optional, List, Iterator

from geneweb.common.types import PersonId, FamilyId
from geneweb.gwu.domain.entities import Person, Family
from geneweb.gwu.domain.repositories import PersonRepository, FamilyRepository
from geneweb.gwu.adapters.input.gw_parser import GwParser, GwDatabase


class GwFilePersonRepository(PersonRepository):
    """
    Implémentation de PersonRepository pour fichiers .gw.
    
    Utilise GwParser en interne pour lire et parser le fichier .gw.
    """
    
    def __init__(self, file_path: Path):
        """
        Initialise le repository avec un fichier .gw.
        
        Args:
            file_path: Chemin du fichier .gw
        """
        self.file_path = file_path
        self.parser = GwParser()
        self.database: Optional[GwDatabase] = None
        self._load()
    
    def _load(self) -> None:
        """Charge le fichier .gw."""
        self.database = self.parser.parse_file(self.file_path)
    
    def get_by_id(self, person_id: PersonId) -> Optional[Person]:
        """
        Récupère une personne par son ID.
        
        Args:
            person_id: ID de la personne
        
        Returns:
            La personne ou None si non trouvée
        """
        if not self.database:
            return None
        
        return self.database.persons.get(person_id)
    
    def get_by_key(self, first_name: str, surname: str, occ: int) -> Optional[Person]:
        """
        Récupère une personne par sa clé (prénom.occ nom).
        
        Args:
            first_name: Prénom
            surname: Nom de famille
            occ: Occurrence
        
        Returns:
            La personne ou None si non trouvée
        """
        if not self.database:
            return None
        
        for person in self.database.persons.values():
            if (person.first_name == first_name and
                person.surname == surname and
                person.occ == occ):
                return person
        
        return None
    
    def get_all(self) -> Iterator[Person]:
        """
        Récupère toutes les personnes de la base.
        
        Returns:
            Itérateur sur les personnes
        """
        if not self.database:
            return iter([])
        
        return iter(self.database.persons.values())
    
    def get_count(self) -> int:
        """
        Retourne le nombre total de personnes.
        
        Returns:
            Nombre de personnes
        """
        if not self.database:
            return 0
        
        return len(self.database.persons)
    
    def search_by_name(self, search_term: str) -> List[Person]:
        """
        Recherche des personnes par nom (prénom ou nom de famille).
        
        Args:
            search_term: Terme de recherche
        
        Returns:
            Liste des personnes correspondantes
        """
        if not self.database:
            return []
        
        search_lower = search_term.lower()
        results = []
        
        for person in self.database.persons.values():
            if (search_lower in person.first_name.lower() or
                search_lower in person.surname.lower()):
                results.append(person)
        
        return results
    
    def get_isolated_persons(self) -> Iterator[Person]:
        """
        Récupère les personnes isolées (sans parents ni conjoints).
        
        Returns:
            Itérateur sur les personnes isolées
        """
        if not self.database:
            return iter([])
        
        isolated = [p for p in self.database.persons.values() if p.is_isolated()]
        return iter(isolated)
    
    def save(self, person: Person) -> None:
        """
        Sauvegarde une personne.
        
        Note: Non implémenté pour GwFileRepository (lecture seule).
        
        Args:
            person: Personne à sauvegarder
        """
        raise NotImplementedError("GwFileRepository est en lecture seule")
    
    def save_all(self, persons: Iterator[Person]) -> None:
        """
        Sauvegarde plusieurs personnes.
        
        Note: Non implémenté pour GwFileRepository (lecture seule).
        
        Args:
            persons: Itérateur de personnes à sauvegarder
        """
        raise NotImplementedError("GwFileRepository est en lecture seule")


class GwFileFamilyRepository(FamilyRepository):
    """
    Implémentation de FamilyRepository pour fichiers .gw.
    
    Utilise GwParser en interne pour lire et parser le fichier .gw.
    """
    
    def __init__(self, file_path: Path):
        """
        Initialise le repository avec un fichier .gw.
        
        Args:
            file_path: Chemin du fichier .gw
        """
        self.file_path = file_path
        self.parser = GwParser()
        self.database: Optional[GwDatabase] = None
        self._load()
    
    def _load(self) -> None:
        """Charge le fichier .gw."""
        self.database = self.parser.parse_file(self.file_path)
    
    def get_by_id(self, family_id: FamilyId) -> Optional[Family]:
        """
        Récupère une famille par son ID.
        
        Args:
            family_id: ID de la famille
        
        Returns:
            La famille ou None si non trouvée
        """
        if not self.database:
            return None
        
        for family in self.database.families:
            if family.family_id == family_id:
                return family
        
        return None
    
    def get_all(self) -> Iterator[Family]:
        """
        Récupère toutes les familles de la base.
        
        Returns:
            Itérateur sur les familles
        """
        if not self.database:
            return iter([])
        
        return iter(self.database.families)
    
    def get_count(self) -> int:
        """
        Retourne le nombre total de familles.
        
        Returns:
            Nombre de familles
        """
        if not self.database:
            return 0
        
        return len(self.database.families)
    
    def get_families_of_person(self, person_id: PersonId) -> List[Family]:
        """
        Récupère les familles où une personne est parent.
        
        Args:
            person_id: ID de la personne
        
        Returns:
            Liste des familles
        """
        if not self.database:
            return []
        
        families = []
        for family in self.database.families:
            if family.father_id == person_id or family.mother_id == person_id:
                families.append(family)
        
        return families
    
    def get_family_of_parents(
        self, father_id: PersonId, mother_id: PersonId
    ) -> Optional[Family]:
        """
        Récupère la famille formée par un père et une mère.
        
        Args:
            father_id: ID du père
            mother_id: ID de la mère
        
        Returns:
            La famille ou None si non trouvée
        """
        if not self.database:
            return None
        
        for family in self.database.families:
            if family.father_id == father_id and family.mother_id == mother_id:
                return family
        
        return None
    
    def save(self, family: Family) -> None:
        """
        Sauvegarde une famille.
        
        Note: Non implémenté pour GwFileFamilyRepository (lecture seule).
        
        Args:
            family: Famille à sauvegarder
        """
        raise NotImplementedError("GwFileFamilyRepository est en lecture seule")
    
    def save_all(self, families: Iterator[Family]) -> None:
        """
        Sauvegarde plusieurs familles.
        
        Note: Non implémenté pour GwFileFamilyRepository (lecture seule).
        
        Args:
            families: Itérateur de familles à sauvegarder
        """
        raise NotImplementedError("GwFileFamilyRepository est en lecture seule")


class GwFileRepository:
    """
    Repository combiné pour accès aux personnes et familles d'un fichier .gw.
    
    Fournit un accès unifié aux deux repositories.
    """
    
    def __init__(self, file_path: Path):
        """
        Initialise le repository avec un fichier .gw.
        
        Args:
            file_path: Chemin du fichier .gw
        """
        self.file_path = file_path
        
        # Parser partagé pour éviter de parser deux fois
        self.parser = GwParser()
        self.database = self.parser.parse_file(file_path)
        
        # Créer les repositories qui partagent la même database
        self.persons = self._create_person_repository()
        self.families = self._create_family_repository()
    
    def _create_person_repository(self) -> GwFilePersonRepository:
        """Crée le PersonRepository avec la database déjà chargée."""
        repo = GwFilePersonRepository.__new__(GwFilePersonRepository)
        repo.file_path = self.file_path
        repo.parser = self.parser
        repo.database = self.database
        return repo
    
    def _create_family_repository(self) -> GwFileFamilyRepository:
        """Crée le FamilyRepository avec la database déjà chargée."""
        repo = GwFileFamilyRepository.__new__(GwFileFamilyRepository)
        repo.file_path = self.file_path
        repo.parser = self.parser
        repo.database = self.database
        return repo
