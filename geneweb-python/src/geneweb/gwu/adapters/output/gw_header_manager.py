#!/usr/bin/env python3
"""
Gestionnaire des en-têtes GW selon les règles OCaml.
Basé sur la logique d'en-tête dans gwuLib.ml
"""

from typing import List, Dict
from geneweb.gwu.adapters.output.gw_writer import GwWriterOptions


class GwHeaderFormatter:
    """Formateur d'en-têtes GW selon les règles OCaml."""
    
    @staticmethod
    def format_gw_header(options: GwWriterOptions) -> List[str]:
        """
        Formate l'en-tête GW selon les règles OCaml.
        Basé sur la logique d'en-tête dans gwuLib.ml
        """
        lines = []
        
        # gwplus doit être en premier (comme OCaml)
        lines.append("gwplus")
        lines.append("")  # Ligne vide après gwplus
        
        # encoding seulement si nécessaire
        if hasattr(options, 'encoding') and options.encoding:
            lines.append(f"encoding: {options.encoding}")
        
        return lines
    
    @staticmethod
    def should_write_encoding(options: GwWriterOptions) -> bool:
        """Détermine si l'encoding doit être écrit."""
        return (hasattr(options, 'encoding') and 
                options.encoding and 
                options.encoding.lower() != 'utf-8')


class GwHeaderManager:
    """Gestionnaire principal des en-têtes GW selon les règles OCaml."""
    
    def __init__(self, options: GwWriterOptions):
        """
        Initialise le gestionnaire d'en-têtes.
        
        Args:
            options: Options de configuration
        """
        self.options = options
        self.formatter = GwHeaderFormatter()
    
    def write_gw_header(self, f) -> None:
        """
        Écrit l'en-tête GW dans le fichier.
        """
        header_lines = self.formatter.format_gw_header(self.options)
        
        for line in header_lines:
            f.write(line + "\n")
    
    def get_header_info(self) -> Dict[str, any]:
        """
        Retourne des informations sur l'en-tête.
        """
        return {
            "has_gwplus": True,
            "has_encoding": self.formatter.should_write_encoding(self.options),
            "encoding": getattr(self.options, 'encoding', 'utf-8')
        }
