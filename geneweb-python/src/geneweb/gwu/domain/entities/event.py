"""Entité Event pour GeneWeb."""

from dataclasses import dataclass, field
from typing import Optional, List

from geneweb.common.types import EventType, PersonId
from geneweb.gwu.domain.entities.date import Date
from geneweb.gwu.domain.entities.place import Place


@dataclass
class Witness:
    """Représente un témoin d'événement."""
    
    person_id: PersonId
    witness_kind: str = "witness"  # witness, witness_godparent, witness_officer, etc.


@dataclass
class Event:
    """
    Représente un événement généalogique.
    
    Supporte tous les types d'événements (naissance, mariage, décès, etc.)
    avec date, lieu, notes, sources et témoins.
    
    Examples:
        # Naissance
        Event(
            event_type=EventType.BIRTH,
            date=Date.from_full_date(15, 8, 1789),
            place=Place(name="Paris")
        )
        
        # Mariage avec témoins
        Event(
            event_type=EventType.MARRIAGE,
            date=Date.from_year(1815),
            witnesses=[Witness(person_id="123"), Witness(person_id="456")]
        )
    """
    
    event_type: EventType
    date: Optional[Date] = None
    place: Optional[Place] = None
    note: Optional[str] = None
    source: Optional[str] = None
    witnesses: List[Witness] = field(default_factory=list)
    
    def has_date(self) -> bool:
        """Vérifie si l'événement a une date."""
        return self.date is not None
    
    def has_place(self) -> bool:
        """Vérifie si l'événement a un lieu."""
        return self.place is not None
    
    def has_witnesses(self) -> bool:
        """Vérifie si l'événement a des témoins."""
        return len(self.witnesses) > 0
    
    def has_note(self) -> bool:
        """Vérifie si l'événement a une note."""
        return self.note is not None and len(self.note.strip()) > 0
    
    def has_source(self) -> bool:
        """Vérifie si l'événement a une source."""
        return self.source is not None and len(self.source.strip()) > 0
    
    def is_birth_like(self) -> bool:
        """Vérifie si c'est un événement de naissance ou baptême."""
        return self.event_type in (EventType.BIRTH, EventType.BAPTISM)
    
    def is_death_like(self) -> bool:
        """Vérifie si c'est un événement de décès, inhumation ou crémation."""
        return self.event_type in (
            EventType.DEATH,
            EventType.BURIAL,
            EventType.CREMATION,
        )
    
    def is_marriage_like(self) -> bool:
        """Vérifie si c'est un événement de mariage."""
        return self.event_type in (
            EventType.MARRIAGE,
            EventType.MARRIAGE_BANN,
            EventType.MARRIAGE_CONTRACT,
            EventType.MARRIAGE_LICENSE,
            EventType.ENGAGEMENT,
        )
    
    def is_divorce_like(self) -> bool:
        """Vérifie si c'est un événement de séparation."""
        return self.event_type in (
            EventType.DIVORCE,
            EventType.SEPARATED,
            EventType.ANNULMENT,
        )
    
    def __str__(self) -> str:
        """Représentation string de l'événement."""
        parts = [self.event_type.value]
        if self.date:
            parts.append(str(self.date))
        if self.place:
            parts.append(str(self.place))
        return " ".join(parts)
