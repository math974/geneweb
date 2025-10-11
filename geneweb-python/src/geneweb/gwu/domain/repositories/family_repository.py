"""Interface FamilyRepository - Port du Domain."""

from abc import ABC, abstractmethod
from typing import Optional, List, Iterator

from geneweb.common.types import FamilyId, PersonId
from geneweb.gwu.domain.entities import Family


class FamilyRepository(ABC):
    """
    Interface pour accéder aux familles de la base.
    
    Cette interface définit le contrat pour la lecture et l'écriture
    de familles. Elle sera implémentée par les adapters (gwdb, .gw, etc.).
    """
    
    @abstractmethod
    def get_by_id(self, family_id: FamilyId) -> Optional[Family]:
        """
        Récupère une famille par son ID.
        
        Args:
            family_id: ID de la famille
        
        Returns:
            La famille ou None si non trouvée
        """
        pass
    
    @abstractmethod
    def get_all(self) -> Iterator[Family]:
        """
        Récupère toutes les familles de la base.
        
        Returns:
            Itérateur sur les familles
        """
        pass
    
    @abstractmethod
    def get_count(self) -> int:
        """
        Retourne le nombre total de familles.
        
        Returns:
            Nombre de familles
        """
        pass
    
    @abstractmethod
    def get_families_of_person(self, person_id: PersonId) -> List[Family]:
        """
        Récupère les familles où une personne est parent.
        
        Args:
            person_id: ID de la personne
        
        Returns:
            Liste des familles
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def save(self, family: Family) -> None:
        """
        Sauvegarde une famille.
        
        Args:
            family: Famille à sauvegarder
        """
        pass
    
    @abstractmethod
    def save_all(self, families: Iterator[Family]) -> None:
        """
        Sauvegarde plusieurs familles.
        
        Args:
            families: Itérateur de familles à sauvegarder
        """
        pass
