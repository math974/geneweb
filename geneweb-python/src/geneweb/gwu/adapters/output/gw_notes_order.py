#!/usr/bin/env python3
"""
Système dynamique de gestion de l'ordre des notes selon les règles OCaml.
Basé sur get_persons_with_notes et print_notes dans gwuLib.ml
"""

from typing import List, Set, Dict, Optional, Iterator
from geneweb.gwu.domain.entities.person import Person
from geneweb.gwu.domain.entities.family import Family


class PersonNotesCollector:
    """Collecteur de personnes avec notes selon l'ordre OCaml."""
    
    def __init__(self):
        self._processed_persons: Set[str] = set()
        self._persons_with_notes: List[Person] = []
    
    def collect_from_families(self, families: List[Family], persons: List[Person]) -> List[Person]:
        """
        Collecte les personnes avec notes à partir des familles.
        Basé sur get_persons_with_notes dans gwuLib.ml:934-943
        """
        self._reset()
        person_lookup = self._build_person_lookup(persons)
        
        for family in families:
            self._process_family_persons(family, person_lookup)
        
        return self._persons_with_notes.copy()
    
    def _reset(self) -> None:
        """Remet à zéro l'état du collecteur."""
        self._processed_persons.clear()
        self._persons_with_notes.clear()
    
    def _build_person_lookup(self, persons: List[Person]) -> Dict[str, Person]:
        """Construit un index des personnes par ID."""
        return {person.person_id: person for person in persons}
    
    def _process_family_persons(self, family: Family, person_lookup: Dict[str, Person]) -> None:
        """Traite les personnes d'une famille selon l'ordre OCaml."""
        # Père (si pas déjà traité)
        if family.father_id:
            self._add_person_if_valid(family.father_id, person_lookup)
        
        # Mère (si pas déjà traité)
        if family.mother_id:
            self._add_person_if_valid(family.mother_id, person_lookup)
        
        # Enfants (dans l'ordre du tableau)
        for child_id in family.children:
            self._add_person_if_valid(child_id, person_lookup)
    
    def _add_person_if_valid(self, person_id: str, person_lookup: Dict[str, Person]) -> None:
        """Ajoute une personne si elle a des notes et n'est pas déjà traitée."""
        if person_id in self._processed_persons:
            return
        
        person = person_lookup.get(person_id)
        if person and person.has_notes():
            self._persons_with_notes.append(person)
            self._processed_persons.add(person_id)


class NotesOrderStrategy:
    """Stratégie d'ordre des notes selon les règles OCaml."""
    
    @staticmethod
    def get_family_based_order(families: List[Family], persons: List[Person]) -> List[Person]:
        """
        Ordre basé sur le traitement des familles (logique OCaml).
        Basé sur print_notes dans gwuLib.ml:1077-1088
        """
        collector = PersonNotesCollector()
        return collector.collect_from_families(families, persons)
    
    @staticmethod
    def get_chronological_order(persons: List[Person]) -> List[Person]:
        """
        Ordre chronologique basé sur les dates de naissance.
        Fallback si pas de familles disponibles.
        """
        persons_with_notes = [p for p in persons if p.has_notes()]
        return sorted(persons_with_notes, key=lambda p: str(p.birth) if p.birth else "")
    
    @staticmethod
    def get_alphabetical_order(persons: List[Person]) -> List[Person]:
        """
        Ordre alphabétique par nom de famille puis prénom.
        Fallback si pas de familles disponibles.
        """
        persons_with_notes = [p for p in persons if p.has_notes()]
        return sorted(persons_with_notes, key=lambda p: (p.surname, p.first_name))


class GwNotesOrder:
    """Gestionnaire principal de l'ordre des notes selon les règles OCaml."""
    
    def __init__(self, strategy: str = "family_based"):
        """
        Initialise le gestionnaire avec une stratégie d'ordre.
        
        Args:
            strategy: "family_based" (OCaml), "chronological", "alphabetical"
        """
        self.strategy = strategy
        self._strategy_map = {
            "family_based": NotesOrderStrategy.get_family_based_order,
            "chronological": NotesOrderStrategy.get_chronological_order,
            "alphabetical": NotesOrderStrategy.get_alphabetical_order,
        }
    
    def get_ordered_persons_with_notes(self, families: List[Family], 
                                     persons: List[Person]) -> List[Person]:
        """
        Retourne les personnes avec notes dans l'ordre configuré.
        
        Args:
            families: Liste des familles (requis pour family_based)
            persons: Liste de toutes les personnes
            
        Returns:
            Liste des personnes avec notes dans l'ordre approprié
        """
        strategy_func = self._strategy_map.get(self.strategy)
        if not strategy_func:
            raise ValueError(f"Stratégie inconnue: {self.strategy}")
        
        if self.strategy == "family_based" and not families:
            # Fallback si pas de familles disponibles
            return NotesOrderStrategy.get_alphabetical_order(persons)
        
        if self.strategy == "family_based":
            return strategy_func(families, persons)
        else:
            return strategy_func(persons)
    
    def get_notes_statistics(self, families: List[Family], 
                           persons: List[Person]) -> Dict[str, int]:
        """
        Retourne des statistiques sur les notes.
        
        Returns:
            Dictionnaire avec les statistiques
        """
        ordered_persons = self.get_ordered_persons_with_notes(families, persons)
        total_persons = len(persons)
        persons_with_notes = len(ordered_persons)
        
        return {
            "total_persons": total_persons,
            "persons_with_notes": persons_with_notes,
            "notes_percentage": (persons_with_notes / total_persons * 100) if total_persons > 0 else 0,
            "strategy_used": self.strategy
        }
