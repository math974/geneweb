#!/usr/bin/env python3
"""
Accumulateur de personnes avec événements selon la logique OCaml exacte.
Basé sur gen.pevents_pl_p dans gwuLib.ml
"""

from typing import List, Set, Dict
from geneweb.gwu.domain.entities.person import Person
from geneweb.gwu.domain.entities.family import Family


class PeventsAccumulator:
    """Accumulateur de personnes avec événements selon la logique OCaml."""
    
    def __init__(self):
        self._pevents_pl_p: List[Person] = []
        self._processed_persons: Set[str] = set()
    
    def reset(self) -> None:
        """Remet à zéro l'accumulateur."""
        self._pevents_pl_p.clear()
        self._processed_persons.clear()
    
    def add_person_with_pevents(self, person: Person) -> None:
        """
        Ajoute une personne avec événements à l'accumulateur.
        Basé sur la ligne 567 dans gwuLib.ml
        """
        # Code d'exclusion hardcodé supprimé - utilise maintenant le système modulaire
        
        if person.person_id not in self._processed_persons and self._has_pevents(person):
            self._pevents_pl_p.append(person)
            self._processed_persons.add(person.person_id)
    
    def _has_pevents(self, person: Person) -> bool:
        """Vérifie si une personne a des événements."""
        return (person.birth is not None or 
                person.death is not None or 
                person.baptism is not None or
                person.burial is not None or
                person.cremation is not None or
                (hasattr(person, 'events') and person.events))
    
    def get_accumulated_persons(self) -> List[Person]:
        """Retourne la liste accumulée des personnes avec événements."""
        return self._pevents_pl_p.copy()
    
    def get_statistics(self) -> Dict[str, int]:
        """Retourne des statistiques sur l'accumulateur."""
        return {
            "accumulated_persons": len(self._pevents_pl_p),
            "processed_persons": len(self._processed_persons)
        }


class PeventsCollector:
    """Collecteur de personnes avec événements selon la logique OCaml exacte."""
    
    def __init__(self):
        self.accumulator = PeventsAccumulator()
    
    def collect_from_families_and_accumulated(self, families: List[Family], 
                                            persons: List[Person]) -> List[Person]:
        """
        Collecte les personnes avec événements selon la logique OCaml exacte.
        Basé sur print_pevents dans gwuLib.ml:690-701
        """
        # 1. Collecter depuis les familles (comme get_persons_with_pevents)
        family_persons = self._collect_from_families(families, persons)
        
        # 2. Ajouter les personnes accumulées (gen.pevents_pl_p)
        accumulated_persons = self.accumulator.get_accumulated_persons()
        
        # 3. Filtrer les personnes accumulées pour exclure celles créées dynamiquement
        filtered_accumulated = self._filter_original_persons(accumulated_persons, persons)
        
        # 4. Combiner et dédupliquer (comme list_memf eq_key)
        all_persons = self._combine_and_deduplicate(family_persons, filtered_accumulated)
        
        return all_persons
    
    def _collect_from_families(self, families: List[Family], persons: List[Person]) -> List[Person]:
        """Collecte depuis les familles selon get_persons_with_pevents."""
        collected_persons = []
        person_lookup = {p.person_id: p for p in persons}
        
        for family in families:
            # Père (si a des événements et pas de parents)
            if family.father_id:
                father = person_lookup.get(family.father_id)
                if father and self._has_pevents_and_no_parents(father):
                    collected_persons.append(father)
            
            # Mère (si a des événements et pas de parents)
            if family.mother_id:
                mother = person_lookup.get(family.mother_id)
                if mother and self._has_pevents_and_no_parents(mother):
                    collected_persons.append(mother)
            
            # Enfants (si ont des événements)
            for child_id in family.children:
                child = person_lookup.get(child_id)
                if child and self._has_pevents(child):
                    collected_persons.append(child)
        
        return collected_persons
    
    def _has_pevents(self, person: Person) -> bool:
        """Vérifie si une personne a des événements."""
        return (person.birth is not None or 
                person.death is not None or 
                person.baptism is not None or
                person.burial is not None or
                person.cremation is not None or
                (hasattr(person, 'events') and person.events))
    
    def _filter_original_persons(self, accumulated_persons: List[Person], 
                                original_persons: List[Person]) -> List[Person]:
        """Filtre les personnes accumulées pour ne garder que celles des données originales."""
        original_lookup = {p.person_id: p for p in original_persons}
        filtered_persons = []
        
        for person in accumulated_persons:
            # Vérifier si la personne est dans les données originales
            if person.person_id in original_lookup:
                # Vérifier que c'est bien la même personne (nom et prénom)
                original_person = original_lookup[person.person_id]
                if (original_person.surname == person.surname and 
                    original_person.first_name == person.first_name):
                    filtered_persons.append(person)
        
        return filtered_persons
    
    def _has_pevents_and_no_parents(self, person: Person) -> bool:
        """Vérifie si une personne a des événements et pas de parents."""
        has_pevents = self._has_pevents(person)
        has_no_parents = (not hasattr(person, 'father_id') or not person.father_id) and \
                        (not hasattr(person, 'mother_id') or not person.mother_id)
        return has_pevents and has_no_parents
    
    def _combine_and_deduplicate(self, family_persons: List[Person], 
                                accumulated_persons: List[Person]) -> List[Person]:
        """Combine et déduplique les listes comme list_memf eq_key."""
        all_persons = []
        seen_ids = set()
        
        # Ajouter les personnes des familles
        for person in family_persons:
            if person.person_id not in seen_ids:
                all_persons.append(person)
                seen_ids.add(person.person_id)
        
        # Ajouter les personnes accumulées
        for person in accumulated_persons:
            if person.person_id not in seen_ids:
                all_persons.append(person)
                seen_ids.add(person.person_id)
        
        return all_persons
    
    def add_person_to_accumulator(self, person: Person) -> None:
        """Ajoute une personne à l'accumulateur."""
        self.accumulator.add_person_with_pevents(person)
    
    def reset_accumulator(self) -> None:
        """Remet à zéro l'accumulateur."""
        self.accumulator.reset()
