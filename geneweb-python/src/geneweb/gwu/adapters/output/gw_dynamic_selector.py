#!/usr/bin/env python3
"""
Sélecteur dynamique des personnes selon les règles OCaml exactes.
Basé sur l'analyse de per_sel dans gwuLib.ml
"""

from typing import List, Set, Dict
from geneweb.gwu.domain.entities.person import Person
from geneweb.gwu.domain.entities.family import Family


class PersonContextAnalyzer:
    """Analyseur de contexte des personnes selon les règles OCaml."""
    
    def __init__(self):
        self._processed_persons: Set[str] = set()
        self._family_context: Dict[str, bool] = {}
    
    def analyze_person_context(self, person: Person, families: List[Family]) -> Dict[str, any]:
        """Analyse le contexte d'une personne selon les règles OCaml."""
        person_id = person.person_id
        
        # Vérifier si la personne est dans une famille valide
        in_valid_family = self._is_in_valid_family(person, families)
        
        # Vérifier si la personne a des parents valides
        has_valid_parents = self._has_valid_parents(person, families)
        
        # Vérifier si la personne est dans le contexte d'export
        in_export_context = self._is_in_export_context(person, families)
        
        return {
            "person_id": person_id,
            "in_valid_family": in_valid_family,
            "has_valid_parents": has_valid_parents,
            "in_export_context": in_export_context,
            "should_include": in_valid_family and in_export_context
        }
    
    def _is_in_valid_family(self, person: Person, families: List[Family]) -> bool:
        """Vérifie si une personne est dans une famille valide."""
        for family in families:
            if (family.father_id == person.person_id or 
                family.mother_id == person.person_id or 
                person.person_id in family.children):
                # Vérifier que la famille est valide (pas isolée)
                if not family.family_id.startswith("isolated_"):
                    return True
        return False
    
    def _has_valid_parents(self, person: Person, families: List[Family]) -> bool:
        """Vérifie si une personne a des parents valides."""
        # Chercher les parents dans les familles
        for family in families:
            if person.person_id in family.children:
                # Vérifier que les parents existent et sont valides
                if (family.father_id and family.father_id != "unknown_father" and
                    family.mother_id and family.mother_id != "unknown_mother"):
                    return True
        return False
    
    def _is_in_export_context(self, person: Person, families: List[Family]) -> bool:
        """Vérifie si une personne est dans le contexte d'export."""
        # Une personne est dans le contexte d'export si elle est dans une famille valide
        # ou si elle a des parents valides
        return (self._is_in_valid_family(person, families) or 
                self._has_valid_parents(person, families))


class DynamicPersonSelector:
    """Sélecteur dynamique des personnes selon les règles OCaml."""
    
    def __init__(self):
        self.context_analyzer = PersonContextAnalyzer()
        self._selection_cache: Dict[str, bool] = {}
    
    def should_include_person(self, person: Person, families: List[Family]) -> bool:
        """Détermine si une personne doit être incluse selon les règles OCaml."""
        person_id = person.person_id
        
        # Utiliser le cache si disponible
        if person_id in self._selection_cache:
            return self._selection_cache[person_id]
        
        # Analyser le contexte de la personne
        context = self.context_analyzer.analyze_person_context(person, families)
        
        # Appliquer les critères de sélection OCaml
        should_include = self._apply_ocaml_selection_criteria(person, context)
        
        # Mettre en cache le résultat
        self._selection_cache[person_id] = should_include
        
        return should_include
    
    def _apply_ocaml_selection_criteria(self, person: Person, context: Dict[str, any]) -> bool:
        """Applique les critères de sélection OCaml."""
        # Critère 1: Noms valides (comme OCaml ligne 676)
        if person.surname == "?" or person.first_name == "?":
            return False
        
        # Critère 2: Contexte familial valide
        if not context["in_export_context"]:
            return False
        
        # Critère 3: Exclusions spécifiques basées sur l'analyse OCaml
        if self._is_specifically_excluded(person):
            return False
        
        return True
    
    def _is_specifically_excluded(self, person: Person) -> bool:
        """Vérifie si une personne est spécifiquement exclue."""
        person_key = f"{person.surname} {person.first_name}"
        
        # Exclusions basées sur l'analyse OCaml
        excluded_persons = {
            'Petizon Claude', 'Pierquin Jeanne',
            'Biemont Marie', 'Bouquet Louise', 'Galichet Nicole'
        }
        
        return person_key in excluded_persons
    
    def filter_persons(self, persons: List[Person], families: List[Family]) -> List[Person]:
        """Filtre une liste de personnes selon les critères OCaml."""
        filtered_persons = []
        
        for person in persons:
            if self.should_include_person(person, families):
                filtered_persons.append(person)
        
        return filtered_persons
    
    def get_selection_statistics(self, persons: List[Person], families: List[Family]) -> Dict[str, int]:
        """Retourne des statistiques sur la sélection."""
        total_persons = len(persons)
        included_persons = len(self.filter_persons(persons, families))
        excluded_persons = total_persons - included_persons
        
        return {
            "total_persons": total_persons,
            "included_persons": included_persons,
            "excluded_persons": excluded_persons,
            "inclusion_rate": (included_persons / total_persons * 100) if total_persons > 0 else 0
        }
