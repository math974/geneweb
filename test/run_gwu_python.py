#!/usr/bin/env python3
"""
Script d'entrée pour GWU Python.
"""

import sys
from geneweb.gwu.cli.gwu_cli import GwuCLI

def main():
    cli = GwuCLI()
    result = cli.run(sys.argv[1:])
    sys.exit(result)

if __name__ == "__main__":
    main()
