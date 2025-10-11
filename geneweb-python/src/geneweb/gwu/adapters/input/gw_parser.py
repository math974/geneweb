"""Parser for .gw (GeneWeb text format) files."""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, TextIO, Iterator
from pathlib import Path

from geneweb.common.types import Sex, EventType, PersonId, FamilyId
from geneweb.gwu.domain.entities import (
    Person,
    Family,
    Event,
    Date,
    Place,
    Note,
    Source,
)
from geneweb.gwu.adapters.input.date_parser import DateParser


@dataclass
class GwDatabase:
    """
    Représentation intermédiaire d'une base .gw.
    
    Contient toutes les données parsées avant conversion en entités du domaine.
    """
    
    encoding: str = "utf-8"
    persons: Dict[str, Person] = field(default_factory=dict)
    families: List[Family] = field(default_factory=list)
    notes_map: Dict[str, str] = field(default_factory=dict)  # key -> note content


class GwParser:
    """
    Parser pour fichiers .gw (format texte GeneWeb).
    
    Lit un fichier .gw ligne par ligne et construit les entités Person et Family.
    """
    
    def __init__(self):
        self.database = GwDatabase()
        self.person_counter = 0
        self.family_counter = 0
    
    def parse_file(self, file_path: Path) -> GwDatabase:
        """
        Parse un fichier .gw et retourne la base de données.
        
        Args:
            file_path: Chemin du fichier .gw
        
        Returns:
            GwDatabase avec toutes les entités parsées
        """
        with open(file_path, "r", encoding="utf-8") as f:
            return self.parse_stream(f)
    
    def parse_stream(self, stream: TextIO) -> GwDatabase:
        """
        Parse un flux texte .gw.
        
        Args:
            stream: Flux texte à parser
        
        Returns:
            GwDatabase avec toutes les entités parsées
        """
        lines = stream.readlines()
        self._parse_lines(lines)
        return self.database
    
    def _parse_lines(self, lines: List[str]) -> None:
        """Parse toutes les lignes du fichier."""
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Ligne vide ou commentaire
            if not line or line.startswith("#"):
                i += 1
                continue
            
            # Encoding
            if line.startswith("encoding:"):
                self.database.encoding = line.split(":", 1)[1].strip()
                i += 1
                continue
            
            # gwplus
            if line == "gwplus":
                i += 1
                continue
            
            # Famille (fam)
            if line.startswith("fam "):
                i = self._parse_family(lines, i)
                continue
            
            # Événements de personne (pevt)
            if line.startswith("pevt "):
                i = self._parse_person_events(lines, i)
                continue
            
            # Notes
            if line.startswith("notes "):
                i = self._parse_notes(lines, i)
                continue
            
            # Sources (ignorées pour l'instant)
            if line.startswith("src ") or line.startswith("csrc "):
                i += 1
                continue
            
            i += 1
    
    def _parse_family(self, lines: List[str], start_idx: int) -> int:
        """
        Parse une définition de famille.
        
        Returns:
            Index de la ligne suivante à parser
        """
        line = lines[start_idx].strip()
        
        # Extraire père et mère depuis "fam Nom Prénom ... + Nom Prénom ..."
        parts = line[4:].split("+")  # Enlever "fam "
        
        if len(parts) < 2:
            # Famille incomplète
            return start_idx + 1
        
        father_str = parts[0].strip()
        mother_str = parts[1].strip()
        
        # Parse père et mère
        father = self._parse_person_ref(father_str, Sex.MALE)
        mother = self._parse_person_ref(mother_str, Sex.FEMALE)
        
        # Créer la famille
        family_id = f"F{self.family_counter}"
        self.family_counter += 1
        
        family = Family(
            family_id=family_id,
            father_id=father.person_id,
            mother_id=mother.person_id,
        )
        
        # Ajouter père et mère à la base si pas déjà présents
        if father.person_id not in self.database.persons:
            self.database.persons[father.person_id] = father
        if mother.person_id not in self.database.persons:
            self.database.persons[mother.person_id] = mother
        
        # Ajouter la famille aux conjoints
        father_in_db = self.database.persons[father.person_id]
        mother_in_db = self.database.persons[mother.person_id]
        father_in_db.spouses.append(family_id)
        mother_in_db.spouses.append(family_id)
        
        # Parser les enfants et événements
        idx = start_idx + 1
        idx = self._parse_family_content(lines, idx, family)
        
        self.database.families.append(family)
        return idx
    
    def _parse_family_content(
        self, lines: List[str], start_idx: int, family: Family
    ) -> int:
        """
        Parse le contenu d'une famille (enfants, événements).
        
        Returns:
            Index de la ligne suivante
        """
        idx = start_idx
        
        while idx < len(lines):
            line = lines[idx].strip()
            
            # Fin de la famille (ligne vide ou nouveau bloc)
            if not line or line.startswith("fam ") or line.startswith("pevt ") or line.startswith("notes "):
                break
            
            # Sources (ignorées pour l'instant)
            if line.startswith("src ") or line.startswith("csrc "):
                idx += 1
                continue
            
            # Événements de famille
            if line == "fevt":
                idx = self._parse_family_events(lines, idx + 1, family)
                continue
            
            # Enfants
            if line == "beg":
                idx = self._parse_children(lines, idx + 1, family)
                continue
            
            idx += 1
        
        return idx
    
    def _parse_family_events(
        self, lines: List[str], start_idx: int, family: Family
    ) -> int:
        """Parse les événements d'une famille."""
        idx = start_idx
        
        while idx < len(lines):
            line = lines[idx].strip()
            
            if line == "end fevt":
                return idx + 1
            
            # Parser les événements
            if line.startswith("#"):
                event = self._parse_event_line(line)
                if event:
                    # Associer l'événement à la famille
                    if event.event_type == EventType.MARRIAGE:
                        family.marriage = event
                    elif event.event_type == EventType.DIVORCE:
                        family.divorce = event
                    elif event.event_type == EventType.ENGAGEMENT:
                        family.engagement = event
                    elif event.event_type == EventType.MARRIAGE_CONTRACT:
                        family.marriage_contract = event
                    elif event.event_type == EventType.SEPARATED:
                        family.separated = event
                    elif event.event_type == EventType.ANNULMENT:
                        family.annulment = event
                    else:
                        family.events.append(event)
            
            idx += 1
        
        return idx
    
    def _parse_children(
        self, lines: List[str], start_idx: int, family: Family
    ) -> int:
        """Parse les enfants d'une famille."""
        idx = start_idx
        
        # Récupérer le nom de famille du père
        father = self.database.persons[family.father_id]
        family_surname = father.surname
        
        while idx < len(lines):
            line = lines[idx].strip()
            
            if line == "end":
                return idx + 1
            
            # Enfant homme ou femme
            if line.startswith("- h ") or line.startswith("- f "):
                sex = Sex.MALE if line.startswith("- h ") else Sex.FEMALE
                child_str = line[4:].strip()  # Enlever "- h " ou "- f "
                
                # Parser l'enfant avec le nom de famille hérité
                child = self._parse_child_ref(child_str, family_surname, sex)
                
                # Ajouter l'enfant à la base si pas déjà présent
                if child.person_id not in self.database.persons:
                    self.database.persons[child.person_id] = child
                
                # Lier l'enfant à ses parents
                child_in_db = self.database.persons[child.person_id]
                child_in_db.parents = family.family_id
                
                # Ajouter l'enfant à la famille
                family.add_child(child.person_id)
            
            idx += 1
        
        return idx
    
    def _parse_person_ref(self, person_str: str, sex: Sex) -> Person:
        """
        Parse une référence de personne (Nom Prénom.occ).
        
        Args:
            person_str: String contenant le nom complet
            sex: Sexe de la personne
        
        Returns:
            Person créée
        """
        # Extraire les parties (gérer les attributs #occu, #src, dates, etc.)
        tokens = person_str.split()
        
        if len(tokens) < 2:
            # Nom incomplet
            return Person(
                person_id=f"P{self.person_counter}",
                first_name="?",
                surname="?",
                sex=sex,
            )
        
        surname = tokens[0]
        first_name_with_occ = tokens[1]
        
        # Séparer prénom et occurrence
        if "." in first_name_with_occ:
            parts = first_name_with_occ.split(".")
            first_name = parts[0]
            try:
                occ = int(parts[1])
            except (ValueError, IndexError):
                occ = 0
        else:
            first_name = first_name_with_occ
            occ = 0
        
        # Remplacer les underscores par des espaces dans le prénom
        first_name = first_name.replace("_", " ")
        
        # Générer un ID unique basé sur le nom
        person_id = f"P{self.person_counter}"
        self.person_counter += 1
        
        return Person(
            person_id=person_id,
            first_name=first_name,
            surname=surname,
            occ=occ,
            sex=sex,
        )
    
    def _parse_child_ref(self, child_str: str, family_surname: str, sex: Sex) -> Person:
        """
        Parse une référence d'enfant (Prénom.occ dates...).
        
        Les enfants héritent du nom de famille du père.
        
        Args:
            child_str: String contenant le prénom et attributs
            family_surname: Nom de famille hérité
            sex: Sexe de l'enfant
        
        Returns:
            Person créée
        """
        # Extraire les parties (prénom, dates, attributs)
        tokens = child_str.split()
        
        if len(tokens) < 1:
            # Prénom manquant
            return Person(
                person_id=f"P{self.person_counter}",
                first_name="?",
                surname=family_surname,
                sex=sex,
            )
        
        first_name_with_occ = tokens[0]
        
        # Séparer prénom et occurrence
        if "." in first_name_with_occ:
            parts = first_name_with_occ.split(".")
            first_name = parts[0]
            try:
                occ = int(parts[1])
            except (ValueError, IndexError):
                occ = 0
        else:
            first_name = first_name_with_occ
            occ = 0
        
        # Remplacer les underscores par des espaces dans le prénom
        first_name = first_name.replace("_", " ")
        
        # Générer un ID unique basé sur le nom
        person_id = f"P{self.person_counter}"
        self.person_counter += 1
        
        return Person(
            person_id=person_id,
            first_name=first_name,
            surname=family_surname,
            occ=occ,
            sex=sex,
        )
    
    def _parse_person_events(self, lines: List[str], start_idx: int) -> int:
        """Parse les événements d'une personne (pevt)."""
        line = lines[start_idx].strip()
        
        # Extraire nom de la personne
        person_name = line[5:].strip()  # Enlever "pevt "
        
        # Trouver la personne dans la base
        person = self._find_person_by_name(person_name)
        
        idx = start_idx + 1
        while idx < len(lines):
            line = lines[idx].strip()
            
            if line == "end pevt":
                return idx + 1
            
            # Parser les événements
            if person and line.startswith("#"):
                event = self._parse_event_line(line)
                if event:
                    # Associer l'événement à la personne
                    if event.event_type == EventType.BIRTH:
                        person.birth = event
                    elif event.event_type == EventType.BAPTISM:
                        person.baptism = event
                    elif event.event_type == EventType.DEATH:
                        person.death = event
                    elif event.event_type == EventType.BURIAL:
                        person.burial = event
                    elif event.event_type == EventType.CREMATION:
                        person.cremation = event
                    else:
                        person.events.append(event)
            
            idx += 1
        
        return idx
    
    def _find_person_by_name(self, name: str) -> Optional[Person]:
        """
        Trouve une personne par son nom complet (Nom Prénom.occ).
        
        Args:
            name: Nom complet "Nom Prénom" ou "Nom Prénom.occ"
        
        Returns:
            Person trouvée ou None
        """
        # Parser le nom
        tokens = name.split()
        if len(tokens) < 2:
            return None
        
        surname = tokens[0]
        first_name_with_occ = tokens[1]
        
        # Séparer prénom et occurrence
        if "." in first_name_with_occ:
            parts = first_name_with_occ.split(".")
            first_name = parts[0].replace("_", " ")
            try:
                occ = int(parts[1])
            except (ValueError, IndexError):
                occ = 0
        else:
            first_name = first_name_with_occ.replace("_", " ")
            occ = 0
        
        # Chercher dans la base
        for person in self.database.persons.values():
            if (person.surname == surname and 
                person.first_name == first_name and 
                person.occ == occ):
                return person
        
        return None
    
    def _parse_event_line(self, line: str) -> Optional[Event]:
        """
        Parse une ligne d'événement (#birt, #deat, etc.).
        
        Args:
            line: Ligne commençant par # (ex: "#birt 1789 #p Paris")
        
        Returns:
            Event parsé ou None
        """
        # Mapping des tags vers EventType
        event_map = {
            "#birt": EventType.BIRTH,
            "#bapm": EventType.BAPTISM,
            "#deat": EventType.DEATH,
            "#buri": EventType.BURIAL,
            "#crem": EventType.CREMATION,
            "#marr": EventType.MARRIAGE,
            "#div": EventType.DIVORCE,
            "#enga": EventType.ENGAGEMENT,
        }
        
        # Trouver le type d'événement
        event_type = None
        for tag, etype in event_map.items():
            if line.startswith(tag):
                event_type = etype
                line = line[len(tag):].strip()
                break
        
        if not event_type:
            return None
        
        # Parser les attributs de l'événement
        date = None
        place = None
        source = None
        
        # Split par # pour trouver les attributs
        parts = line.split("#")
        
        # Première partie = date (si présente)
        if parts[0].strip():
            date = DateParser.parse(parts[0].strip())
        
        # Parser les autres attributs
        for part in parts[1:]:
            part = part.strip()
            if part.startswith("p "):
                # Lieu
                place_str = part[2:].strip()
                place = Place(name=place_str)
            elif part.startswith("s "):
                # Source
                source_str = part[2:].strip()
                source = source_str
            elif part.startswith("bp "):
                # Birth place
                place_str = part[3:].strip()
                place = Place(name=place_str)
            elif part.startswith("dp "):
                # Death place
                place_str = part[3:].strip()
                place = Place(name=place_str)
            elif part.startswith("mp "):
                # Marriage place
                place_str = part[3:].strip()
                place = Place(name=place_str)
        
        return Event(
            event_type=event_type,
            date=date,
            place=place,
            source=source,
        )
    
    def _parse_notes(self, lines: List[str], start_idx: int) -> int:
        """Parse les notes d'une personne."""
        line = lines[start_idx].strip()
        
        # Extraire nom de la personne
        person_name = line[6:].strip()  # Enlever "notes "
        
        idx = start_idx + 1
        if idx < len(lines) and lines[idx].strip() == "beg":
            idx += 1
            note_lines = []
            
            while idx < len(lines):
                line = lines[idx].strip()
                
                if line == "end notes":
                    # Stocker la note
                    note_content = "\n".join(note_lines)
                    self.database.notes_map[person_name] = note_content
                    return idx + 1
                
                note_lines.append(lines[idx].rstrip())
                idx += 1
        
        return idx
    
    def get_all_persons(self) -> Iterator[Person]:
        """Retourne un itérateur sur toutes les personnes."""
        return iter(self.database.persons.values())
    
    def get_all_families(self) -> Iterator[Family]:
        """Retourne un itérateur sur toutes les familles."""
        return iter(self.database.families)
    
    def get_person_count(self) -> int:
        """Retourne le nombre de personnes."""
        return len(self.database.persons)
    
    def get_family_count(self) -> int:
        """Retourne le nombre de familles."""
        return len(self.database.families)
