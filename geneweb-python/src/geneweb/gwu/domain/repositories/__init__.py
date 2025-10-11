"""Repositories (Ports) du domaine GWU."""

from geneweb.gwu.domain.repositories.person_repository import PersonRepository
from geneweb.gwu.domain.repositories.family_repository import FamilyRepository

__all__ = [
    "PersonRepository",
    "FamilyRepository",
]
