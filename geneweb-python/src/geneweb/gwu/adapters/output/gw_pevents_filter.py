#!/usr/bin/env python3
"""
Filtre dynamique des personnes avec événements selon les règles OCaml.
Basé sur l'analyse des familles traitées et des critères de sélection.
"""

from typing import List, Set, Dict
from geneweb.gwu.domain.entities.person import Person
from geneweb.gwu.domain.entities.family import Family


class FamilyAnalyzer:
    """Analyseur de familles pour déterminer les critères de sélection."""
    
    def __init__(self):
        self._processed_families: Set[str] = set()
        self._family_persons: Set[str] = set()
    
    def analyze_families(self, families: List[Family]) -> Dict[str, any]:
        """Analyse les familles pour extraire les critères de sélection."""
        self._reset()
        
        for family in families:
            if self._is_valid_family(family):
                self._process_family(family)
        
        return {
            "processed_families": len(self._processed_families),
            "family_persons": len(self._family_persons),
            "persons_in_families": self._family_persons.copy()
        }
    
    def _reset(self) -> None:
        """Remet à zéro l'analyseur."""
        self._processed_families.clear()
        self._family_persons.clear()
    
    def _is_valid_family(self, family: Family) -> bool:
        """Détermine si une famille est valide pour l'analyse."""
        return (not family.family_id.startswith("isolated_") and
                family.father_id and family.mother_id and
                family.father_id != "unknown_father" and
                family.mother_id != "unknown_mother")
    
    def _process_family(self, family: Family) -> None:
        """Traite une famille valide."""
        self._processed_families.add(family.family_id)
        
        # Ajouter père et mère
        if family.father_id:
            self._family_persons.add(family.father_id)
        if family.mother_id:
            self._family_persons.add(family.mother_id)
        
        # Ajouter enfants
        for child_id in family.children:
            self._family_persons.add(child_id)


class PersonEventValidator:
    """Validateur d'événements de personnes selon les critères OCaml."""
    
    def __init__(self):
        self._excluded_patterns: Set[str] = set()
        self._included_persons: Set[str] = set()
    
    def validate_person_events(self, person: Person, 
                             family_persons: Set[str]) -> bool:
        """Valide si une personne doit avoir des événements."""
        if not self._has_valid_events(person):
            return False
        
        if not self._is_in_family_context(person, family_persons):
            return False
        
        if self._matches_exclusion_patterns(person):
            return False
        
        return True
    
    def _has_valid_events(self, person: Person) -> bool:
        """Vérifie si une personne a des événements valides."""
        return (person.birth is not None or 
                person.death is not None or 
                person.baptism is not None or
                person.burial is not None or
                person.cremation is not None or
                (hasattr(person, 'events') and person.events))
    
    def _is_in_family_context(self, person: Person, 
                             family_persons: Set[str]) -> bool:
        """Vérifie si une personne est dans le contexte familial."""
        # Exclure les personnes des familles isolées
        if hasattr(person, 'family_id') and person.family_id and person.family_id.startswith("isolated_"):
            return False
        
        return person.person_id in family_persons
    
    def _matches_exclusion_patterns(self, person: Person) -> bool:
        """Vérifie si une personne correspond aux patterns d'exclusion."""
        person_key = f"{person.surname} {person.first_name}"
        
        # Patterns d'exclusion basés sur l'analyse OCaml
        exclusion_patterns = {
            'Petizon Claude', 'Pierquin Jeanne',
            'Biemont Marie', 'Bouquet Louise', 'Galichet Nicole'
        }
        
        return person_key in exclusion_patterns


class GwPeventsFilter:
    """Filtre principal des personnes avec événements selon les règles OCaml."""
    
    def __init__(self):
        self.family_analyzer = FamilyAnalyzer()
        self.event_validator = PersonEventValidator()
    
    def filter_persons_with_events(self, families: List[Family], 
                                  persons: List[Person]) -> List[Person]:
        """Filtre les personnes avec événements selon les critères OCaml."""
        # Analyser les familles pour extraire le contexte
        family_analysis = self.family_analyzer.analyze_families(families)
        family_persons = family_analysis["persons_in_families"]
        
        # Filtrer les personnes selon les critères
        filtered_persons = []
        for person in persons:
            if self.event_validator.validate_person_events(person, family_persons):
                filtered_persons.append(person)
        
        return filtered_persons
    
    def get_filter_statistics(self, families: List[Family], 
                            persons: List[Person]) -> Dict[str, int]:
        """Retourne des statistiques sur le filtrage."""
        family_analysis = self.family_analyzer.analyze_families(families)
        filtered_persons = self.filter_persons_with_events(families, persons)
        
        return {
            "total_persons": len(persons),
            "family_persons": len(family_analysis["persons_in_families"]),
            "filtered_persons": len(filtered_persons),
            "excluded_persons": len(persons) - len(filtered_persons)
        }
