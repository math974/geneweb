#!/usr/bin/env python3
"""
Gestionnaire des familles manquantes selon les règles OCaml.
Basé sur la logique de collecte des familles dans gwuLib.ml
"""

from typing import List, Set, Dict
from geneweb.gwu.domain.entities.person import Person
from geneweb.gwu.domain.entities.family import Family


class FamilyCollector:
    """Collecteur de familles selon les règles OCaml."""
    
    def __init__(self):
        self._processed_families: Set[str] = set()
        self._all_families: List[Family] = []
    
    def collect_all_families(self, families: List[Family], persons: List[Person]) -> List[Family]:
        """
        Collecte toutes les familles selon l'ordre OCaml.
        Basé sur la logique de collecte des familles dans gwuLib.ml
        """
        self._reset()
        
        # Ajouter toutes les familles existantes
        for family in families:
            self._add_family(family)
        
        # Ajouter les familles manquantes (personnes isolées)
        self._add_isolated_persons_families(persons)
        
        return self._all_families.copy()
    
    def _reset(self) -> None:
        """Remet à zéro l'état du collecteur."""
        self._processed_families.clear()
        self._all_families.clear()
    
    def _add_family(self, family: Family) -> None:
        """Ajoute une famille si elle n'est pas déjà traitée."""
        if family.family_id not in self._processed_families:
            self._all_families.append(family)
            self._processed_families.add(family.family_id)
    
    def _add_isolated_persons_families(self, persons: List[Person]) -> None:
        """Ajoute les familles pour les personnes isolées."""
        for person in persons:
            if self._is_isolated_person(person):
                # Créer une famille fictive pour la personne isolée
                isolated_family = self._create_isolated_family(person)
                self._add_family(isolated_family)
    
    def _is_isolated_person(self, person: Person) -> bool:
        """Vérifie si une personne est isolée (pas de parents, pas de famille)."""
        has_parents = (hasattr(person, 'father_id') and person.father_id) or \
                     (hasattr(person, 'mother_id') and person.mother_id)
        has_family = hasattr(person, 'family_id') and person.family_id
        
        return not has_parents and not has_family
    
    def _create_isolated_family(self, person: Person) -> Family:
        """Crée une famille fictive pour une personne isolée."""
        # Code d'exclusion hardcodé supprimé - utilise maintenant le système modulaire
        
        # Créer une famille avec la personne comme seul enfant
        family = Family(
            family_id=f"isolated_{person.person_id}",
            father_id="unknown_father",  # ID fictif pour père inconnu
            mother_id="unknown_mother",  # ID fictif pour mère inconnue
            children=[person.person_id],
            marriage=None,
            divorce=None,
            notes=None,
            events=None
        )
        return family


class FamilyFormatter:
    """Formateur de familles selon les règles OCaml."""
    
    @staticmethod
    def format_family_header(family: Family, father: Person = None, mother: Person = None) -> str:
        """
        Formate l'en-tête d'une famille.
        Basé sur print_family dans gwuLib.ml:798-820
        """
        parts = ["fam"]
        
        # Père
        if father:
            parts.append(f"{father.surname} {father.first_name}")
        else:
            parts.append("? ?")
        
        # Séparateur
        parts.append("+")
        
        # Date de mariage
        if family.marriage and family.marriage.date:
            parts.append(str(family.marriage.date))
        
        # Mère
        if mother:
            parts.append(f"{mother.surname} {mother.first_name}")
        else:
            parts.append("? ?")
        
        return " ".join(parts)
    
    @staticmethod
    def format_family_children(family: Family, persons: List[Person]) -> List[str]:
        """
        Formate les enfants d'une famille.
        """
        lines = []
        
        if family.children:
            lines.append("beg")
            for child_id in family.children:
                child = next((p for p in persons if p.person_id == child_id), None)
                if child:
                    lines.append(f"  {child.surname} {child.first_name}")
            lines.append("end")
        
        return lines


class GwFamilyManager:
    """Gestionnaire principal des familles selon les règles OCaml."""
    
    def __init__(self, options):
        """
        Initialise le gestionnaire de familles.
        
        Args:
            options: Options de configuration (GwWriterOptions)
        """
        self.options = options
        self.collector = FamilyCollector()
        self.formatter = FamilyFormatter()
    
    def get_all_families(self, families: List[Family], persons: List[Person]) -> List[Family]:
        """
        Retourne toutes les familles dans l'ordre OCaml.
        """
        return self.collector.collect_all_families(families, persons)
    
    def format_family_section(self, family: Family, persons: List[Person]) -> List[str]:
        """
        Formate une section famille complète.
        """
        lines = []
        
        # Trouver père et mère
        father = None
        mother = None
        if family.father_id:
            father = next((p for p in persons if p.person_id == family.father_id), None)
        if family.mother_id:
            mother = next((p for p in persons if p.person_id == family.mother_id), None)
        
        # En-tête de famille
        header = self.formatter.format_family_header(family, father, mother)
        lines.append(header)
        
        # Enfants
        children_lines = self.formatter.format_family_children(family, persons)
        lines.extend(children_lines)
        
        return lines
    
    def get_family_statistics(self, families: List[Family], persons: List[Person]) -> Dict[str, int]:
        """
        Retourne des statistiques sur les familles.
        """
        all_families = self.get_all_families(families, persons)
        total_families = len(all_families)
        original_families = len(families)
        isolated_families = total_families - original_families
        
        return {
            "total_families": total_families,
            "original_families": original_families,
            "isolated_families": isolated_families
        }
