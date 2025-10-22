#!/usr/bin/env python3
"""
Formateur de lignes d'enfants selon les règles OCaml.
Basé sur print_child dans gwuLib.ml:492-507
"""

from typing import List, Optional
from geneweb.gwu.domain.entities.person import Person
from geneweb.gwu.adapters.output.gw_child_attributes import GwChildAttributes


class GwChildFormatter:
    """Formateur de lignes d'enfants selon les règles OCaml."""
    
    @staticmethod
    def format_child_line(person: Person, family_surname: str, 
                         common_src: str, common_bp: str, options) -> str:
        """
        Formate la ligne complète d'un enfant.
        Basé sur print_child dans gwuLib.ml:492-507
        """
        parts = ["-"]
        
        # Sexe
        sex_marker = GwChildFormatter._get_sex_marker(person)
        parts.append(sex_marker)
        
        # Prénom
        first_name = GwChildFormatter._format_first_name(person)
        parts.append(first_name)
        
        # Occ (si nécessaire)
        occ_suffix = GwChildFormatter._get_occ_suffix(person)
        if occ_suffix:
            parts.append(occ_suffix)
        
        # Nom de famille (si différent du nom de famille de la famille)
        if person.surname != family_surname:
            parts.append(person.surname)
        
        # Attributs
        attributes = GwChildAttributes.format_child_attributes(
            person, True, common_src, common_bp, options
        )
        parts.extend(attributes)
        
        return " ".join(parts)
    
    @staticmethod
    def _get_sex_marker(person: Person) -> str:
        """Retourne le marqueur de sexe."""
        if hasattr(person, 'sex') and person.sex:
            if person.sex.value == "male":
                return "h"
            elif person.sex.value == "female":
                return "f"
        return ""
    
    @staticmethod
    def _format_first_name(person: Person) -> str:
        """Formate le prénom."""
        first_name = person.first_name or ""
        # Remplacer les espaces par des underscores
        return first_name.replace(' ', '_')
    
    @staticmethod
    def _get_occ_suffix(person: Person) -> str:
        """Retourne le suffixe d'occ si nécessaire."""
        if hasattr(person, 'occ') and person.occ and person.occ != 0:
            return f".{person.occ}"
        return ""
