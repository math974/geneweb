"""Repository Pattern pour les Bases - 20 lignes max"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from domain.entities.person import Person
from domain.entities.base import GenealogyBase

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
    
    def load_base(self, base_name: str) -> Optional[GenealogyBase]:
        if base_name in self._cache:
            return self._cache[base_name]
        
        base = self._load_from_disk(base_name)
        if base:
            self._cache[base_name] = base
        return base
    
    def _load_from_disk(self, base_name: str) -> Optional[GenealogyBase]:
        # Implémentation simplifiée
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
