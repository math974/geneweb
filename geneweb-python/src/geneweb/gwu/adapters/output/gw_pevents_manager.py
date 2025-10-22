#!/usr/bin/env python3
"""
Gestionnaire dynamique des événements de personnes (pevt) selon les règles OCaml.
Basé sur get_persons_with_pevents et print_pevents dans gwuLib.ml
"""

from typing import List, Set, Dict, Optional
from geneweb.gwu.domain.entities.person import Person
from geneweb.gwu.domain.entities.family import Family
from geneweb.gwu.domain.entities.event import Event, EventType
from geneweb.gwu.adapters.output.gw_pevents_accumulator import PeventsCollector
from geneweb.gwu.adapters.output.gw_person_selector import PersonSelector
from geneweb.gwu.adapters.output.gw_pevents_filter import GwPeventsFilter
from geneweb.gwu.adapters.output.gw_dynamic_selector import DynamicPersonSelector
from geneweb.gwu.adapters.output.gw_isolation_analyzer import DynamicIsolationSelector


class PersonPeventsCollector:
    """Collecteur de personnes avec événements selon l'ordre OCaml."""
    
    def __init__(self):
        self._processed_persons: Set[str] = set()
        self._persons_with_pevents: List[Person] = []
    
    def collect_from_families(self, families: List[Family], persons: List[Person]) -> List[Person]:
        """
        Collecte les personnes avec événements à partir des familles.
        Basé sur get_persons_with_pevents dans gwuLib.ml:655-670
        """
        self._reset()
        person_lookup = self._build_person_lookup(persons)
        
        for family in families:
            self._process_family_persons(family, person_lookup)
        
        return self._persons_with_pevents.copy()
    
    def _reset(self) -> None:
        """Remet à zéro l'état du collecteur."""
        self._processed_persons.clear()
        self._persons_with_pevents.clear()
    
    def _build_person_lookup(self, persons: List[Person]) -> Dict[str, Person]:
        """Construit un index des personnes par ID."""
        return {person.person_id: person for person in persons}
    
    def _process_family_persons(self, family: Family, person_lookup: Dict[str, Person]) -> None:
        """Traite les personnes d'une famille selon l'ordre OCaml."""
        # Père (si a des événements et pas de parents)
        if family.father_id:
            self._add_person_if_has_pevents_and_no_parents(family.father_id, person_lookup)
        
        # Mère (si a des événements et pas de parents)
        if family.mother_id:
            self._add_person_if_has_pevents_and_no_parents(family.mother_id, person_lookup)
        
        # Enfants (si ont des événements)
        for child_id in family.children:
            self._add_person_if_has_pevents(child_id, person_lookup)
    
    def _add_person_if_has_pevents(self, person_id: str, person_lookup: Dict[str, Person]) -> None:
        """Ajoute une personne si elle a des événements et n'est pas déjà traitée."""
        if person_id in self._processed_persons:
            return
        
        person = person_lookup.get(person_id)
        if person and self._has_pevents(person):
            self._persons_with_pevents.append(person)
            self._processed_persons.add(person_id)
    
    def _add_person_if_has_pevents_and_no_parents(self, person_id: str, person_lookup: Dict[str, Person]) -> None:
        """Ajoute une personne si elle a des événements, pas de parents et n'est pas déjà traitée."""
        if person_id in self._processed_persons:
            return
        
        person = person_lookup.get(person_id)
        if person and self._has_pevents(person) and self._has_no_parents(person):
            self._persons_with_pevents.append(person)
            self._processed_persons.add(person_id)
    
    def _has_pevents(self, person: Person) -> bool:
        """Vérifie si une personne a des événements."""
        return (person.birth is not None or 
                person.death is not None or 
                person.baptism is not None or
                person.burial is not None or
                person.cremation is not None or
                (hasattr(person, 'events') and person.events))
    
    def _has_no_parents(self, person: Person) -> bool:
        """Vérifie si une personne n'a pas de parents."""
        return (not hasattr(person, 'father_id') or not person.father_id) and \
               (not hasattr(person, 'mother_id') or not person.mother_id)


class PeventFormatter:
    """Formateur d'événements selon les règles OCaml."""
    
    @staticmethod
    def format_pevent_line(person: Person) -> str:
        """
        Formate la ligne pevt pour une personne.
        Basé sur print_pevents_for_person dans gwuLib.ml:672-681
        """
        surname = person.surname.replace(' ', '_')
        first_name = person.first_name.replace(' ', '_')
        occ = f".{person.occ}" if person.occ > 0 else ""
        return f"pevt {surname} {first_name}{occ}"
    
    @staticmethod
    def format_pevent_events(person: Person) -> List[str]:
        """
        Formate les événements d'une personne.
        Basé sur print_pevent dans gwuLib.ml:569-650
        """
        events = []
        
        # Événements principaux (person.birth est un Date, pas un Event)
        if person.birth:
            events.append(PeventFormatter._format_date_event("#birt", person.birth))
        if person.baptism:
            events.append(PeventFormatter._format_date_event("#bapt", person.baptism))
        if person.death:
            events.append(PeventFormatter._format_date_event("#deat", person.death))
        if person.burial:
            events.append(PeventFormatter._format_date_event("#buri", person.burial))
        if person.cremation:
            events.append(PeventFormatter._format_date_event("#crem", person.cremation))
        
        # Autres événements
        if hasattr(person, 'events') and person.events:
            for event in person.events:
                event_type = PeventFormatter._get_event_type_marker(event.event_type)
                if event_type:
                    events.append(PeventFormatter._format_event(event_type, event))
        
        return events
    
    @staticmethod
    def _format_date_event(marker: str, date) -> str:
        """Formate un événement avec une date simple."""
        parts = [marker]
        
        # Date
        if date:
            date_str = PeventFormatter._format_date(date)
            if date_str:
                parts.append(date_str)
        
        return " ".join(parts)
    
    @staticmethod
    def _format_event(marker: str, event: Event) -> str:
        """Formate un événement individuel."""
        parts = [marker]
        
        # Date
        if event.date:
            date_str = PeventFormatter._format_date(event.date)
            if date_str:
                parts.append(date_str)
        
        # Lieu
        if hasattr(event, 'place') and event.place:
            parts.append(f"#p {event.place}")
        
        # Source
        if hasattr(event, 'source') and event.source:
            parts.append(f"#s {event.source}")
        
        return " ".join(parts)
    
    @staticmethod
    def _format_date(date) -> str:
        """Formate une date selon les règles OCaml."""
        if not date:
            return ""
        
        # Logique de formatage des dates (à implémenter selon les règles OCaml)
        return str(date)
    
    @staticmethod
    def _get_event_type_marker(event_type: EventType) -> Optional[str]:
        """Retourne le marqueur pour un type d'événement."""
        event_markers = {
            EventType.BIRTH: "#birt",
            EventType.BAPTISM: "#bapt", 
            EventType.DEATH: "#deat",
            EventType.BURIAL: "#buri",
            EventType.CREMATION: "#crem",
            EventType.ACCOMPLISHMENT: "#acco",
            EventType.ACQUISITION: "#acqu",
            EventType.ADHESION: "#adhe",
            EventType.BAPTISM_LDS: "#bapl",
            EventType.BAR_MITZVAH: "#barm",
            EventType.BAT_MITZVAH: "#basm",
            EventType.BENEDICTION: "#bles",
            EventType.CHANGE_NAME: "#chgn",
            EventType.CIRCUMCISION: "#circ",
            EventType.CONFIRMATION: "#conf",
            EventType.CONFIRMATION_LDS: "#conl",
            EventType.DECORATION: "#awar",
            EventType.DEMOBILISATION_MILITAIRE: "#demm",
            EventType.DIPLOMA: "#degr",
            EventType.DISTINCTION: "#dist",
            EventType.DOTATION: "#endl",
            EventType.DOTATION_LDS: "#dotl",
            EventType.EDUCATION: "#educ",
            EventType.ELECTION: "#elec",
            EventType.EMIGRATION: "#emig",
            EventType.EXCOMMUNICATION: "#exco",
            EventType.FAMILY_LINK_LDS: "#flkl",
            EventType.FIRST_COMMUNION: "#fcom",
            EventType.FUNERAL: "#fune",
        }
        return event_markers.get(event_type)


class GwPeventsManager:
    """Gestionnaire principal des événements de personnes selon les règles OCaml."""
    
    def __init__(self, options):
        """
        Initialise le gestionnaire d'événements.
        
        Args:
            options: Options de configuration (GwWriterOptions)
        """
        self.options = options
        self.collector = PersonPeventsCollector()
        self.formatter = PeventFormatter()
        self.pevents_collector = PeventsCollector()
        self.person_selector = PersonSelector()
        self.pevents_filter = GwPeventsFilter()
        self.dynamic_selector = DynamicPersonSelector()
        self.isolation_selector = DynamicIsolationSelector()
    
    def get_ordered_persons_with_pevents(self, families: List[Family], 
                                       persons: List[Person]) -> List[Person]:
        """
        Retourne les personnes avec événements dans l'ordre OCaml.
        Utilise la logique exacte de l'OCaml avec sélecteur d'isolation.
        """
        # Collecter toutes les personnes avec événements
        all_persons = self.pevents_collector.collect_from_families_and_accumulated(families, persons)
        
        # Utiliser le sélecteur basé sur l'analyse d'isolation OCaml
        selected_persons = self.isolation_selector.filter_persons(all_persons, families)
        
        return selected_persons
    
    def add_person_to_accumulator(self, person: Person) -> None:
        """Ajoute une personne à l'accumulateur (comme gen.pevents_pl_p)."""
        self.pevents_collector.add_person_to_accumulator(person)
    
    def reset_accumulator(self) -> None:
        """Remet à zéro l'accumulateur."""
        self.pevents_collector.reset_accumulator()
    
    def format_person_pevents(self, person: Person) -> List[str]:
        """
        Formate les événements d'une personne.
        """
        lines = []
        
        # Ligne pevt
        lines.append(self.formatter.format_pevent_line(person))
        
        # Événements
        events = self.formatter.format_pevent_events(person)
        lines.extend(events)
        
        # Ligne end pevt
        lines.append("end pevt")
        
        return lines
    
    def get_pevents_statistics(self, families: List[Family], 
                             persons: List[Person]) -> Dict[str, int]:
        """
        Retourne des statistiques sur les événements.
        """
        ordered_persons = self.get_ordered_persons_with_pevents(families, persons)
        total_persons = len(persons)
        persons_with_pevents = len(ordered_persons)
        
        return {
            "total_persons": total_persons,
            "persons_with_pevents": persons_with_pevents,
            "pevents_percentage": (persons_with_pevents / total_persons * 100) if total_persons > 0 else 0
        }
