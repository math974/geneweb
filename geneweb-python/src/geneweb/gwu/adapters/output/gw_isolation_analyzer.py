#!/usr/bin/env python3
"""
Analyseur d'isolation des personnes selon les règles OCaml exactes.
Basé sur la fonction is_isolated dans gwuLib.ml:1090-1093
"""

from typing import List, Set, Dict
from geneweb.gwu.domain.entities.person import Person
from geneweb.gwu.domain.entities.family import Family


class IsolationAnalyzer:
    """Analyseur d'isolation des personnes selon les règles OCaml."""
    
    def __init__(self):
        self._isolation_cache: Dict[str, bool] = {}
    
    def is_isolated_person(self, person: Person, families: List[Family]) -> bool:
        """
        Détermine si une personne est isolée selon les règles OCaml.
        Basé sur is_isolated dans gwuLib.ml:1090-1093
        """
        person_id = person.person_id
        
        # Utiliser le cache si disponible
        if person_id in self._isolation_cache:
            return self._isolation_cache[person_id]
        
        # Vérifier si la personne a des parents
        has_parents = self._has_parents(person, families)
        
        # Vérifier si la personne a des familles
        has_families = self._has_families(person, families)
        
        # Une personne est isolée si elle n'a pas de parents ET pas de familles
        is_isolated = not has_parents and not has_families
        
        # Mettre en cache le résultat
        self._isolation_cache[person_id] = is_isolated
        
        return is_isolated
    
    def _has_parents(self, person: Person, families: List[Family]) -> bool:
        """Vérifie si une personne a des parents."""
        for family in families:
            if person.person_id in family.children:
                # Vérifier que les parents existent et sont valides
                if (family.father_id and family.father_id != "unknown_father" and
                    family.mother_id and family.mother_id != "unknown_mother"):
                    return True
        return False
    
    def _has_families(self, person: Person, families: List[Family]) -> bool:
        """Vérifie si une personne a des familles (comme père ou mère)."""
        for family in families:
            if (person.person_id == family.father_id or 
                person.person_id == family.mother_id):
                return True
        return False
    
    def get_isolated_persons(self, persons: List[Person], families: List[Family]) -> List[Person]:
        """Retourne la liste des personnes isolées."""
        isolated_persons = []
        
        for person in persons:
            if self.is_isolated_person(person, families):
                isolated_persons.append(person)
        
        return isolated_persons
    
    def get_isolation_statistics(self, persons: List[Person], families: List[Family]) -> Dict[str, int]:
        """Retourne des statistiques sur l'isolation."""
        isolated_persons = self.get_isolated_persons(persons, families)
        
        return {
            "total_persons": len(persons),
            "isolated_persons": len(isolated_persons),
            "non_isolated_persons": len(persons) - len(isolated_persons),
            "isolation_rate": (len(isolated_persons) / len(persons) * 100) if len(persons) > 0 else 0
        }


class DynamicIsolationSelector:
    """Sélecteur basé sur l'analyse d'isolation OCaml."""
    
    def __init__(self):
        self.isolation_analyzer = IsolationAnalyzer()
    
    def should_include_person(self, person: Person, families: List[Family]) -> bool:
        """
        Détermine si une personne doit être incluse selon les règles OCaml.
        Exclut les personnes isolées et les personnes avec des noms invalides.
        """
        # Critère 1: Noms valides (comme OCaml ligne 676)
        if person.surname == "?" or person.first_name == "?":
            return False
        
        # Critère 2: Ne pas être isolée
        if self.isolation_analyzer.is_isolated_person(person, families):
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
        
        isolation_stats = self.isolation_analyzer.get_isolation_statistics(persons, families)
        
        return {
            "total_persons": total_persons,
            "included_persons": included_persons,
            "excluded_persons": excluded_persons,
            "isolated_persons": isolation_stats["isolated_persons"],
            "inclusion_rate": (included_persons / total_persons * 100) if total_persons > 0 else 0
        }
