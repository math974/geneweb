#!/usr/bin/env python3
"""
Gestion de la section notes-db selon les règles OCaml.
Basé sur la logique dans gwuLib.ml:1762-1773
"""

from typing import Optional
from geneweb.gwu.adapters.output.gw_writer import GwWriterOptions


class GwNotesDb:
    """Gestion de la section notes-db selon les règles OCaml."""
    
    @staticmethod
    def should_write_notes_db(options: GwWriterOptions) -> bool:
        """
        Détermine si on doit écrire la section notes-db.
        Basé sur opts.no_notes = `none dans gwuLib.ml:1762
        """
        # En Python, no_notes est un booléen, donc on inverse la logique
        return not options.no_notes
    
    @staticmethod
    def format_notes_db_content(content: str) -> str:
        """
        Formate le contenu de notes-db selon les règles OCaml.
        Basé sur rs_printf dans gwuLib.ml:1604-1615
        """
        if not content or not content.strip():
            return ""
        
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            if line.strip():  # Ignorer les lignes vides
                # Ajouter 2 espaces au début de chaque ligne (comme OCaml)
                formatted_lines.append(f"  {line}")
            else:
                formatted_lines.append("")  # Garder les lignes vides
        
        return '\n'.join(formatted_lines)
    
    @staticmethod
    def write_notes_db_section(f, content: str, options: GwWriterOptions) -> None:
        """
        Écrit la section notes-db complète.
        Basé sur gwuLib.ml:1770-1772
        """
        if not GwNotesDb.should_write_notes_db(options):
            return
        
        if not content or not content.strip():
            return
        
        f.write("notes-db\n")
        formatted_content = GwNotesDb.format_notes_db_content(content)
        f.write(formatted_content)
        f.write("\nend notes-db\n")
