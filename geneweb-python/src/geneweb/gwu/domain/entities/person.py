"""Entité Person pour GeneWeb."""

from dataclasses import dataclass, field
from typing import Optional, List

from geneweb.common.types import Sex, AccessLevel, PersonId, FamilyId
from geneweb.gwu.domain.entities.event import Event
from geneweb.gwu.domain.entities.note import Note, Source, Title


@dataclass
class Person:
    """
    Représente une personne dans la base généalogique.
    
    Entité centrale du domaine généalogique, contient toutes les informations
    sur une personne : identité, événements, relations familiales, métadonnées.
    
    Examples:
        # Personne simple
        Person(
            person_id="1",
            first_name="Jean",
            surname="Dupont",
            sex=Sex.MALE
        )
        
        # Personne avec événements
        Person(
            person_id="2",
            first_name="Marie",
            surname="Martin",
            occ=0,
            sex=Sex.FEMALE,
            birth=Event(
                event_type=EventType.BIRTH,
                date=Date.from_year(1850)
            )
        )
    """
    
    # Identité (requis)
    person_id: PersonId
    first_name: str
    surname: str
    sex: Sex
    occ: int = 0
    
    # Accès et vie privée
    public: bool = True
    access: AccessLevel = AccessLevel.PUBLIC
    
    # Événements principaux
    birth: Optional[Event] = None
    baptism: Optional[Event] = None
    death: Optional[Event] = None
    burial: Optional[Event] = None
    cremation: Optional[Event] = None
    
    # Relations familiales
    parents: Optional[FamilyId] = None  # Famille des parents
    spouses: List[FamilyId] = field(default_factory=list)  # Familles où cette personne est parent
    
    # Autres événements
    events: List[Event] = field(default_factory=list)
    
    # Métadonnées
    notes: Optional[Note] = None
    sources: List[Source] = field(default_factory=list)
    occupation: Optional[str] = None
    titles: List[Title] = field(default_factory=list)
    
    # Image
    image: Optional[str] = None
    
    # Relations et liens
    related_persons: List[PersonId] = field(default_factory=list)
    
    def __post_init__(self):
        """Validation post-initialisation."""
        if not self.first_name or not self.first_name.strip():
            raise ValueError("Le prénom ne peut pas être vide")
        if not self.surname or not self.surname.strip():
            raise ValueError("Le nom de famille ne peut pas être vide")
        if self.occ < 0:
            raise ValueError("L'occurrence ne peut pas être négative")
    
    def format_name(self) -> str:
        """
        Formate le nom complet (Prénom.occ NOM).
        
        Returns:
            String au format "Prénom.occ NOM"
        
        Examples:
            Person(first_name="Jean", surname="Dupont", occ=0) -> "Jean.0 Dupont"
            Person(first_name="Jean", surname="Dupont", occ=1) -> "Jean.1 Dupont"
        """
        return f"{self.first_name}.{self.occ} {self.surname}"
    
    def format_key(self) -> str:
        """
        Formate la clé unique (Prénom.occ NOM) - alias de format_name().
        
        Returns:
            String au format "Prénom.occ NOM"
        """
        return self.format_name()
    
    def has_birth(self) -> bool:
        """Vérifie si la personne a une date/lieu de naissance."""
        return self.birth is not None
    
    def has_death(self) -> bool:
        """Vérifie si la personne a une date/lieu de décès."""
        return self.death is not None
    
    def has_parents(self) -> bool:
        """Vérifie si la personne a des parents connus."""
        return self.parents is not None
    
    def has_spouses(self) -> bool:
        """Vérifie si la personne a des conjoints."""
        return len(self.spouses) > 0
    
    def is_isolated(self) -> bool:
        """
        Vérifie si la personne est isolée (sans parents ni conjoints).
        
        Returns:
            True si la personne n'a ni parents ni conjoints
        """
        return not self.has_parents() and not self.has_spouses()
    
    def has_notes(self) -> bool:
        """Vérifie si la personne a des notes."""
        return self.notes is not None and bool(self.notes)
    
    def has_sources(self) -> bool:
        """Vérifie si la personne a des sources."""
        return len(self.sources) > 0
    
    def has_occupation(self) -> bool:
        """Vérifie si la personne a une profession."""
        return self.occupation is not None and len(self.occupation.strip()) > 0
    
    def has_titles(self) -> bool:
        """Vérifie si la personne a des titres."""
        return len(self.titles) > 0
    
    def has_image(self) -> bool:
        """Vérifie si la personne a une image."""
        return self.image is not None and len(self.image.strip()) > 0
    
    def has_events(self) -> bool:
        """Vérifie si la personne a des événements additionnels."""
        return len(self.events) > 0
    
    def is_public(self) -> bool:
        """Vérifie si la personne est publique."""
        return self.public and self.access == AccessLevel.PUBLIC
    
    def is_male(self) -> bool:
        """Vérifie si la personne est de sexe masculin."""
        return self.sex == Sex.MALE
    
    def is_female(self) -> bool:
        """Vérifie si la personne est de sexe féminin."""
        return self.sex == Sex.FEMALE
    
    def __str__(self) -> str:
        """Représentation string (nom formaté)."""
        return self.format_name()
    
    def __repr__(self) -> str:
        """Représentation détaillée."""
        return (
            f"Person(id={self.person_id}, name={self.format_name()}, "
            f"sex={self.sex.value})"
        )
