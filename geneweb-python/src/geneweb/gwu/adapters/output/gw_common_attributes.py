#!/usr/bin/env python3
"""
Calcul des attributs communs pour les enfants.
Basé sur common_children dans gwuLib.ml:512-530
"""

from typing import List, Optional
from geneweb.gwu.domain.entities.person import Person


class GwCommonAttributes:
    """Calcul des attributs communs pour les enfants."""
    
    @staticmethod
    def get_common_children_sources(children: List[Person]) -> str:
        """
        Calcule la source commune des enfants.
        Basé sur common_children_sources dans gwuLib.ml:532
        """
        return GwCommonAttributes._get_common_attribute(
            children, lambda p: p.sources[0] if p.sources else ""
        )
    
    @staticmethod
    def get_common_children_birth_place(children: List[Person]) -> str:
        """
        Calcule le lieu de naissance commun des enfants.
        Basé sur common_children_birth_place dans gwuLib.ml:533
        """
        return GwCommonAttributes._get_common_attribute(
            children, lambda p: getattr(p, 'birth_place', '') or ''
        )
    
    @staticmethod
    def _get_common_attribute(children: List[Person], getter) -> str:
        """
        Calcule l'attribut commun le plus fréquent.
        Basé sur common_children dans gwuLib.ml:512-530
        """
        if len(children) <= 1:
            return ""
        
        # Extraire les valeurs
        values = []
        for child in children:
            value = getter(child)
            if value:
                values.append(value)
        
        if not values or "" in values:
            return ""
        
        # Compter les occurrences
        value_counts = {}
        for value in values:
            value_counts[value] = value_counts.get(value, 0) + 1
        
        # Trouver la valeur la plus fréquente
        if not value_counts:
            return ""
        
        max_count = max(value_counts.values())
        if max_count <= 1:
            return ""
        
        # Retourner la première valeur avec le compte maximum
        for value, count in value_counts.items():
            if count == max_count:
                return value
        
        return ""
