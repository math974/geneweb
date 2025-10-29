"""Family entity for GeneWeb."""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Family:
    """Family entity matching GeneWeb family structure."""
    
    # Identification
    id: int
    
    # Parents
    father_id: int
    mother_id: int
    
    # Children
    children_ids: list[int] | None = None
    
    # Marriage
    marriage_date: Optional[date] = None
    marriage_place: Optional[str] = None
    marriage_src: Optional[str] = None
    marriage_type: str = "Married"  # Married, NotMarried, Engaged, NoSexesCheckNotMarried, etc.
    
    # Divorce
    divorce_date: Optional[date] = None
    divorce_type: str = "NotDivorced"  # NotDivorced, Divorced, Separated
    
    # Notes
    notes: Optional[str] = None
    fsources: Optional[str] = None
    
    # Witnesses
    witnesses: list[int] | None = None
