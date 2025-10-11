"""Entité Place pour GeneWeb."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Place:
    """
    Représente un lieu géographique.
    
    Peut être simple (nom) ou avec coordonnées géographiques.
    
    Examples:
        Place(name="Paris, France")
        Place(name="New York", coordinates="40.7128,-74.0060")
    """
    
    name: str
    coordinates: Optional[str] = None
    
    def __post_init__(self):
        """Validation post-initialisation."""
        if not self.name or not self.name.strip():
            raise ValueError("Le nom du lieu ne peut pas être vide")
    
    def to_gw_format(self) -> str:
        """
        Convertit le lieu en format .gw.
        
        Returns:
            String au format .gw
        
        Examples:
            Place(name="Paris") -> "Paris"
            Place(name="Paris, France") -> "Paris, France"
        """
        return self.name.strip()
    
    def has_coordinates(self) -> bool:
        """Vérifie si le lieu a des coordonnées."""
        return self.coordinates is not None and len(self.coordinates.strip()) > 0
    
    def __str__(self) -> str:
        """Représentation string (nom du lieu)."""
        return self.name
    
    @classmethod
    def from_string(cls, place_string: str) -> "Place":
        """
        Crée un lieu à partir d'une chaîne.
        
        Args:
            place_string: Nom du lieu
        
        Returns:
            Instance de Place
        """
        return cls(name=place_string.strip())
