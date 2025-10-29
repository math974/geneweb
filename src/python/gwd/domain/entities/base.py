"""Entité Base généalogique - 20 lignes max par fonction"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import date
from .person import Person
from .family import Family

@dataclass
class GenealogyBase:
    """Base généalogique - 20 lignes max"""
    name: str
    persons: Dict[int, Person] = field(default_factory=dict)
    families: Dict[int, Family] = field(default_factory=dict)
    title: str = ""
    wizard_password: str = ""
    friend_password: str = ""
    version: str = "1.0"
    
    @property
    def persons_count(self) -> int:
        """Nombre de personnes"""
        return len(self.persons)
    
    @property
    def families_count(self) -> int:
        """Nombre de familles"""
        return len(self.families)
    
    def get_person(self, person_id: int) -> Optional[Person]:
        """Obtenir une personne - MAX 20 LIGNES"""
        return self.persons.get(person_id)
    
    def add_person(self, person: Person) -> None:
        """Ajouter une personne - MAX 20 LIGNES"""
        self.persons[person.id] = person
    
    def get_family(self, family_id: int) -> Optional[Family]:
        """Obtenir une famille - MAX 20 LIGNES"""
        return self.families.get(family_id)
    
    def add_family(self, family: Family) -> None:
        """Ajouter une famille - MAX 20 LIGNES"""
        self.families[family.id] = family
    
    def search_persons(self, query: str) -> List[Person]:
        """Rechercher des personnes - MAX 20 LIGNES"""
        query_lower = query.lower()
        return [
            p for p in self.persons.values()
            if query_lower in p.first_name.lower()
            or query_lower in p.surname.lower()
        ]
