"""Main exporter for gwb2ged"""

import logging
from pathlib import Path
from typing import Optional

from lib.db.io.msgpack import MessagePackReader
from lib.db.database.base import Base

from .options import ExportOptions


class Gwb2GedExporter:
    """Export GeneWeb MessagePack database to GEDCOM format"""

    def __init__(self, options: ExportOptions):
        """
        Initialize exporter with options

        Args:
            options: Export options configuration
        """
        self.options = options
        self.logger = logging.getLogger(__name__)

    def export(self, database_name: str, base_dir: Optional[Path] = None) -> None:
        """
        Export database to GEDCOM format

        Args:
            database_name: Name of the database (without extension)
            base_dir: Base directory containing the databases (default: distribution/bases)
        """
        self.logger.info(f"Exporting database: {database_name}")

        # Determine base directory
        if base_dir is None:
            # Try to find distribution/bases from project root
            from tools.test_utils import get_project_root
            project_root = get_project_root()
            base_dir = project_root / "distribution" / "bases"
        else:
            base_dir = Path(base_dir)

        # Load MessagePack database
        self.logger.debug(f"Loading database from: {base_dir}")
        reader = MessagePackReader(str(base_dir))
        data = reader.load_database(database_name)
        base = Base(data)

        self.logger.info(f"Loaded database: {base.nb_of_persons()} persons, "
                        f"{base.nb_of_families()} families")

        # Get output stream
        output_stream, close_func = self.options.get_output_stream()

        try:
            # Export to GEDCOM
            self._export_gedcom(base, output_stream, database_name)
            self.logger.info("Export completed successfully")

        finally:
            close_func()

    def _export_gedcom(self, base: Base, output: any, database_name: str) -> None:
        """
        Export base to GEDCOM format

        Args:
            base: GeneWeb Base object
            output: Output stream (file-like object)
            database_name: Name of the database
        """
        # TODO: Implement full GEDCOM export
        # For now, create a basic GEDCOM structure

        # Write HEAD
        output.write("0 HEAD\n")
        output.write("1 SOUR GeneWeb\n")
        output.write("2 VERS 0.1.0\n")
        output.write("2 NAME gwb2ged\n")
        output.write("1 GEDC\n")

        # Write charset
        if self.options.charset.value == "UTF-8":
            output.write("2 VERS 5.5.1\n")
        else:
            output.write("2 VERS 5.5\n")

        output.write("2 FORM LINEAGE-LINKED\n")
        output.write(f"1 CHAR {self.options.charset.value}\n")

        if self.options.output_file:
            output.write(f"1 FILE {Path(self.options.output_file).name}\n")

        # TODO: Export persons and families
        # This requires implementing the full conversion from Base to GEDCOM
        # For now, just write TRLR
        output.write("0 TRLR\n")

        if self.options.verbose:
            self.logger.debug("Wrote basic GEDCOM structure (full export not yet implemented)")

