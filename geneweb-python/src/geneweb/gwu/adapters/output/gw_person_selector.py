#!/usr/bin/env python3
"""
Sélecteur de personnes selon les règles OCaml.
Basé sur per_sel dans gwuLib.ml
"""

from typing import List, Set
from geneweb.gwu.domain.entities.person import Person


class PersonSelector:
    """Sélecteur de personnes selon les règles OCaml."""
    
    def __init__(self):
        self._selected_persons: Set[str] = set()
        self._excluded_persons: Set[str] = set()
    
    def select_person(self, person: Person) -> bool:
        """
        Détermine si une personne doit être sélectionnée.
        Basé sur per_sel dans gwuLib.ml
        """
        # Exclure les personnes avec des noms invalides
        if person.surname == "?" or person.first_name == "?":
            return False
        
        # Exclure les personnes déjà exclues
        if person.person_id in self._excluded_persons:
            return False
        
        # Inclure les personnes sélectionnées
        if person.person_id in self._selected_persons:
            return True
        
        # Logique de sélection par défaut (toutes les personnes valides)
        return True
    
    def add_selected_person(self, person_id: str) -> None:
        """Ajoute une personne à la liste des sélectionnées."""
        self._selected_persons.add(person_id)
    
    def add_excluded_person(self, person_id: str) -> None:
        """Ajoute une personne à la liste des exclues."""
        self._excluded_persons.add(person_id)
    
    def filter_persons(self, persons: List[Person]) -> List[Person]:
        """Filtre une liste de personnes selon les critères de sélection."""
        return [p for p in persons if self.select_person(p)]
    
    def get_statistics(self) -> dict:
        """Retourne des statistiques sur la sélection."""
        return {
            "selected_persons": len(self._selected_persons),
            "excluded_persons": len(self._excluded_persons)
        }
