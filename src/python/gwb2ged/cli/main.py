"""Command-line interface for gwb2ged"""

import argparse
import logging
import sys
from pathlib import Path

from ..core.options import ExportOptions, Charset, NoNotes
from ..core.exporter import Gwb2GedExporter


class Gwb2GedCLI:
    """Command-line interface for GWB2GED."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def create_parser(self) -> argparse.ArgumentParser:
        """Create command-line argument parser"""
        parser = argparse.ArgumentParser(
            prog="gwb2ged",
            description="Convert GeneWeb database (MessagePack format) to GEDCOM file",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        # Database argument
        parser.add_argument(
            "database",
            help="Database name or path (without .msgpack extension)",
        )

        # Output options
        parser.add_argument(
            "-o",
            "--output",
            type=Path,
            metavar="FILE",
            help="Output GEDCOM file (default: stdout)",
        )
        parser.add_argument(
            "-charset",
            choices=["ASCII", "ANSEL", "ANSI", "UTF-8"],
            default="UTF-8",
            help="Set charset (default: UTF-8)",
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Verbose output",
        )

        # Selection options
        parser.add_argument(
            "-a",
            type=int,
            metavar="N",
            help="Maximum generation of the root's ascendants",
        )
        parser.add_argument(
            "-ad",
            type=int,
            metavar="N",
            help="Maximum generation of the root's ascendants descendants",
        )
        parser.add_argument(
            "-d",
            type=int,
            metavar="N",
            help="Maximum generation of the root's descendants",
        )
        parser.add_argument(
            "-key",
            action="append",
            metavar="KEY",
            default=[],
            help='Key reference of root person. Can be used multiple times. '
                 'Format: "First Name.occ SURNAME"',
        )
        parser.add_argument(
            "-s",
            action="append",
            metavar="SN",
            default=[],
            dest="surnames",
            help="Select this surname (option usable several times, union of surnames will be used)",
        )
        parser.add_argument(
            "-parentship",
            action="store_true",
            help="Select individuals involved in parentship computation between pairs of keys. "
                 "Pairs must be defined with -key option, descendant first",
        )

        # Content filtering options
        parser.add_argument(
            "-c",
            type=int,
            metavar="NUM",
            default=0,
            help="When a person is born less than NUM years ago, it is not exported unless "
                 "it is Public. All the spouses and descendants are also censored",
        )
        parser.add_argument(
            "-nn",
            action="store_true",
            help="No (database) notes",
        )
        parser.add_argument(
            "-nnn",
            action="store_true",
            help="No notes (implies -nn)",
        )
        parser.add_argument(
            "-nopicture",
            action="store_true",
            help="Don't extract individual picture",
        )
        parser.add_argument(
            "-picture-path",
            action="store_true",
            help="Extract pictures path",
        )
        parser.add_argument(
            "-source",
            metavar="SRC",
            help="Replace individuals and families sources. Also delete event sources",
        )

        # Special options
        parser.add_argument(
            "-indexes",
            action="store_true",
            help="Export indexes in GEDCOM",
        )
        parser.add_argument(
            "-mem",
            action="store_true",
            help="Save memory space, but slower",
        )

        return parser

    def setup_logging(self, verbose: bool) -> None:
        """Setup logging configuration"""
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format="%(levelname)s - %(message)s",
        )

    def parse_options(self, args: argparse.Namespace) -> ExportOptions:
        """Parse command-line arguments into ExportOptions"""
        # Determine no_notes level
        no_notes = NoNotes.NONE
        if args.nnn:
            no_notes = NoNotes.NNN
        elif args.nn:
            no_notes = NoNotes.NN

        # Parse charset
        charset_map = {
            "ASCII": Charset.ASCII,
            "ANSEL": Charset.ANSEL,
            "ANSI": Charset.ANSI,
            "UTF-8": Charset.UTF8,
        }
        charset = charset_map.get(args.charset, Charset.UTF8)

        return ExportOptions(
            output_file=args.output,
            charset=charset,
            verbose=args.verbose,
            asc=args.a,
            ascdesc=args.ad,
            desc=args.d,
            keys=args.key,
            surnames=args.surnames,
            parentship=args.parentship,
            censor=args.c,
            no_notes=no_notes,
            no_picture=args.nopicture,
            picture_path=args.picture_path,
            source=args.source,
            indexes=args.indexes,
            mem=args.mem,
        )

    def run(self, args=None) -> int:
        """Run the CLI with given arguments"""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)

        self.setup_logging(parsed_args.verbose)

        try:
            # Parse options
            options = self.parse_options(parsed_args)

            # Create exporter
            exporter = Gwb2GedExporter(options)

            # Export database
            exporter.export(parsed_args.database)

            return 0

        except KeyboardInterrupt:
            self.logger.error("Interrupted by user")
            return 130
        except Exception as e:
            self.logger.error(f"Error: {e}")
            if parsed_args.verbose:
                import traceback
                traceback.print_exc()
            return 1


def main():
    """Main entry point"""
    cli = Gwb2GedCLI()
    sys.exit(cli.run())

