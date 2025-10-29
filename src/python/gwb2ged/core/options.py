"""Export options for gwb2ged"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, List
import sys


class Charset(str, Enum):
    """GEDCOM charset options"""
    ASCII = "ASCII"
    ANSEL = "ANSEL"
    ANSI = "ANSI"
    UTF8 = "UTF-8"


class NoNotes(str, Enum):
    """Note exclusion options"""
    NONE = "none"  # Include all notes
    NN = "nn"  # Exclude database notes
    NNN = "nnn"  # Exclude all notes


@dataclass
class ExportOptions:
    """Options for GeneWeb database to GEDCOM export"""

    # Output options
    output_file: Optional[Path] = None  # Output GEDCOM file (None = stdout)
    charset: Charset = Charset.UTF8
    verbose: bool = False

    # Selection options
    asc: Optional[int] = None  # Maximum generation of root's ascendants
    ascdesc: Optional[int] = None  # Maximum generation of root's ascendants descendants
    desc: Optional[int] = None  # Maximum generation of root's descendants
    keys: List[str] = field(default_factory=list)  # Key references (can be multiple)
    surnames: List[str] = field(default_factory=list)  # Filter by surnames (can be multiple)
    parentship: bool = False  # Select individuals involved in parentship computation

    # Content filtering options
    censor: int = 0  # Censor persons born less than N years ago
    no_notes: NoNotes = NoNotes.NONE  # Note exclusion level
    no_picture: bool = False  # Don't extract individual picture
    picture_path: bool = False  # Extract pictures path
    source: Optional[str] = None  # Replace individuals and families sources

    # Special options
    indexes: bool = False  # Export indexes in GEDCOM
    mem: bool = False  # Save memory space (slower)

    def get_output_stream(self):
        """Get output stream (file or stdout)"""
        if self.output_file is None:
            return sys.stdout, lambda: None
        else:
            output_path = Path(self.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            file_stream = open(output_path, "w", encoding="utf-8")
            return file_stream, file_stream.close

