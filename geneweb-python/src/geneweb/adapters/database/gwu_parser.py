"""Parser for GeneWeb text format (gwu output)."""

import re
import subprocess
from pathlib import Path
from typing import Optional
from datetime import date

from geneweb.domain.entities.person import Person, Sex
from geneweb.domain.entities.family import Family


class GwuParser:
    """Parser for GWU output format."""
    
    def __init__(self):
        """Initialize parser."""
        self.persons: dict[str, Person] = {}
        self.families: list[Family] = []
        self.person_id_counter = 0
        self.family_id_counter = 0
        self.person_key_to_id: dict[str, int] = {}
    
    def parse_date(self, date_str: str) -> Optional[date]:
        """Parse a date string."""
        if not date_str or date_str == '' or date_str.startswith('<') or date_str.startswith('~'):
            return None
        
        # Format: DD/MM/YYYY ou DD/MM/YY
        parts = date_str.strip().split('/')
        if len(parts) == 3:
            try:
                day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                if year < 100:
                    year += 1900 if year > 50 else 2000
                return date(year, month, day)
            except (ValueError, IndexError):
                return None
        return None
    
    def parse_person_key(self, line: str) -> str:
        """Extract person key from line."""
        # Format: "Surname FirstName.occ" ou "Surname FirstName"
        parts = line.split()
        if len(parts) >= 2:
            surname = parts[0]
            first_name = ' '.join(parts[1:])
            # Remove occ if present
            first_name = first_name.split('.')[0]
            return f"{first_name} {surname}"
        return line
    
    def parse_pevt(self, lines: list[str], idx: int) -> tuple[int, dict]:
        """Parse pevt (person events) block."""
        events = {}
        person_key = None
        
        while idx < len(lines):
            line = lines[idx].strip()
            
            if line.startswith('pevt '):
                person_key = self.parse_person_key(line[5:])
            elif line.startswith('#birt '):
                events['birth_date'] = self.parse_date(line[6:].split('#')[0].strip())
                if '#p ' in line:
                    events['birth_place'] = line.split('#p ')[1].split('#')[0].strip()
            elif line.startswith('#deat '):
                events['death_type'] = 'Dead'
                date_part = line[6:].split('#')[0].strip()
                events['death_date'] = self.parse_date(date_part)
                if '#p ' in line:
                    events['death_place'] = line.split('#p ')[1].split('#')[0].strip()
            elif line.startswith('#bapt '):
                if '#p ' in line:
                    events['baptism_place'] = line.split('#p ')[1].split('#')[0].strip()
            elif line.startswith('end pevt'):
                break
            
            idx += 1
        
        return idx, (person_key, events)
    
    def parse_family(self, lines: list[str], idx: int) -> tuple[int, Optional[Family]]:
        """Parse fam block."""
        family = None
        children = []
        father_key = None
        mother_key = None
        marriage_date = None
        marriage_place = None
        
        line = lines[idx].strip()
        
        # Parse family header: "fam Father + Mother" ou "fam Father +date Mother"
        if line.startswith('fam '):
            parts = line[4:].split('+')
            if len(parts) >= 2:
                father_key = self.parse_person_key(parts[0].strip())
                mother_part = parts[1].strip()
                # Remove date/place if present
                mother_key = mother_part.split('#')[0].strip()
                for word in mother_key.split():
                    if word and not word[0].isdigit() and '/' not in word:
                        mother_key = self.parse_person_key(' '.join(mother_key.split()[mother_key.split().index(word):]))
                        break
        
        idx += 1
        
        # Parse family content
        in_children = False
        while idx < len(lines):
            line = lines[idx].strip()
            
            if line.startswith('fevt'):
                # Parse family events
                idx += 1
                while idx < len(lines) and not lines[idx].strip().startswith('end fevt'):
                    evt_line = lines[idx].strip()
                    if evt_line.startswith('#marr '):
                        date_part = evt_line[6:].split('#')[0].strip()
                        marriage_date = self.parse_date(date_part)
                        if '#p ' in evt_line:
                            marriage_place = evt_line.split('#p ')[1].split('#')[0].strip()
                    idx += 1
            elif line.startswith('beg'):
                in_children = True
            elif line.startswith('end') and in_children:
                break
            elif line.startswith('- ') and in_children:
                # Parse child: "- h/f FirstName ..."
                sex = Sex.MALE if line[2] == 'h' else (Sex.FEMALE if line[2] == 'f' else Sex.UNKNOWN)
                child_info = line[4:].split()
                if child_info:
                    first_name = child_info[0]
                    birth_date_str = child_info[1] if len(child_info) > 1 else None
                    
                    # Get or create person
                    person_key = f"{first_name} (child)"
                    if person_key not in self.person_key_to_id:
                        person = Person(
                            id=self.person_id_counter,
                            first_name=first_name,
                            surname="",
                            sex=sex,
                            birth_date=self.parse_date(birth_date_str) if birth_date_str else None
                        )
                        self.persons[person_key] = person
                        self.person_key_to_id[person_key] = self.person_id_counter
                        self.person_id_counter += 1
                    
                    children.append(self.person_key_to_id[person_key])
            elif line.startswith('####|'):
                break
            
            idx += 1
        
        # Create family if we have parents
        if father_key or mother_key:
            father_id = self.person_key_to_id.get(father_key, 0)
            mother_id = self.person_key_to_id.get(mother_key, 0)
            
            family = Family(
                id=self.family_id_counter,
                father_id=father_id,
                mother_id=mother_id,
                children_ids=children if children else None,
                marriage_date=marriage_date,
                marriage_place=marriage_place
            )
            self.family_id_counter += 1
        
        return idx, family
    
    def parse(self, gwu_output: str) -> tuple[list[Person], list[Family]]:
        """Parse GWU output."""
        lines = gwu_output.split('\n')
        idx = 0
        person_events = {}
        
        while idx < len(lines):
            line = lines[idx].strip()
            
            if line.startswith('pevt '):
                idx, (person_key, events) = self.parse_pevt(lines, idx)
                person_events[person_key] = events
            elif line.startswith('fam '):
                idx, family = self.parse_family(lines, idx)
                if family:
                    self.families.append(family)
            
            idx += 1
        
        # Apply events to persons
        for person_key, events in person_events.items():
            if person_key in self.persons:
                person = self.persons[person_key]
                for key, value in events.items():
                    setattr(person, key, value)
        
        return list(self.persons.values()), self.families


def parse_gwu_output(gwu_path: Path, base_dir: Path, base_name: str) -> tuple[list[Person], list[Family]]:
    """Parse gwu output to extract persons and families."""
    try:
        # Run gwu to export the base
        result = subprocess.run(
            [str(gwu_path), str(base_dir / base_name)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return [], []
        
        # Parse the output
        parser = GwuParser()
        return parser.parse(result.stdout)
        
    except Exception:
        return [], []


class GwuCache:
    """Cache for gwu-exported data."""
    
    def __init__(self, gwu_path: Path):
        """Initialize cache."""
        self.gwu_path = gwu_path
        self._cache: dict[str, tuple[list[Person], list[Family]]] = {}
    
    def get_data(self, base_dir: Path, base_name: str) -> tuple[list[Person], list[Family]]:
        """Get cached data or parse from gwu."""
        cache_key = f"{base_dir}/{base_name}"
        
        if cache_key not in self._cache:
            self._cache[cache_key] = parse_gwu_output(self.gwu_path, base_dir, base_name)
        
        return self._cache[cache_key]
