"""Entité Famille - 20 lignes max par fonction"""
from dataclasses import dataclass
from typing import Optional, List
from datetime import date

@dataclass
class Family:
    """Entité Famille - 20 lignes max"""
    id: int
    husband_id: Optional[int] = None
    wife_id: Optional[int] = None
    children_ids: List[int] = None
    marriage_date: Optional[date] = None
    marriage_place: Optional[str] = None
    divorce_date: Optional[date] = None
    divorce_place: Optional[str] = None
    notes: str = ""
    sources: List[str] = None
    
    def __post_init__(self):
        if self.children_ids is None:
            self.children_ids = []
        if self.sources is None:
            self.sources = []
    
    @property
    def is_married(self) -> bool:
        """Vérifie si le couple est marié"""
        return self.marriage_date is not None
    
    @property
    def is_divorced(self) -> bool:
        """Vérifie si le couple est divorcé"""
        return self.divorce_date is not None
    
    def add_child(self, child_id: int) -> None:
        """Ajouter un enfant - MAX 20 LIGNES"""
        if child_id not in self.children_ids:
            self.children_ids.append(child_id)
    
    def get_children_count(self) -> int:
        """Nombre d'enfants - MAX 20 LIGNES"""
        return len(self.children_ids)
    
    def is_complete(self) -> bool:
        """Famille complète (père + mère) - MAX 20 LIGNES"""
        return self.husband_id is not None and self.wife_id is not None