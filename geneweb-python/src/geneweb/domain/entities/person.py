"""Person entity for GeneWeb."""

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional


class Sex(Enum):
    """Sex of a person."""
    MALE = 0
    FEMALE = 1
    UNKNOWN = 2


@dataclass
class Person:
    """Person entity matching GeneWeb person structure."""
    
    # Identification
    id: int
    first_name: str
    surname: str
    
    # Optional names
    public_name: Optional[str] = None
    qualifiers: list[str] | None = None
    aliases: list[str] | None = None
    first_names_aliases: list[str] | None = None
    surnames_aliases: list[str] | None = None
    
    # Personal info
    sex: Sex = Sex.UNKNOWN
    occupation: Optional[str] = None
    image: Optional[str] = None
    
    # Birth
    birth_date: Optional[date] = None
    birth_place: Optional[str] = None
    birth_src: Optional[str] = None
    
    # Baptism
    baptism_date: Optional[date] = None
    baptism_place: Optional[str] = None
    baptism_src: Optional[str] = None
    
    # Death
    death_date: Optional[date] = None
    death_place: Optional[str] = None
    death_src: Optional[str] = None
    death_type: str = "NotDead"  # NotDead, Dead, DeadYoung, DeadDontKnowWhen, etc.
    
    # Burial
    burial_date: Optional[date] = None
    burial_place: Optional[str] = None
    burial_src: Optional[str] = None
    
    # Relations
    parents_family_id: Optional[int] = None  # ascendants
    families_ids: list[int] | None = None    # unions (as parent)
    
    # Notes
    notes: Optional[str] = None
    psources: Optional[str] = None
    
    @property
    def full_name(self) -> str:
        """Get full name."""
        return f"{self.first_name} {self.surname}"
    
    @property
    def display_name(self) -> str:
        """Get display name (with public name if available)."""
        if self.public_name:
            return f"{self.first_name} {self.public_name} {self.surname}"
        return self.full_name
