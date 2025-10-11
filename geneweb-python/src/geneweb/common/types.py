"""Types et énumérations communs pour GeneWeb."""

from enum import Enum
from typing import TypeAlias


# Types de base
PersonId: TypeAlias = str
FamilyId: TypeAlias = str


class Sex(str, Enum):
    """Sexe d'une personne."""
    
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class AccessLevel(str, Enum):
    """Niveau d'accès aux informations."""
    
    PUBLIC = "public"
    PRIVATE = "private"
    FRIEND = "friend"


class DatePrecision(str, Enum):
    """Précision d'une date."""
    
    SURE = "sure"  # Date exacte
    ABOUT = "about"  # Vers (circa ~)
    MAYBE = "maybe"  # Peut-être ?
    BEFORE = "before"  # Avant <
    AFTER = "after"  # Après >
    OR_YEAR = "or_year"  # Ou année (|)
    YEAR_INTERVAL = "year_interval"  # Intervalle (..)


class Calendar(str, Enum):
    """Type de calendrier."""
    
    GREGORIAN = "gregorian"
    JULIAN = "julian"
    FRENCH = "french"
    HEBREW = "hebrew"


class EventType(str, Enum):
    """Type d'événement."""
    
    # Événements de personne
    BIRTH = "birth"
    BAPTISM = "baptism"
    DEATH = "death"
    BURIAL = "burial"
    CREMATION = "cremation"
    
    # Événements de famille
    MARRIAGE = "marriage"
    MARRIAGE_BANN = "marriage_bann"
    MARRIAGE_CONTRACT = "marriage_contract"
    MARRIAGE_LICENSE = "marriage_license"
    ENGAGEMENT = "engagement"
    DIVORCE = "divorce"
    SEPARATED = "separated"
    ANNULMENT = "annulment"
    
    # Autres événements
    OCCUPATION = "occupation"
    RESIDENCE = "residence"
    PROPERTY = "property"
    CENSUS = "census"
    TITLE = "title"
    GRADUATION = "graduation"
    MILITARY_SERVICE = "military_service"
    RELIGION = "religion"
    CUSTOM_EVENT = "custom_event"


class Charset(str, Enum):
    """Encodage de caractères."""
    
    UTF8 = "UTF-8"
    ASCII = "ASCII"
    ANSEL = "ANSEL"
    ANSI = "ANSI"


class RelationType(str, Enum):
    """Type de relation."""
    
    PARENT = "parent"
    CHILD = "child"
    SPOUSE = "spouse"
    SIBLING = "sibling"
    WITNESS = "witness"
    GODPARENT = "godparent"
