"""
Règles de formatage GW extraites du code OCaml.
Ces fonctions respectent les règles de formatage d'OCaml pour n'importe quel fichier.
"""

from typing import Optional, List, Any
from geneweb.gwu.domain.entities.person import Person
from geneweb.gwu.domain.entities.family import Family
from geneweb.gwu.domain.entities.date import Date
from geneweb.gwu.domain.entities.event import Event, EventType
from geneweb.common.types import AccessLevel


class GwFormattingRules:
    """Règles de formatage GW basées sur la logique OCaml."""
    
    @staticmethod
    def has_infos_not_dates(person: Person, options) -> bool:
        """
        Vérifie si une personne a des informations non-dates.
        Basé sur has_infos_not_dates dans gwuLib.ml:228-249
        """
        return (
            bool(person.sources) or
            bool(person.occupation) or
            bool(person.titles) or
            person.access != AccessLevel.PUBLIC or
            bool(person.image)
        )
    
    @staticmethod
    def has_infos(person: Person, options) -> bool:
        """
        Vérifie si une personne a des informations à afficher.
        Basé sur has_infos dans gwuLib.ml:251-255
        """
        return (
            GwFormattingRules.has_infos_not_dates(person, options) or
            GwFormattingRules.has_birth(person) or
            GwFormattingRules.has_baptism(person) or
            GwFormattingRules.has_death(person)
        )
    
    @staticmethod
    def has_birth(person: Person) -> bool:
        """Vérifie si la personne a une naissance."""
        if not person.birth:
            return False
        if hasattr(person.birth, 'date'):
            return person.birth.date is not None
        return person.birth is not None
    
    @staticmethod
    def has_baptism(person: Person) -> bool:
        """Vérifie si la personne a un baptême."""
        return person.baptism is not None
    
    @staticmethod
    def has_death(person: Person) -> bool:
        """Vérifie si la personne a un décès."""
        if not person.death:
            return False
        if hasattr(person.death, 'date'):
            return person.death.date is not None
        return person.death is not None
    
    @staticmethod
    def should_print_parent_dates(person: Person, is_first_definition: bool, 
                                 has_printed_parents: bool, options) -> bool:
        """
        Détermine si on doit imprimer les dates d'un parent.
        Basé sur print_parent dans gwuLib.ml:466-490
        """
        pr = (not has_printed_parents) and is_first_definition
        if not pr:
            return False
        
        has_infos = GwFormattingRules.has_infos(person, options)
        if has_infos:
            return True
        
        # Si pas d'infos mais nom valide, générer " 0"
        return person.first_name != "?" and person.surname != "?"
    
    @staticmethod
    def format_parent_name(person: Person) -> str:
        """
        Formate le nom d'un parent.
        Basé sur print_parent dans gwuLib.ml:482-486
        """
        surname = person.surname or ""
        first_name = person.first_name or ""
        
        # Gestion de l'occ
        if person.occ == 0:
            occ_suffix = ""
        else:
            occ_suffix = f".{person.occ}"
        
        # Remplacer les espaces par des underscores dans le prénom
        first_name_clean = first_name.replace(' ', '_')
        return f"{surname} {first_name_clean}{occ_suffix}"
    
    @staticmethod
    def should_print_marriage_info(family: Family, options) -> bool:
        """
        Détermine si on doit imprimer les infos de mariage.
        Basé sur print_family dans gwuLib.ml:803
        """
        if not family.marriage:
            return False
        return not options.no_events
    
    @staticmethod
    def format_marriage_date(family: Family) -> str:
        """
        Formate la date de mariage.
        Basé sur print_date_option dans gwuLib.ml:803
        """
        if not family.marriage or not hasattr(family.marriage, 'date'):
            return ""
        return GwFormattingRules.format_date(family.marriage.date)
    
    @staticmethod
    def format_date(date: Date) -> str:
        """
        Formate une date selon les règles OCaml.
        Basé sur print_date_dmy dans gwuLib.ml:115-125
        """
        if not date:
            return ""
        
        if not hasattr(date, 'year') or date.year <= 0:
            return ""
        
        # Préfixe de précision
        prefix = ""
        if hasattr(date, 'precision'):
            if date.precision == "approx" or date.precision == "about":
                prefix = "~"
            elif date.precision == "unknown" or date.precision == "maybe":
                prefix = "?"
            elif date.precision == "before":
                prefix = "<"
            elif date.precision == "after":
                prefix = ">"
        
        # Format de la date
        if hasattr(date, 'month') and date.month > 0:
            if hasattr(date, 'day') and date.day > 0:
                return f"{prefix}{date.day}/{date.month}/{date.year}"
            else:
                return f"{prefix}{date.month}/{date.year}"
        else:
            # Si mois = 0, ajouter "0" avant l'année
            if prefix:
                return f"0 {prefix}{date.year}"
            else:
                return f"0{date.year}"
    
    @staticmethod
    def format_marriage_place(family: Family) -> str:
        """
        Formate le lieu de mariage.
        Basé sur print_if_no_empty dans gwuLib.ml:825
        """
        if not family.marriage or not hasattr(family.marriage, 'place'):
            return ""
        return GwFormattingRules.format_place(family.marriage.place)
    
    @staticmethod
    def format_place(place) -> str:
        """
        Formate un lieu selon les règles OCaml.
        """
        if not place:
            return ""
        
        if hasattr(place, 'name'):
            return place.name
        return str(place)
    
    @staticmethod
    def format_marriage_source(family: Family, options) -> str:
        """
        Formate la source de mariage.
        Basé sur print_family dans gwuLib.ml:826-827
        """
        if not family.marriage or not hasattr(family.marriage, 'source'):
            return ""
        if not options.no_sources:
            return family.marriage.source or ""
        return ""
    
    @staticmethod
    def should_print_family_sources(family: Family, options) -> bool:
        """
        Détermine si on doit imprimer les sources de famille.
        Basé sur print_family dans gwuLib.ml:857-863
        """
        return not options.no_sources and bool(family.sources)
    
    @staticmethod
    def should_print_family_events(family: Family, options) -> bool:
        """
        Détermine si on doit imprimer les événements de famille.
        Basé sur print_family dans gwuLib.ml:879-882
        """
        return not options.no_events and bool(family.events)
    
    @staticmethod
    def should_print_children(family: Family) -> bool:
        """
        Détermine si on doit imprimer les enfants.
        Basé sur print_family dans gwuLib.ml:883-893
        """
        return len(family.children) > 0
