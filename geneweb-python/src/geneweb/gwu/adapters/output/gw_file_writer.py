"""Writer pour fichiers .gw."""

from pathlib import Path
from typing import Set, Optional, List
from datetime import datetime

from geneweb.common.types import PersonId, FamilyId, Charset
from geneweb.gwu.domain.entities import Person, Family, Event, Date, Place, Note, Source, Title
from geneweb.gwu.domain.config import ExportOptions


class GwFileWriter:
    """
    Writer pour générer des fichiers .gw.
    
    Supporte toutes les options de format de gwu :
    - Encoding (UTF-8, ANSEL, etc.)
    - Format ancien (--old_gw)
    - Format gwplus (--gwplus)
    - Filtres (no_notes, no_src, no_evt)
    """

    def __init__(self, options: ExportOptions):
        """
        Initialise le writer.
        
        Args:
            options: Options d'export
        """
        self.options = options
        self.encoding = self._get_encoding()
        self.old_gw = options.old_gw
        self.gwplus = options.gw_plus
        self.no_notes = options.no_notes
        self.no_sources = options.no_sources
        self.no_events = options.no_events

    def write_database(
        self,
        output_path: Path,
        persons: List[Person],
        families: List[Family],
        selected_person_ids: Set[PersonId],
        selected_family_ids: Set[FamilyId]
    ) -> None:
        """
        Écrit une base de données complète au format .gw.
        
        Args:
            output_path: Chemin du fichier de sortie
            persons: Liste des personnes
            families: Liste des familles
            selected_person_ids: IDs des personnes sélectionnées
            selected_family_ids: IDs des familles sélectionnées
        """
        # Filtrer les personnes et familles sélectionnées
        selected_persons = [p for p in persons if p.person_id in selected_person_ids]
        selected_families = [f for f in families if f.family_id in selected_family_ids]
        
        # Générer le contenu
        content = self._generate_gw_content(selected_persons, selected_families)
        
        # Écrire le fichier
        with open(output_path, 'w', encoding=self.encoding) as f:
            f.write(content)

    def write_person(self, output_path: Path, person: Person) -> None:
        """
        Écrit une personne seule au format .gw.
        
        Args:
            output_path: Chemin du fichier de sortie
            person: Personne à écrire
        """
        # Générer le contenu avec en-tête
        lines = []
        lines.append(self._generate_header())
        lines.append(self._generate_person_content(person))
        content = '\n'.join(lines)
        
        with open(output_path, 'w', encoding=self.encoding) as f:
            f.write(content)

    def write_family(self, output_path: Path, family: Family) -> None:
        """
        Écrit une famille seule au format .gw.
        
        Args:
            output_path: Chemin du fichier de sortie
            family: Famille à écrire
        """
        # Générer le contenu avec en-tête
        lines = []
        lines.append(self._generate_header())
        lines.append(self._generate_family_content(family))
        content = '\n'.join(lines)
        
        with open(output_path, 'w', encoding=self.encoding) as f:
            f.write(content)

    def _generate_gw_content(self, persons: List[Person], families: List[Family]) -> str:
        """Génère le contenu complet d'un fichier .gw."""
        lines = []
        
        # En-tête
        lines.append(self._generate_header())
        
        # Personnes
        for person in persons:
            lines.append(self._generate_person_content(person))
        
        # Familles
        for family in families:
            lines.append(self._generate_family_content(family))
        
        return '\n'.join(lines)

    def _generate_header(self) -> str:
        """Génère l'en-tête du fichier .gw."""
        lines = []
        
        # Encoding (toujours ajouter)
        lines.append(f"encoding: {self.encoding.lower()}")
        
        # Gwplus
        if self.gwplus:
            lines.append("gwplus")
        
        return '\n'.join(lines)

    def _generate_person_content(self, person: Person) -> str:
        """Génère le contenu d'une personne."""
        lines = []
        
        # En-tête de la personne
        lines.append(f"# {person.format_key()}")
        
        # Sexe
        if person.sex.value != "unknown":
            lines.append(f"#sex {person.sex.value}")
        
        # Accès
        if not person.public:
            lines.append("#public n")
        if person.access.value != "public":
            lines.append(f"#access {person.access.value}")
        
        # Événements principaux
        if person.birth:
            lines.append(self._generate_event_line(person.birth, "birt"))
        if person.baptism:
            lines.append(self._generate_event_line(person.baptism, "bapt"))
        if person.death:
            lines.append(self._generate_event_line(person.death, "deat"))
        if person.burial:
            lines.append(self._generate_event_line(person.burial, "buri"))
        if person.cremation:
            lines.append(self._generate_event_line(person.cremation, "crem"))
        
        # Autres événements
        if not self.no_events:
            for event in person.events:
                event_type = getattr(event, 'event_type', None)
                if hasattr(event_type, 'value'):
                    lines.append(self._generate_event_line(event, event_type.value))
                else:
                    lines.append(self._generate_event_line(event, str(event_type) if event_type else 'unknown'))
        
        # Profession
        if person.occupation:
            lines.append(f"#occ {person.occupation}")
        
        # Titres
        for title in person.titles:
            lines.append(f"#titl {title.name}")
            if title.place:
                lines.append(f"#titl_place {title.place}")
            if title.date_start:
                lines.append(f"#titl_date_start {title.date_start}")
            if title.date_end:
                lines.append(f"#titl_date_end {title.date_end}")
        
        # Image
        if person.image:
            lines.append(f"#image {person.image}")
        
        # Notes
        if not self.no_notes and person.notes:
            if hasattr(person.notes, 'content'):
                lines.append(f"#note {person.notes.content}")
            else:
                # person.notes est une liste de chaînes
                for note in person.notes:
                    lines.append(f"#note {note}")
        
        # Sources
        if not self.no_sources:
            for source in person.sources:
                if hasattr(source, 'reference'):
                    lines.append(f"#src {source.reference}")
                else:
                    lines.append(f"#src {source}")
        
        return '\n'.join(lines)

    def _generate_family_content(self, family: Family) -> str:
        """Génère le contenu d'une famille."""
        lines = []
        
        # En-tête de la famille
        lines.append(f"#f {family.father_id} {family.mother_id}")
        
        # Enfants
        for child_id in family.children:
            lines.append(f"#c {child_id}")
        
        # Événements d'union
        if family.marriage:
            lines.append(self._generate_event_line(family.marriage, "marr"))
        if family.marriage_bann:
            lines.append(self._generate_event_line(family.marriage_bann, "marb"))
        if family.marriage_contract:
            lines.append(self._generate_event_line(family.marriage_contract, "marc"))
        if family.marriage_license:
            lines.append(self._generate_event_line(family.marriage_license, "marl"))
        if family.engagement:
            lines.append(self._generate_event_line(family.engagement, "enga"))
        
        # Événements de séparation
        if family.divorce:
            lines.append(self._generate_event_line(family.divorce, "div"))
        if family.separated:
            lines.append(self._generate_event_line(family.separated, "sepa"))
        if family.annulment:
            lines.append(self._generate_event_line(family.annulment, "annu"))
        
        # Autres événements
        if not self.no_events:
            for event in family.events:
                event_type = getattr(event, 'event_type', None)
                if hasattr(event_type, 'value'):
                    lines.append(self._generate_event_line(event, event_type.value))
                else:
                    lines.append(self._generate_event_line(event, str(event_type) if event_type else 'unknown'))
        
        # Témoins
        for witness in family.witnesses:
            lines.append(f"#wit {witness.person_id}")
            if witness.witness_kind != "witness":
                lines.append(f"#wit_kind {witness.witness_kind}")
        
        # Notes
        if not self.no_notes and family.notes:
            if hasattr(family.notes, 'content'):
                lines.append(f"#note {family.notes.content}")
            else:
                # family.notes est une liste de chaînes
                for note in family.notes:
                    lines.append(f"#note {note}")
        
        # Sources
        if not self.no_sources:
            for source in family.sources:
                if hasattr(source, 'reference'):
                    lines.append(f"#src {source.reference}")
                else:
                    lines.append(f"#src {source}")
        
        return '\n'.join(lines)

    def _generate_event_line(self, event: Event, event_type: str) -> str:
        """Génère une ligne d'événement."""
        parts = [f"#{event_type}"]
        
        # Date
        if hasattr(event, 'date') and event.date:
            if hasattr(event.date, 'to_gw_format'):
                parts.append(event.date.to_gw_format(old_gw=self.old_gw))
            else:
                parts.append(str(event.date))
        
        # Lieu
        if hasattr(event, 'place') and event.place:
            if hasattr(event.place, 'name'):
                parts.append(f"#p {event.place.name}")
            else:
                parts.append(f"#p {event.place}")
        
        # Source
        if hasattr(event, 'source') and event.source:
            parts.append(f"#s {event.source}")
        
        return " ".join(parts)

    def _get_encoding(self) -> str:
        """Détermine l'encoding à utiliser."""
        if hasattr(self.options, 'encoding') and self.options.encoding:
            return self.options.encoding
        return "UTF-8"
