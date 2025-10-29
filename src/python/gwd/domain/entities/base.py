"""Entité Base généalogique - 20 lignes max par fonction"""
from dataclasses import dataclass
from typing import Dict, List
from pathlib import Path
from .person import Person
from .family import Family

@dataclass
class GenealogyBase:
    """Base généalogique - 20 lignes max"""
    name: str
    path: str
    persons: Dict[int, Person]
    families: Dict[int, Family]
    last_modified: str
    version: str = "1.0"
    
    @property
    def persons_count(self) -> int:
        """Nombre de personnes"""
        return len(self.persons)
    
    @property
    def families_count(self) -> int:
        """Nombre de familles"""
        return len(self.families)
    
    def get_person(self, person_id: int) -> Person:
        """Récupère une personne par ID"""
        return self.persons.get(person_id)
    
    def get_family(self, family_id: int) -> Family:
        """Récupère une famille par ID"""
        return self.families.get(family_id)
