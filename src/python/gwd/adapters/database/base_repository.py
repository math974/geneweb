"""Repository Pattern pour les Bases - 20 lignes max"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from datetime import date
import sys
from pathlib import Path

# Add lib directory to path for MessagePack imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from lib.db.io.msgpack import MessagePackReader
    from lib.db.models.person import GenPerson
    from lib.db.models.family import GenFamily
    from lib.db.core.types import Iper, Ifam
    from lib.db.models.events import Date as GenDate
except ImportError:
    # Fallback for absolute imports
    pass

from domain.entities.person import Person
from domain.entities.base import GenealogyBase
from domain.entities.family import Family

class BaseRepository(ABC):
    """Repository pour les bases - 20 lignes max"""

    @abstractmethod
    def load_base(self, base_name: str) -> Optional[GenealogyBase]:
        pass

    @abstractmethod
    def get_person_by_id(self, base_name: str, person_id: int) -> Optional[Person]:
        pass

    @abstractmethod
    def search_persons(self, base_name: str, query: str) -> List[Person]:
        pass

class MessagePackBaseRepository(BaseRepository):
    """Repository MessagePack - 20 lignes max"""

    def __init__(self, bases_dir: str):
        self.bases_dir = bases_dir
        self._cache: Dict[str, GenealogyBase] = {}
        self.reader = MessagePackReader(bases_dir.rstrip('/'))

    def load_base(self, base_name: str, force_reload: bool = False) -> Optional[GenealogyBase]:
        if force_reload and base_name in self._cache:
            del self._cache[base_name]
        elif base_name in self._cache and not force_reload:
            return self._cache[base_name]

        base = self._load_from_disk(base_name)
        if base:
            self._cache[base_name] = base
        return base

    def list_bases(self) -> List[str]:
        """Liste toutes les bases disponibles"""
        import os
        bases = []
        if not os.path.exists(self.bases_dir):
            return bases
        for item in os.listdir(self.bases_dir):
            if item.endswith('.msgpack') and os.path.isdir(os.path.join(self.bases_dir, item)):
                bases.append(item.replace('.msgpack', ''))
        return sorted(bases)

    def _load_from_disk(self, base_name: str) -> Optional[GenealogyBase]:
        """Charge la base depuis le disque"""
        try:
            base_data = self.reader.load_database(base_name)
            if not base_data:
                return None

            # Convertir les personnes
            persons = {}
            for iper, gen_person in base_data.persons.items():
                persons[int(iper)] = self._convert_person(gen_person, int(iper))

            # Convertir les familles (utiliser couples et descends)
            families = {}
            for ifam, gen_family in base_data.families.items():
                # Obtenir le couple (père/mère) depuis couples
                couple = base_data.couples.get(ifam)
                husband_id = int(couple.father) if couple and couple.father else None
                wife_id = int(couple.mother) if couple and couple.mother else None

                # Obtenir les enfants depuis descends
                descend = base_data.descends.get(ifam)
                children_ids = []
                if descend and descend.children:
                    children_ids = [int(child) for child in descend.children]

                families[int(ifam)] = self._convert_family(
                    gen_family, int(ifam), husband_id, wife_id, children_ids
                )

            return GenealogyBase(
                name=base_name,
                path=f"{self.bases_dir}/{base_name}.msgpack",
                persons=persons,
                families=families,
                last_modified="2024-01-01"
            )
        except Exception as e:
            import traceback
            print(f"Error loading base {base_name}: {e}")
            traceback.print_exc()
            return None

    def _convert_person(self, gen_person: GenPerson, person_id: int) -> Person:
        """Convertit GenPerson en Person"""
        # Extraire date de naissance
        birth_date = None
        birth_place = None
        if gen_person.birth:
            birth_date = self._convert_date(gen_person.birth)

        # Chercher place de naissance dans les événements
        for event in gen_person.events or []:
            if event.name.upper() in ["BIRT", "BIRTH"]:
                birth_place = event.place or ""
                if not birth_date and event.date:
                    birth_date = self._convert_date(event.date)
                break

        # Extraire date de décès
        death_date = None
        death_place = None
        if gen_person.death:
            death_date = self._convert_date(gen_person.death)

        # Chercher place de décès dans les événements
        for event in gen_person.events or []:
            if event.name.upper() in ["DEAT", "DEATH"]:
                death_place = event.place or ""
                if not death_date and event.date:
                    death_date = self._convert_date(event.date)
                break

        # Extraire les sources
        sources = []
        if gen_person.sources:
            sources = [s.strip() for s in gen_person.sources.split(",") if s.strip()]

        return Person(
            id=person_id,
            first_name=gen_person.first_name or "",
            surname=gen_person.surname or "",
            occ=gen_person.occ or 0,
            birth=birth_date,
            death=death_date,
            birth_place=birth_place,
            death_place=death_place,
            notes=gen_person.notes or "",
            sources=sources
        )

    def _convert_family(
        self, gen_family: GenFamily, family_id: int,
        husband_id: Optional[int], wife_id: Optional[int], children_ids: List[int]
    ) -> Family:
        """Convertit GenFamily en Family"""
        # Extraire date et lieu de mariage
        marriage_date = None
        marriage_place = None
        if gen_family.marriage:
            marriage_date = self._convert_date(gen_family.marriage)
        if gen_family.marriage_place:
            marriage_place = gen_family.marriage_place

        # Chercher aussi dans les événements
        for event in gen_family.events or []:
            if event.name.upper() in ["MARR", "MARRIAGE"]:
                if not marriage_date and event.date:
                    marriage_date = self._convert_date(event.date)
                if not marriage_place and event.place:
                    marriage_place = event.place
                break

        # Extraire date et lieu de divorce
        divorce_date = None
        divorce_place = None
        if gen_family.divorce_date:
            divorce_date = self._convert_date(gen_family.divorce_date)
        if gen_family.divorce_place:
            divorce_place = gen_family.divorce_place

        # Chercher aussi dans les événements
        for event in gen_family.events or []:
            if event.name.upper() in ["DIV", "DIVORCE"]:
                if not divorce_date and event.date:
                    divorce_date = self._convert_date(event.date)
                if not divorce_place and event.place:
                    divorce_place = event.place
                break

        sources = []
        if gen_family.sources:
            sources = [s.strip() for s in gen_family.sources.split(",") if s.strip()]

        return Family(
            id=family_id,
            husband_id=husband_id,
            wife_id=wife_id,
            children_ids=children_ids,
            marriage_date=marriage_date,
            marriage_place=marriage_place,
            divorce_date=divorce_date,
            divorce_place=divorce_place,
            notes=gen_family.notes or "",
            sources=sources
        )

    def _convert_date(self, gen_date: GenDate) -> Optional[date]:
        """Convertit GenDate en date"""
        if not gen_date or not gen_date.year:
            return None
        try:
            return date(
                year=gen_date.year,
                month=gen_date.month or 1,
                day=gen_date.day or 1
            )
        except (ValueError, AttributeError):
            return None

    def get_person_by_id(self, base_name: str, person_id: int) -> Optional[Person]:
        base = self.load_base(base_name)
        return base.persons.get(person_id) if base else None

    def search_persons(self, base_name: str, query: str) -> List[Person]:
        base = self.load_base(base_name)
        if not base:
            return []

        query_lower = query.lower()
        return [
            person for person in base.persons.values()
            if query_lower in person.first_name.lower() or query_lower in person.surname.lower()
        ]
