"""Value Object Place - 20 lignes max par fonction"""
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Place:
    """Value object pour un lieu - 20 lignes max"""
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    
    @property
    def full_place(self) -> str:
        """Lieu complet - MAX 20 LIGNES"""
        parts = [p for p in [self.city, self.region, self.country] if p]
        return ", ".join(parts) if parts else ""
    
    @property
    def short_place(self) -> str:
        """Lieu court (ville) - MAX 20 LIGNES"""
        return self.city or ""
    
    def __str__(self) -> str:
        """Représentation string - MAX 20 LIGNES"""
        return self.full_place or "Unknown"

