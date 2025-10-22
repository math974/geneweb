"""Entité Family pour GeneWeb."""

from dataclasses import dataclass, field
from typing import Optional, List

from geneweb.common.types import FamilyId, PersonId
from geneweb.gwu.domain.entities.event import Event, Witness
from geneweb.gwu.domain.entities.note import Note, Source


@dataclass
class Family:
    """
    Représente une famille (union de deux personnes).
    
    Une famille relie un père, une mère et leurs enfants.
    Contient les événements de l'union (mariage, divorce) et métadonnées.
    
    Examples:
        # Famille simple
        Family(
            family_id="F1",
            father_id="P1",
            mother_id="P2"
        )
        
        # Famille avec mariage et enfants
        Family(
            family_id="F2",
            father_id="P3",
            mother_id="P4",
            marriage=Event(
                event_type=EventType.MARRIAGE,
                date=Date.from_year(1850)
            ),
            children=["P5", "P6", "P7"]
        )
    """
    
    # Identité
    family_id: FamilyId
    father_id: PersonId
    mother_id: PersonId
    
    # Événements d'union
    marriage: Optional[Event] = None
    marriage_bann: Optional[Event] = None
    marriage_contract: Optional[Event] = None
    marriage_license: Optional[Event] = None
    engagement: Optional[Event] = None
    
    # Événements de séparation
    divorce: Optional[Event] = None
    separated: Optional[Event] = None
    annulment: Optional[Event] = None
    
    # Enfants (ordre important)
    children: List[PersonId] = field(default_factory=list)
    
    # Autres événements
    events: List[Event] = field(default_factory=list)
    
    # Métadonnées
    notes: Optional[Note] = None
    sources: List[Source] = field(default_factory=list)
    witnesses: List[Witness] = field(default_factory=list)
    
    def __post_init__(self):
        """Validation post-initialisation."""
        if not self.family_id or not self.family_id.strip():
            raise ValueError("L'ID de la famille ne peut pas être vide")
        if not self.father_id or not self.father_id.strip():
            raise ValueError("L'ID du père ne peut pas être vide")
        if not self.mother_id or not self.mother_id.strip():
            raise ValueError("L'ID de la mère ne peut pas être vide")
    
    def has_marriage(self) -> bool:
        """Vérifie si la famille a un événement de mariage."""
        return self.marriage is not None
    
    def has_divorce(self) -> bool:
        """Vérifie si la famille a un événement de divorce."""
        return self.divorce is not None
    
    def has_children(self) -> bool:
        """Vérifie si la famille a des enfants."""
        return len(self.children) > 0
    
    def children_count(self) -> int:
        """Retourne le nombre d'enfants."""
        return len(self.children)
    
    def has_notes(self) -> bool:
        """Vérifie si la famille a des notes."""
        return self.notes is not None and bool(self.notes)
    
    def has_sources(self) -> bool:
        """Vérifie si la famille a des sources."""
        return len(self.sources) > 0
    
    def has_witnesses(self) -> bool:
        """Vérifie si la famille a des témoins."""
        return len(self.witnesses) > 0
    
    def has_events(self) -> bool:
        """Vérifie si la famille a des événements additionnels."""
        return len(self.events) > 0 or self.marriage is not None
    
    def is_married(self) -> bool:
        """
        Vérifie si le couple est marié (a un mariage et pas de divorce).
        
        Returns:
            True si mariage sans divorce
        """
        return self.has_marriage() and not self.has_divorce()
    
    def is_divorced(self) -> bool:
        """
        Vérifie si le couple est divorcé.
        
        Returns:
            True si divorce
        """
        return self.has_divorce()
    
    def get_parents(self) -> tuple[PersonId, PersonId]:
        """
        Retourne le tuple (père, mère).
        
        Returns:
            Tuple (father_id, mother_id)
        """
        return (self.father_id, self.mother_id)
    
    def add_child(self, child_id: PersonId) -> None:
        """
        Ajoute un enfant à la famille.
        
        Args:
            child_id: ID de l'enfant à ajouter
        """
        if child_id not in self.children:
            self.children.append(child_id)
    
    def remove_child(self, child_id: PersonId) -> bool:
        """
        Retire un enfant de la famille.
        
        Args:
            child_id: ID de l'enfant à retirer
        
        Returns:
            True si l'enfant a été retiré, False si non trouvé
        """
        if child_id in self.children:
            self.children.remove(child_id)
            return True
        return False
    
    def __str__(self) -> str:
        """Représentation string de la famille."""
        return f"Family({self.father_id} + {self.mother_id}, {self.children_count()} enfants)"
    
    def __repr__(self) -> str:
        """Représentation détaillée."""
        return (
            f"Family(id={self.family_id}, father={self.father_id}, "
            f"mother={self.mother_id}, children={self.children_count()})"
        )
