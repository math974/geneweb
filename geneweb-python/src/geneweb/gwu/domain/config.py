"""Configuration et options pour GWU."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Set
from enum import Enum

from geneweb.common.types import Charset


class OutputFormat(str, Enum):
    """Format de sortie."""
    
    GW = "gw"  # Format .gw (par défaut)
    GEDCOM = "gedcom"  # Format GEDCOM
    JSON = "json"  # Format JSON


@dataclass
class ExportOptions:
    """
    Options d'export pour GWU.
    
    Représente toutes les options disponibles dans gwu OCaml.
    """
    
    # Options de base
    output_file: Optional[Path] = None
    output_dir: Optional[Path] = None
    output_format: OutputFormat = OutputFormat.GW
    
    # Options de sélection
    keys: List[str] = None  # -k (clés de personnes)
    asc_depth: Optional[int] = None  # -a (profondeur ascendance)
    desc_depth: Optional[int] = None  # -d (profondeur descendance)
    asc_desc_depth: Optional[int] = None  # -ad (profondeur asc+desc)
    parentship: bool = False  # --parentship
    isolated: bool = False  # --isolated
    
    # Options de formatage
    charset: Charset = Charset.UTF8  # --charset
    gw_plus: bool = True  # gwplus (par défaut)
    old_gw: bool = False  # --old-gw (format < 7.00)
    no_notes: bool = False  # --no-notes
    no_sources: bool = False  # --no-sources
    no_witnesses: bool = False  # --no-witnesses
    
    # Options de séparation
    separate_persons: List[str] = None  # -sep (personnes à séparer)
    separate_families: bool = False  # Séparer les familles
    
    # Options de filtrage
    filter_public: bool = False  # --public-only
    filter_private: bool = False  # --private-only
    no_notes: bool = False  # --no-notes
    no_sources: bool = False  # --no-src
    no_events: bool = False  # --no-evt
    
    # Options de format
    gw_plus: bool = True  # --gwplus
    encoding: str = "UTF-8"  # -enc
    old_gw: bool = False  # --old-gw
    
    # Options de tri
    sort_by_name: bool = False  # --sort-by-name
    sort_by_date: bool = False  # --sort-by-date
    
    # Options de validation
    validate_dates: bool = True  # --validate-dates
    check_consistency: bool = True  # --check-consistency
    
    def __post_init__(self):
        """Validation post-initialisation."""
        if self.keys is None:
            self.keys = []
        if self.separate_persons is None:
            self.separate_persons = []
        
        # Validation des profondeurs
        if self.asc_depth is not None and self.asc_depth < 0:
            raise ValueError("asc_depth doit être >= 0")
        if self.desc_depth is not None and self.desc_depth < 0:
            raise ValueError("desc_depth doit être >= 0")
        if self.asc_desc_depth is not None and self.asc_desc_depth < 0:
            raise ValueError("asc_desc_depth doit être >= 0")
        
        # Validation des options mutuellement exclusives
        if self.filter_public and self.filter_private:
            raise ValueError("filter_public et filter_private sont mutuellement exclusifs")
        
        if self.sort_by_name and self.sort_by_date:
            raise ValueError("sort_by_name et sort_by_date sont mutuellement exclusifs")


@dataclass
class SelectionCriteria:
    """
    Critères de sélection des personnes.
    
    Utilisé par SelectionService pour filtrer les personnes.
    """
    
    # Sélection par clé
    keys: Set[str] = None
    
    # Sélection par profondeur
    asc_depth: Optional[int] = None
    desc_depth: Optional[int] = None
    asc_desc_depth: Optional[int] = None
    
    # Sélection par type
    parentship: bool = False
    isolated_only: bool = False
    
    # Filtres d'accès
    public_only: bool = False
    private_only: bool = False
    
    # Filtres de contenu
    with_events: bool = False
    with_notes: bool = False
    with_sources: bool = False
    
    def __post_init__(self):
        """Validation post-initialisation."""
        if self.keys is None:
            self.keys = set()
        
        # Validation des profondeurs
        if self.asc_depth is not None and self.asc_depth < 0:
            raise ValueError("asc_depth doit être >= 0")
        if self.desc_depth is not None and self.desc_depth < 0:
            raise ValueError("desc_depth doit être >= 0")
        if self.asc_desc_depth is not None and self.asc_desc_depth < 0:
            raise ValueError("asc_desc_depth doit être >= 0")
        
        # Validation des options mutuellement exclusives
        if self.public_only and self.private_only:
            raise ValueError("public_only et private_only sont mutuellement exclusifs")
    
    def is_empty(self) -> bool:
        """Vérifie si les critères sont vides (pas de sélection)."""
        return (
            not self.keys and
            self.asc_depth is None and
            self.desc_depth is None and
            self.asc_desc_depth is None and
            not self.parentship and
            not self.isolated_only and
            not self.public_only and
            not self.private_only and
            not self.with_events and
            not self.with_notes and
            not self.with_sources
        )


@dataclass
class ExportRequest:
    """
    Requête d'export.
    
    DTO pour passer les paramètres d'export aux use cases.
    """
    
    # Base de données
    database_path: Path
    
    # Options d'export
    options: ExportOptions
    
    # Critères de sélection
    selection: Optional[SelectionCriteria] = None
    
    # Options de sortie
    output_file: Optional[Path] = None
    output_dir: Optional[Path] = None
    
    # Options de validation
    validate: bool = True
    
    def __post_init__(self):
        """Validation post-initialisation."""
        if self.validate and not self.database_path.exists():
            raise ValueError(f"Base de données non trouvée: {self.database_path}")
        
        # Validation des options de sortie
        if self.output_file and self.output_dir:
            raise ValueError("output_file et output_dir sont mutuellement exclusifs")


@dataclass
class ExportResult:
    """
    Résultat d'export.
    
    DTO pour retourner les résultats des use cases.
    """
    
    # Statut
    success: bool
    error_message: Optional[str] = None
    
    # Statistiques
    exported_persons: int = 0
    exported_families: int = 0
    exported_events: int = 0
    
    # Fichiers générés
    output_files: List[Path] = None
    
    # Métadonnées
    processing_time: float = 0.0
    memory_used: int = 0  # en bytes
    
    def __post_init__(self):
        """Validation post-initialisation."""
        if self.output_files is None:
            self.output_files = []
        
        if not self.success and not self.error_message:
            raise ValueError("error_message requis si success=False")
    
    def add_output_file(self, file_path: Path) -> None:
        """Ajoute un fichier de sortie."""
        self.output_files.append(file_path)
    
    def get_total_exported(self) -> int:
        """Retourne le total des éléments exportés."""
        return self.exported_persons + self.exported_families + self.exported_events
