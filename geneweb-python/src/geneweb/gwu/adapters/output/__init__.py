"""Adapters de sortie pour GWU."""

from .gw_writer import GwWriter
from .console_writer import ConsoleWriter

__all__ = [
    "GwWriter",
    "ConsoleWriter",
]