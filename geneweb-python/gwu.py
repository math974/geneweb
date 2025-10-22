#!/usr/bin/env python3
"""Script d'entrée pour GWU."""

import sys
from geneweb.gwu.cli import GwuCLI


def main():
    """Fonction principale."""
    cli = GwuCLI()
    exit_code = cli.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
