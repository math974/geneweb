"""
Formateurs GW basés sur les règles OCaml.
Chaque fonction fait maximum 20 lignes et respecte les règles de formatage.
"""

from typing import List, Optional
from geneweb.gwu.domain.entities.person import Person
from geneweb.gwu.domain.entities.family import Family
from geneweb.gwu.domain.entities.date import Date
from geneweb.gwu.domain.entities.event import EventType
from geneweb.gwu.adapters.output.gw_formatting_rules import GwFormattingRules
from geneweb.gwu.adapters.output.gw_child_formatter import GwChildFormatter


class GwFormatters:
    """Formateurs GW basés sur les règles OCaml."""
    
    @staticmethod
    def format_fam_line(family: Family, father: Person, mother: Person, 
                       is_first_father_def: bool, is_first_mother_def: bool,
                       has_printed_father_parents: bool, has_printed_mother_parents: bool,
                       options) -> str:
        """
        Formate la ligne 'fam' selon les règles OCaml.
        Basé sur print_family dans gwuLib.ml:800-843
        """
        # Format: "fam père + ..."
        line = f"fam {GwFormatters._format_parent_name(father, is_first_father_def, has_printed_father_parents, options)} +"
        
        # Date de mariage
        if GwFormattingRules.should_print_marriage_info(family, options):
            marriage_date = GwFormattingRules.format_marriage_date(family)
            if marriage_date:
                line += f" {marriage_date}"
        
        # Attributs de mariage
        if GwFormattingRules.should_print_marriage_info(family, options):
            place = GwFormattingRules.format_marriage_place(family)
            if place:
                line += f" #mp {place}"
            
            source = GwFormattingRules.format_marriage_source(family, options)
            if source:
                line += f" #ms {source}"
        
        # Mère
        line += f" {GwFormatters._format_parent_name(mother, is_first_mother_def, has_printed_mother_parents, options)}"
        
        return line
    
    @staticmethod
    def _format_parent_name(person: Person, is_first_def: bool, 
                           has_printed_parents: bool, options) -> str:
        """
        Formate le nom d'un parent avec ses dates/attributs.
        Basé sur print_parent dans gwuLib.ml:466-490
        """
        name = GwFormattingRules.format_parent_name(person)
        
        if not GwFormattingRules.should_print_parent_dates(person, is_first_def, 
                                                          has_printed_parents, options):
            return name
        
        # Ajouter les attributs du parent
        attrs = []
        
        # Occupation
        if person.occupation:
            attrs.append(f"#occu {person.occupation}")
        
        # Sources
        if person.sources and not options.no_sources:
            for source in person.sources:
                attrs.append(f"#src {source}")
        
        # Dates
        if GwFormattingRules.has_infos(person, options):
            # Infos complètes
            birth_date = GwFormatters._extract_date(person.birth)
            death_date = GwFormatters._extract_date(person.death)
            
            if birth_date:
                attrs.append(GwFormattingRules.format_date(birth_date))
            elif death_date:
                attrs.append("0")
            
            if death_date:
                attrs.append(GwFormattingRules.format_date(death_date))
        else:
            # Juste "0" si nom valide
            attrs.append("0")
        
        if attrs:
            return f"{name} {' '.join(attrs)}"
        return name
    
    @staticmethod
    def _extract_date(date_obj) -> Optional[Date]:
        """Extrait la date d'un objet Event ou Date."""
        if not date_obj:
            return None
        if hasattr(date_obj, 'date'):  # C'est un Event
            return date_obj.date
        elif hasattr(date_obj, 'year'):  # C'est un objet Date
            return date_obj
        return None
    
    @staticmethod
    def _format_date(date: Date) -> str:
        """Formate une date selon les règles OCaml."""
        if not date or not hasattr(date, 'year'):
            return ""
        
        if date.year == 0:
            return ""
        
        if hasattr(date, 'day') and date.day > 0 and hasattr(date, 'month') and date.month > 0:
            return f"{date.day}/{date.month}/{date.year}"
        elif hasattr(date, 'month') and date.month > 0:
            return f"{date.month}/{date.year}"
        else:
            return str(date.year)
    
    @staticmethod
    def format_pevt_line(person: Person, options) -> str:
        """
        Formate la ligne 'pevt' selon les règles OCaml.
        """
        name = GwFormattingRules.format_parent_name(person)
        return f"pevt {name}"
    
    @staticmethod
    def format_pevt_events(person: Person, options) -> List[str]:
        """
        Formate les événements d'un pevt selon les règles OCaml.
        """
        events = []
        
        # Naissance
        if GwFormattingRules.has_birth(person) and not options.no_events:
            birth_date = GwFormatters._extract_date(person.birth)
            if birth_date:
                formatted_date = GwFormatters._format_date(birth_date)
                if formatted_date:
                    events.append(f"#birt {formatted_date}")
        
        # Décès
        if GwFormattingRules.has_death(person) and not options.no_events:
            death_date = GwFormatters._extract_date(person.death)
            if death_date:
                formatted_date = GwFormatters._format_date(death_date)
                if formatted_date:
                    events.append(f"#deat {formatted_date}")
                else:
                    events.append("#deat ")
        
        return events
    
    @staticmethod
    def format_family_sources(family: Family, options) -> List[str]:
        """
        Formate les sources de famille selon les règles OCaml.
        """
        sources = []
        
        if GwFormattingRules.should_print_family_sources(family, options):
            for source in family.sources:
                if isinstance(source, str) and source.startswith("csrc: "):
                    sources.append(f"csrc {source[6:]}")
                else:
                    sources.append(f"src {source}")
        
        return sources
    
    @staticmethod
    def format_family_events(family: Family, options) -> List[str]:
        """
        Formate les événements de famille selon les règles OCaml.
        """
        # Vérifier si on doit imprimer des événements ou des notes
        has_marriage = family.marriage is not None
        has_notes = family.notes and len(family.notes) > 0
        has_events = family.events and len(family.events) > 0
        
        if not (has_marriage or has_notes or has_events):
            return []
        
        events = ["fevt"]
        
        # Événement de mariage
        if family.marriage:
            event_line = "#marr"
            if hasattr(family.marriage, 'date') and family.marriage.date:
                event_line += f" {GwFormattingRules.format_date(family.marriage.date)}"
            if hasattr(family.marriage, 'place') and family.marriage.place:
                event_line += f" #p {family.marriage.place.name if hasattr(family.marriage.place, 'name') else family.marriage.place}"
            if hasattr(family.marriage, 'source') and family.marriage.source and not options.no_sources:
                event_line += f" #s {family.marriage.source}"
            # Toujours ajouter un espace à la fin si pas d'autres attributs
            if event_line == "#marr":
                event_line += " "
            events.append(event_line)
        
        # Notes de famille
        if family.notes:
            for note in family.notes:
                events.append(f"note {note}")
        
        # Autres événements
        for event in family.events:
            if event.event_type == EventType.MARRIAGE:
                # Déjà traité ci-dessus
                continue
            event_line = f"#{event.event_type.value.lower()}"
            if hasattr(event, 'date') and event.date:
                event_line += f" {GwFormattingRules.format_date(event.date)}"
            if hasattr(event, 'place') and event.place:
                event_line += f" #p {event.place.name if hasattr(event.place, 'name') else event.place}"
            if hasattr(event, 'source') and event.source and not options.no_sources:
                event_line += f" #s {event.source}"
            events.append(event_line)
        
        events.append("end fevt")
        return events
    
    @staticmethod
    def format_child_line(child: Person, family_surname: str, 
                         common_src: str, common_bp: str, options) -> str:
        """
        Formate la ligne d'un enfant selon les règles OCaml.
        Utilise le nouveau formateur d'enfants.
        """
        return GwChildFormatter.format_child_line(
            child, family_surname, common_src, common_bp, options
        )
