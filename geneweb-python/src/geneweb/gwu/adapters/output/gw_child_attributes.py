#!/usr/bin/env python3
"""
Gestion des attributs des enfants selon les règles OCaml.
Basé sur print_infos dans gwuLib.ml:342-408
"""

from typing import List, Optional
from geneweb.gwu.domain.entities.person import Person
from geneweb.gwu.domain.entities.date import Date
from geneweb.gwu.adapters.output.gw_formatting_rules import GwFormattingRules


class GwChildAttributes:
    """Gestion des attributs des enfants selon les règles OCaml."""
    
    @staticmethod
    def format_child_attributes(person: Person, is_child: bool, 
                               common_src: str, common_bp: str, options) -> List[str]:
        """
        Formate les attributs d'un enfant selon les règles OCaml.
        Basé sur print_infos dans gwuLib.ml:342-408
        """
        attrs = []
        
        # Occupation
        if person.occupation:
            attrs.append(f"#occu {person.occupation}")
        
        # Sources (si différentes de la source commune)
        if person.sources and not options.no_sources:
            for source in person.sources:
                if source != common_src:
                    attrs.append(f"#src {source}")
        
        # Date de naissance
        birth_attrs = GwChildAttributes._format_birth_attributes(person, is_child, options)
        attrs.extend(birth_attrs)
        
        # Date de baptême
        baptism_attrs = GwChildAttributes._format_baptism_attributes(person, options)
        attrs.extend(baptism_attrs)
        
        # Date de décès
        death_attrs = GwChildAttributes._format_death_attributes(person, options)
        attrs.extend(death_attrs)
        
        # Lieu de décès
        if person.death and hasattr(person.death, 'place') and person.death.place:
            attrs.append(f"#dp {person.death.place}")
        
        # Source de décès
        if person.death and hasattr(person.death, 'source') and person.death.source and not options.no_sources:
            attrs.append(f"#ds {person.death.source}")
        
        # Access level
        access_attrs = GwChildAttributes._format_access_attributes(person)
        attrs.extend(access_attrs)
        
        return attrs
    
    @staticmethod
    def _format_birth_attributes(person: Person, is_child: bool, options) -> List[str]:
        """Formate les attributs de naissance."""
        attrs = []
        
        # Date de naissance
        if person.birth and hasattr(person.birth, 'date') and person.birth.date:
            birth_date = GwFormattingRules.format_date(person.birth.date)
            if birth_date:
                attrs.append(birth_date)
        elif GwChildAttributes._zero_birth_is_required(person, is_child, options):
            attrs.append("0")
        
        # Lieu de naissance
        if person.birth and hasattr(person.birth, 'place') and person.birth.place:
            attrs.append(f"#bp {person.birth.place}")
        
        # Source de naissance
        if person.birth and hasattr(person.birth, 'source') and person.birth.source and not options.no_sources:
            attrs.append(f"#bs {person.birth.source}")
        
        return attrs
    
    @staticmethod
    def _format_baptism_attributes(person: Person, options) -> List[str]:
        """Formate les attributs de baptême."""
        attrs = []
        
        # Date de baptême
        if hasattr(person, 'baptism') and person.baptism and hasattr(person.baptism, 'date') and person.baptism.date:
            baptism_date = GwFormattingRules.format_date(person.baptism.date)
            if baptism_date:
                attrs.append(f"!{baptism_date}")
        
        # Lieu de baptême
        if person.baptism and hasattr(person.baptism, 'place') and person.baptism.place:
            attrs.append(f"#pp {person.baptism.place}")
        
        # Source de baptême
        if person.baptism and hasattr(person.baptism, 'source') and person.baptism.source and not options.no_sources:
            attrs.append(f"#ps {person.baptism.source}")
        
        return attrs
    
    @staticmethod
    def _format_death_attributes(person: Person, options) -> List[str]:
        """Formate les attributs de décès."""
        attrs = []
        
        if person.death and hasattr(person.death, 'date') and person.death.date:
            death_date = GwFormattingRules.format_date(person.death.date)
            if death_date:
                # Ajouter le préfixe de type de décès si nécessaire
                death_prefix = GwChildAttributes._get_death_prefix(person.death)
                attrs.append(f"{death_prefix}{death_date}")
        elif hasattr(person, 'death_status'):
            death_status = person.death_status
            if death_status == "DeadYoung":
                attrs.append("mj")
            elif death_status == "DeadDontKnowWhen":
                attrs.append("0")
            elif death_status == "OfCourseDead":
                attrs.append("od")
        
        return attrs
    
    @staticmethod
    def _format_access_attributes(person: Person) -> List[str]:
        """Formate les attributs d'accès."""
        attrs = []
        
        if hasattr(person, 'access') and person.access:
            access_str = str(person.access)
            if "od" in access_str:
                attrs.append("od")
        
        return attrs
    
    @staticmethod
    def _zero_birth_is_required(person: Person, is_child: bool, options) -> bool:
        """
        Détermine si un "0" est requis pour la naissance.
        Basé sur zero_birth_is_required dans gwuLib.ml
        """
        # Logique simplifiée : si c'est un enfant et qu'il n'y a pas de date de naissance
        return is_child and (not person.birth or not hasattr(person.birth, 'date') or not person.birth.date)
    
    @staticmethod
    def _get_death_prefix(death_event) -> str:
        """Retourne le préfixe de type de décès."""
        if hasattr(death_event, 'reason'):
            reason = death_event.reason
            if reason == "Killed":
                return "k"
            elif reason == "Murdered":
                return "m"
            elif reason == "Executed":
                return "e"
            elif reason == "Disappeared":
                return "s"
        return ""
