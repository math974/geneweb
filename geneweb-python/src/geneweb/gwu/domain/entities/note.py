"""Entité Note pour GeneWeb."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Note:
    """
    Représente une note (texte libre).
    
    Peut contenir du texte simple ou du wiki markup.
    """
    
    content: str
    
    def __post_init__(self):
        """Validation post-initialisation."""
        if self.content is None:
            self.content = ""
    
    def is_empty(self) -> bool:
        """Vérifie si la note est vide."""
        return len(self.content.strip()) == 0
    
    def __str__(self) -> str:
        """Représentation string de la note."""
        return self.content
    
    def __bool__(self) -> bool:
        """Vérifie si la note contient du texte."""
        return not self.is_empty()


@dataclass
class Source:
    """
    Représente une source (référence documentaire).
    
    Examples:
        Source(reference="Registre paroissial de Paris, 1789")
        Source(reference="Acte de naissance n°123")
    """
    
    reference: str
    
    def __post_init__(self):
        """Validation post-initialisation."""
        if self.reference is None:
            self.reference = ""
    
    def is_empty(self) -> bool:
        """Vérifie si la source est vide."""
        return len(self.reference.strip()) == 0
    
    def __str__(self) -> str:
        """Représentation string de la source."""
        return self.reference
    
    def __bool__(self) -> bool:
        """Vérifie si la source contient une référence."""
        return not self.is_empty()


@dataclass
class Title:
    """
    Représente un titre (noblesse, fonction).
    
    Examples:
        Title(name="Duc de Normandie")
        Title(name="Maire", place="Paris")
    """
    
    name: str
    place: Optional[str] = None
    date_start: Optional[str] = None
    date_end: Optional[str] = None
    
    def __post_init__(self):
        """Validation post-initialisation."""
        if not self.name or not self.name.strip():
            raise ValueError("Le nom du titre ne peut pas être vide")
    
    def __str__(self) -> str:
        """Représentation string du titre."""
        parts = [self.name]
        if self.place:
            parts.append(f"de {self.place}")
        return " ".join(parts)
