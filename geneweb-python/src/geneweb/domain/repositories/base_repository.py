"""Repository protocols for GeneWeb."""

from typing import Protocol, Optional

from geneweb.domain.entities.person import Person
from geneweb.domain.entities.family import Family


class PersonRepository(Protocol):
    """Protocol for person repository."""
    
    def get_by_id(self, person_id: int) -> Optional[Person]:
        """Get person by ID."""
        ...
    
    def get_all(self) -> list[Person]:
        """Get all persons."""
        ...
    
    def count(self) -> int:
        """Count persons in base."""
        ...
    
    def search(self, name: str) -> list[Person]:
        """Search persons by name."""
        ...


class FamilyRepository(Protocol):
    """Protocol for family repository."""
    
    def get_by_id(self, family_id: int) -> Optional[Family]:
        """Get family by ID."""
        ...
    
    def get_all(self) -> list[Family]:
        """Get all families."""
        ...
    
    def count(self) -> int:
        """Count families in base."""
        ...


class BaseRepository(Protocol):
    """Protocol for base-level operations."""
    
    def exists(self, base_name: str) -> bool:
        """Check if base exists."""
        ...
    
    def get_person_repository(self, base_name: str) -> PersonRepository:
        """Get person repository for a base."""
        ...
    
    def get_family_repository(self, base_name: str) -> FamilyRepository:
        """Get family repository for a base."""
        ...
