"""Parser for .gw (GeneWeb text format) files."""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, TextIO, Iterator
from pathlib import Path

from geneweb.common.types import Sex, EventType, PersonId, FamilyId, DatePrecision
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
    gwplus: bool = False
    persons: Dict[str, Person] = field(default_factory=dict)
    families: List[Family] = field(default_factory=list)
    sources: List[Dict[str, str]] = field(default_factory=list)  # sources et csrc
    notes_map: Dict[str, str] = field(default_factory=dict)  # key -> note content
    person_key_index: Dict[tuple, str] = field(default_factory=dict)  # (first_name, surname, occ) -> person_id


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
        # Associer les notes aux personnes après le parsing complet
        self._associate_notes_to_persons()
        
        return self.database
    
    def _associate_notes_to_persons(self) -> None:
        """Associe les notes parsées aux personnes correspondantes."""
        for person_name, note_content in self.database.notes_map.items():
            # Trouver la personne correspondante
            person = self._find_person_by_name(person_name)
            if person:
                person.notes = note_content
    
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
                self.database.gwplus = True
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
            
            # Événements de famille (fevt)
            if line.startswith("fevt"):
                i = self._parse_family_events(lines, i)
                continue
            
            # Notes
            if line.startswith("notes "):
                i = self._parse_notes(lines, i)
                continue
            
            # Notes de base
            if line.startswith("notes-db"):
                i = self._parse_notes_db(lines, i)
                continue
            
            # Pages étendues
            if line.startswith("page-ext "):
                i = self._parse_page_ext(lines, i)
                continue
            
            # Sources
            if line.startswith("src ") or line.startswith("csrc "):
                i = self._parse_source(lines, i)
                continue
            
            i += 1
    
    def _parse_family(self, lines: List[str], start_idx: int) -> int:
        """
        Parse une définition de famille.
        
        Returns:
            Index de la ligne suivante à parser
        """
        line = lines[start_idx].strip()
        
        # Extraire père et mère depuis "fam Nom Prénom ... + date_mariage Nom Prénom ..."
        parts = line[4:].split("+")  # Enlever "fam "
        
        if len(parts) < 2:
            # Famille incomplète
            return start_idx + 1
        
        father_str = parts[0].strip()
        mother_part = parts[1].strip()
        
        # Extraire la date de mariage et ses attributs si présents
        # Format: "date #mp place #ms source nom_mere prenom_mere ..."
        mother_tokens = mother_part.split()
        marriage_date = None
        mother_start_idx = 0
        
        # Vérifier si le premier token est une date (contient "/" ou "<" ou ">" ou "~" ou est un nombre)
        if mother_tokens and (('/' in mother_tokens[0] or 
                               mother_tokens[0].startswith(('<', '>', '~')) or
                               mother_tokens[0].isdigit())):
            marriage_date = mother_tokens[0]
            mother_start_idx = 1
        else:
            # Pas de date de mariage, mais on peut avoir des attributs #mp et #ms
            mother_start_idx = 0
        
        # Sauter les attributs #mp et #ms (avec ou sans date de mariage)
        while mother_start_idx < len(mother_tokens):
            token = mother_tokens[mother_start_idx]
            if token in ('#mp', '#ms'):
                # Attribut de mariage, on saute le tag et sa valeur
                mother_start_idx += 1
                if mother_start_idx < len(mother_tokens) and not mother_tokens[mother_start_idx].startswith('#'):
                    mother_start_idx += 1
            else:
                # C'est le début du nom de la mère (ou #src qui fait partie de la mère)
                break
        
        # Reconstituer la chaîne de la mère sans la date de mariage et ses attributs
        mother_str = ' '.join(mother_tokens[mother_start_idx:])
        
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
            sources=[],
            events=[],
            notes=[]
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
            
            # Sources (traitement complet)
            if line.startswith("src ") or line.startswith("csrc "):
                idx = self._parse_source(lines, idx, family)
                continue
            
            # Événements de famille
            if line == "fevt":
                idx = self._parse_family_events_detailed(lines, idx + 1, family)
                continue
            
            # Enfants
            if line == "beg":
                idx = self._parse_children(lines, idx + 1, family)
                continue
            
            idx += 1
        
        return idx
    
    def _parse_family_events_detailed(
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
            # Parser les notes
            elif line.startswith("note "):
                note_content = line[5:].strip()  # Enlever "note "
                if not hasattr(family, 'notes') or family.notes is None:
                    family.notes = []
                family.notes.append(note_content)
            
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
    
    def _get_or_create_person(
        self, first_name: str, surname: str, occ: int, sex: Sex
    ) -> Person:
        """
        Récupère une personne existante ou en crée une nouvelle (déduplication).
        
        Utilise l'index par clé (first_name, surname, occ) pour éviter les doublons.
        
        Args:
            first_name: Prénom
            surname: Nom de famille
            occ: Occurrence
            sex: Sexe
        
        Returns:
            Person (existante ou nouvellement créée)
        """
        # Créer la clé de recherche
        key = (first_name, surname, occ)
        
        # Vérifier si la personne existe déjà
        if key in self.database.person_key_index:
            person_id = self.database.person_key_index[key]
            person = self.database.persons[person_id]
            
            # Mettre à jour le sexe si nécessaire (si c'était UNKNOWN)
            if person.sex == Sex.UNKNOWN and sex != Sex.UNKNOWN:
                person.sex = sex
            
            return person
        
        # Créer une nouvelle personne
        person_id = f"P{self.person_counter}"
        self.person_counter += 1
        
        person = Person(
            person_id=person_id,
            first_name=first_name,
            surname=surname,
            occ=occ,
            sex=sex,
        )
        
        # Ajouter à la base et à l'index
        self.database.persons[person_id] = person
        self.database.person_key_index[key] = person_id
        
        return person
    
    def _parse_person_ref(self, person_str: str, sex: Sex) -> Person:
        """
        Parse une référence de personne (Nom Prénom.occ #attributs).
        
        Args:
            person_str: String contenant le nom complet et attributs
            sex: Sexe de la personne
        
        Returns:
            Person (récupérée ou créée avec déduplication)
        """
        # Extraire les parties (gérer les attributs #occu, #src, dates, etc.)
        tokens = person_str.split()
        
        if len(tokens) < 2:
            # Nom incomplet - créer sans déduplication
            person_id = f"P{self.person_counter}"
            self.person_counter += 1
            return Person(
                person_id=person_id,
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
        
        # Utiliser la déduplication
        person = self._get_or_create_person(first_name, surname, occ, sex)
        
        # Parser les attributs (#occu, #src, dates)
        self._parse_person_attributes(tokens[2:], person)
        
        return person
    
    def _parse_person_attributes(self, tokens: List[str], person: Person) -> None:
        """
        Parse les attributs d'une personne (#occu, #src, dates).
        
        Args:
            tokens: Liste des tokens à parser
            person: Personne à mettre à jour
        """
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token == "#occu":
                # Occupation
                if i + 1 < len(tokens):
                    person.occupation = tokens[i + 1]
                    i += 2
                else:
                    i += 1
            elif token == "#src":
                # Source
                if i + 1 < len(tokens):
                    person.sources.append(tokens[i + 1])
                    i += 2
                else:
                    i += 1
            elif token.startswith("#"):
                # Autre attribut - ignorer pour l'instant
                i += 1
            else:
                # Date - parser si possible
                date_str = token
                if i + 1 < len(tokens) and not tokens[i + 1].startswith("#"):
                    # Date suivie d'une autre date (naissance décès)
                    date_str += " " + tokens[i + 1]
                    i += 2
                else:
                    i += 1
                
                # Parser la date
                self._parse_date_attribute(date_str, person)
    
    def _parse_date_attribute(self, date_str: str, person: Person) -> None:
        """
        Parse une date d'attribut (naissance décès).
        
        Args:
            date_str: String contenant la date (ex: "1814 1/1/1835")
            person: Personne à mettre à jour
        """
        # Séparer les dates de naissance et décès
        dates = date_str.split()
        
        if len(dates) >= 1:
            # Date de naissance
            birth_date = self._parse_single_date(dates[0])
            if birth_date:
                person.birth = birth_date
        
        if len(dates) >= 2:
            # Date de décès
            death_date = self._parse_single_date(dates[1])
            if death_date:
                person.death = death_date
    
    def _parse_single_date(self, date_str: str):
        """
        Parse une date simple.
        
        Args:
            date_str: String contenant la date (ex: "1814", "1/1/1835")
        
        Returns:
            Date object ou None
        """
        if not date_str:
            return None
        
        # Date simple (année)
        if date_str.isdigit():
            return Date(year=int(date_str), precision=DatePrecision.SURE)
        
        # Date avec mois et jour (1/1/1835)
        if "/" in date_str:
            parts = date_str.split("/")
            if len(parts) == 3:
                try:
                    day = int(parts[0])
                    month = int(parts[1])
                    year = int(parts[2])
                    return Date(year=year, month=month, day=day, precision=DatePrecision.SURE)
                except ValueError:
                    pass
        
        # Date avec mois et année (1/1835)
        if "/" in date_str and date_str.count("/") == 1:
            parts = date_str.split("/")
            if len(parts) == 2:
                try:
                    month = int(parts[0])
                    year = int(parts[1])
                    return Date(year=year, month=month, precision=DatePrecision.SURE)
                except ValueError:
                    pass
        
        return None
    
    def _parse_child_ref(self, child_str: str, family_surname: str, sex: Sex) -> Person:
        """
        Parse une référence d'enfant (Prénom.occ dates...).
        
        Les enfants héritent du nom de famille du père.
        
        Args:
            child_str: String contenant le prénom et attributs
            family_surname: Nom de famille hérité
            sex: Sexe de l'enfant
        
        Returns:
            Person (récupérée ou créée avec déduplication)
        """
        # Extraire les parties (prénom, dates, attributs)
        tokens = child_str.split()
        
        if len(tokens) < 1:
            # Prénom manquant - créer sans déduplication
            person_id = f"P{self.person_counter}"
            self.person_counter += 1
            return Person(
                person_id=person_id,
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
        
        # Utiliser la déduplication
        person = self._get_or_create_person(first_name, family_surname, occ, sex)
        
        # Parser les attributs (#occu, #src, dates)
        self._parse_person_attributes(tokens[1:], person)
        
        return person
    
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
    
    def _parse_source(self, lines: List[str], start_idx: int, family: Family = None) -> int:
        """
        Parse une source (src ou csrc).
        
        Returns:
            Index de la ligne suivante à parser
        """
        line = lines[start_idx].strip()
        
        # Extraire le contenu de la source
        if line.startswith("src "):
            source_text = line[4:].strip()
            # Ajouter la source à la famille si disponible
            if family:
                family.sources.append(source_text)
            # Stocker la source dans la base de données
            if not hasattr(self.database, 'sources'):
                self.database.sources = []
            self.database.sources.append({
                'type': 'src',
                'text': source_text,
                'family_id': family.family_id if family else None
            })
        elif line.startswith("csrc "):
            source_text = line[5:].strip()
            # Ajouter la source de couple à la famille si disponible
            if family:
                family.sources.append(f"csrc: {source_text}")
            # Stocker la source de couple dans la base de données
            if not hasattr(self.database, 'sources'):
                self.database.sources = []
            self.database.sources.append({
                'type': 'csrc',
                'text': source_text,
                'family_id': family.family_id if family else None
            })
        
        return start_idx + 1
    
    def _parse_family_events(self, lines: List[str], start_idx: int, family: Family = None) -> int:
        """
        Parse les événements d'une famille (fevt).
        
        Returns:
            Index de la ligne suivante à parser
        """
        idx = start_idx
        events = []
        notes = []
        
        while idx < len(lines):
            line = lines[idx].strip()
            if line == "end fevt":
                # Stocker les événements et notes dans la famille
                if family:
                    family.events = events
                    family.notes = notes
                return idx + 1
            
            # Parser les événements de famille
            if line.startswith("#marr"):
                events.append(line)
            elif line.startswith("#div"):
                events.append(line)
            elif line.startswith("#"):
                events.append(line)
            elif line.startswith("note "):
                notes.append(line[5:].strip())
            
            idx += 1
        
        return idx
    
    def _parse_notes_db(self, lines: List[str], start_idx: int) -> int:
        """
        Parse les notes de base (notes-db).
        
        Returns:
            Index de la ligne suivante à parser
        """
        # Collecter le contenu des notes de base
        notes_content = []
        idx = start_idx + 1
        while idx < len(lines):
            line = lines[idx].strip()
            if line == "end notes-db":
                # Stocker les notes de base
                if not hasattr(self.database, 'notes_db'):
                    self.database.notes_db = ""
                self.database.notes_db = '\n'.join(notes_content)
                return idx + 1
            notes_content.append(line)
            idx += 1
        
        return idx
    
    def _parse_page_ext(self, lines: List[str], start_idx: int) -> int:
        """
        Parse une page étendue (page-ext).
        
        Returns:
            Index de la ligne suivante à parser
        """
        line = lines[start_idx].strip()
        # Extraire le nom de la page
        page_name = line[9:].strip()  # Enlever "page-ext "
        
        # Collecter le contenu de la page
        page_content = []
        idx = start_idx + 1
        while idx < len(lines):
            line = lines[idx].strip()
            if line == "end page-ext":
                # Stocker la page étendue
                if not hasattr(self.database, 'pages_ext'):
                    self.database.pages_ext = {}
                self.database.pages_ext[page_name] = '\n'.join(page_content)
                return idx + 1
            page_content.append(line)
            idx += 1
        
        return idx
