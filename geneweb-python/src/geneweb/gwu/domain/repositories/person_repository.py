"""Interface PersonRepository - Port du Domain."""

from abc import ABC, abstractmethod
from typing import Optional, List, Iterator

from geneweb.common.types import PersonId
from geneweb.gwu.domain.entities import Person


class PersonRepository(ABC):
    """
    Interface pour accéder aux personnes de la base.
    
    Cette interface définit le contrat pour la lecture et l'écriture
    de personnes. Elle sera implémentée par les adapters (gwdb, .gw, etc.).
    """
    
    @abstractmethod
    def get_by_id(self, person_id: PersonId) -> Optional[Person]:
        """
        Récupère une personne par son ID.
        
        Args:
            person_id: ID de la personne
        
        Returns:
            La personne ou None si non trouvée
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def get_all(self) -> Iterator[Person]:
        """
        Récupère toutes les personnes de la base.
        
        Returns:
            Itérateur sur les personnes
        """
        pass
    
    @abstractmethod
    def get_count(self) -> int:
        """
        Retourne le nombre total de personnes.
        
        Returns:
            Nombre de personnes
        """
        pass
    
    @abstractmethod
    def search_by_name(self, search_term: str) -> List[Person]:
        """
        Recherche des personnes par nom (prénom ou nom de famille).
        
        Args:
            search_term: Terme de recherche
        
        Returns:
            Liste des personnes correspondantes
        """
        pass
    
    @abstractmethod
    def get_isolated_persons(self) -> Iterator[Person]:
        """
        Récupère les personnes isolées (sans parents ni conjoints).
        
        Returns:
            Itérateur sur les personnes isolées
        """
        pass
    
    @abstractmethod
    def save(self, person: Person) -> None:
        """
        Sauvegarde une personne.
        
        Args:
            person: Personne à sauvegarder
        """
        pass
    
    @abstractmethod
    def save_all(self, persons: Iterator[Person]) -> None:
        """
        Sauvegarde plusieurs personnes.
        
        Args:
            persons: Itérateur de personnes à sauvegarder
        """
        pass
