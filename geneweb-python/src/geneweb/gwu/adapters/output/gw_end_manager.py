"""
Gestionnaire des sections 'end' selon les règles OCaml.
Basé sur l'analyse de gwuLib.ml.
"""

from typing import List, Dict, Set
from geneweb.gwu.domain.entities.person import Person
from geneweb.gwu.domain.entities.family import Family


class GwEndManager:
    """Gestionnaire des sections 'end' selon OCaml."""
    
    def __init__(self):
        self.end_count = 0
        self.end_types: Dict[str, int] = {}
    
    def count_end_sections(self, families: List[Family], persons: List[Person]) -> int:
        """
        Compte les sections 'end' selon les règles OCaml.
        Basé sur l'analyse de gwuLib.ml lignes 796, 893, 1299.
        """
        count = 0
        
        # 1. 'end' pour chaque famille (enfants) - ligne 893
        for family in families:
            if family.children:
                count += 1
                self._increment_type("family_children")
        
        # 2. 'end' pour les relations - ligne 1299
        # (implémenté dans le gestionnaire de relations)
        count += self._count_relation_ends(persons)
        self._increment_type("relations", self._count_relation_ends(persons))
        
        # 3. 'end' pour les familles isolées
        count += self._count_isolated_family_ends(persons)
        self._increment_type("isolated_families", self._count_isolated_family_ends(persons))
        
        self.end_count = count
        return count
    
    def _count_relation_ends(self, persons: List[Person]) -> int:
        """Compte les 'end' pour les relations."""
        # OCaml génère un 'end' pour chaque personne avec relations
        count = 0
        for person in persons:
            if hasattr(person, 'relations') and person.relations:
                count += 1
        return count
    
    def _count_isolated_family_ends(self, persons: List[Person]) -> int:
        """Compte les 'end' pour les familles isolées."""
        # OCaml génère un 'end' pour chaque famille isolée
        count = 0
        for person in persons:
            if self._is_isolated_person(person):
                count += 1
        return count
    
    def _is_isolated_person(self, person: Person) -> bool:
        """Vérifie si une personne est isolée."""
        # Logique simplifiée - à adapter selon les besoins
        return (person.surname == "?" and person.first_name == "?")
    
    def _increment_type(self, end_type: str, count: int = 1) -> None:
        """Incrémente le compteur pour un type d'end."""
        if end_type not in self.end_types:
            self.end_types[end_type] = 0
        self.end_types[end_type] += count
    
    def get_end_statistics(self) -> Dict[str, int]:
        """Retourne les statistiques des sections 'end'."""
        return {
            "total": self.end_count,
            "by_type": self.end_types.copy()
        }
