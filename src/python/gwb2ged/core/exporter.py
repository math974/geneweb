"""Main exporter for gwb2ged"""

import logging
import sys
from pathlib import Path
from typing import Optional

from lib.db.io.msgpack import MessagePackReader
from lib.db.database.base import Base
from gedcom.exporter import GedcomExporter

from .options import ExportOptions
from .converter import BaseToGedcomConverter


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
        base = Base(data, db_name=database_name, data_dir=str(base_dir))

        self.logger.info(
            f"Loaded database: {base.nb_of_persons()} persons, "
            f"{base.nb_of_families()} families"
        )

        # Convert Base to GEDCOM
        self.logger.debug("Converting Base to GEDCOM format")
        converter = BaseToGedcomConverter(base, self.options)
        gedcom_db = converter.convert()

        # Export GEDCOM
        if self.options.output_file:
            # Export to file
            self.logger.info(f"Exporting to file: {self.options.output_file}")
            gedcom_exporter = GedcomExporter()
            encoding = self._get_encoding()
            gedcom_exporter.export_file(
                self.options.output_file, gedcom_db, encoding=encoding
            )
        else:
            # Export to stdout
            self.logger.debug("Exporting to stdout")
            gedcom_exporter = GedcomExporter()
            encoding = self._get_encoding()
            # Reopen stdout with correct encoding if needed
            if encoding != "utf-8":
                import io

                output = io.TextIOWrapper(
                    sys.stdout.buffer, encoding=encoding, errors="replace"
                )
                gedcom_exporter.export_content(output, gedcom_db)
            else:
                gedcom_exporter.export_content(sys.stdout, gedcom_db)

        self.logger.info("Export completed successfully")

    def _get_encoding(self) -> str:
        """Get encoding based on charset option"""
        charset_encoding_map = {
            "UTF-8": "utf-8",
            "ASCII": "ascii",
            "ANSI": "latin-1",  # ANSI is typically Windows-1252, use latin-1 as fallback
            "ANSEL": "latin-1",  # ANSEL encoding
        }
        return charset_encoding_map.get(self.options.charset.value, "utf-8")
