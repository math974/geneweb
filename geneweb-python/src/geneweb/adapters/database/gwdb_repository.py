"""GeneWeb database repository implementation."""

from pathlib import Path
from typing import Optional

from geneweb.domain.entities.person import Person, Sex
from geneweb.domain.entities.family import Family
from geneweb.adapters.database.gwu_parser import GwuCache


class GwdbPersonRepository:
    """Person repository for GeneWeb database."""
    
    def __init__(self, base_dir: Path, base_name: str, gwu_cache: GwuCache):
        """Initialize repository."""
        self.base_dir = base_dir
        self.base_name = base_name
        self.base_path = base_dir / f"{base_name}.gwb"
        self.gwu_cache = gwu_cache
        self._persons: Optional[list[Person]] = None
        self._families: Optional[list[Family]] = None
    
    def _load_data(self) -> None:
        """Load data from gwu if not already loaded."""
        if self._persons is None:
            self._persons, self._families = self.gwu_cache.get_data(self.base_dir, self.base_name)
    
    def get_by_id(self, person_id: int) -> Optional[Person]:
        """Get person by ID."""
        self._load_data()
        for person in self._persons or []:
            if person.id == person_id:
                return person
        return None
    
    def get_all(self) -> list[Person]:
        """Get all persons."""
        self._load_data()
        return self._persons or []
    
    def count(self) -> int:
        """Count persons in base."""
        self._load_data()
        return len(self._persons) if self._persons else 0
    
    def search(self, name: str) -> list[Person]:
        """Search persons by name."""
        self._load_data()
        results = []
        name_lower = name.lower()
        for person in self._persons or []:
            if (name_lower in person.first_name.lower() or 
                name_lower in person.surname.lower()):
                results.append(person)
        return results


class GwdbFamilyRepository:
    """Family repository for GeneWeb database."""
    
    def __init__(self, base_dir: Path, base_name: str, gwu_cache: GwuCache):
        """Initialize repository."""
        self.base_dir = base_dir
        self.base_name = base_name
        self.base_path = base_dir / f"{base_name}.gwb"
        self.gwu_cache = gwu_cache
        self._persons: Optional[list[Person]] = None
        self._families: Optional[list[Family]] = None
    
    def _load_data(self) -> None:
        """Load data from gwu if not already loaded."""
        if self._families is None:
            self._persons, self._families = self.gwu_cache.get_data(self.base_dir, self.base_name)
    
    def get_by_id(self, family_id: int) -> Optional[Family]:
        """Get family by ID."""
        self._load_data()
        for family in self._families or []:
            if family.id == family_id:
                return family
        return None
    
    def get_all(self) -> list[Family]:
        """Get all families."""
        self._load_data()
        return self._families or []
    
    def count(self) -> int:
        """Count families in base."""
        self._load_data()
        return len(self._families) if self._families else 0


class GwdbBaseRepository:
    """Base repository for GeneWeb databases."""
    
    def __init__(self, base_dir: Path, gwu_path: Optional[Path] = None):
        """Initialize repository."""
        self.base_dir = base_dir
        # Default gwu path
        if gwu_path is None:
            gwu_path = base_dir.parent / "gw" / "gwu"
        self.gwu_cache = GwuCache(gwu_path)
    
    def exists(self, base_name: str) -> bool:
        """Check if base exists."""
        base_path = self.base_dir / f"{base_name}.gwb"
        return base_path.exists() and base_path.is_dir()
    
    def get_person_repository(self, base_name: str) -> GwdbPersonRepository:
        """Get person repository for a base."""
        return GwdbPersonRepository(self.base_dir, base_name, self.gwu_cache)
    
    def get_family_repository(self, base_name: str) -> GwdbFamilyRepository:
        """Get family repository for a base."""
        return GwdbFamilyRepository(self.base_dir, base_name, self.gwu_cache)
