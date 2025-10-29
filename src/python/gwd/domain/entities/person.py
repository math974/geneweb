"""Entité Personne - 20 lignes max par fonction"""
from dataclasses import dataclass
from typing import Optional, List
from datetime import date

@dataclass
class Person:
    """Entité Personne - 20 lignes max"""
    id: int
    first_name: str
    surname: str
    public_name: Optional[str] = None
    occ: int = 0
    birth: Optional[date] = None
    death: Optional[date] = None
    birth_place: Optional[str] = None
    death_place: Optional[str] = None
    notes: str = ""
    sources: List[str] = None
    
    def __post_init__(self):
        if self.sources is None:
            self.sources = []
    
    @property
    def display_name(self) -> str:
        """Nom d'affichage de la personne"""
        if self.public_name:
            return f"{self.public_name} {self.surname}"
        return f"{self.first_name} {self.surname}"
    
    @property
    def age_at_death(self) -> Optional[int]:
        """Âge au décès si décédé"""
        if self.birth and self.death:
            return self.death.year - self.birth.year
        return None
