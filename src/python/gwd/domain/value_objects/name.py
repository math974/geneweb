"""Value Object Name - 20 lignes max par fonction"""
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Name:
    """Value object pour un nom - 20 lignes max"""
    first_name: str
    surname: str
    public_name: Optional[str] = None
    
    @property
    def display_name(self) -> str:
        """Nom d'affichage - MAX 20 LIGNES"""
        if self.public_name:
            return f"{self.public_name} {self.surname}"
        return f"{self.first_name} {self.surname}"
    
    @property
    def full_name(self) -> str:
        """Nom complet - MAX 20 LIGNES"""
        return f"{self.first_name} {self.surname}"
    
    def __str__(self) -> str:
        """Représentation string - MAX 20 LIGNES"""
        return self.display_name

