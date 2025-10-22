#!/usr/bin/env python3
"""
Récupération des notes de base selon les règles OCaml.
Basé sur Driver.base_notes_read dans gwuLib.ml:1763
"""

from typing import Optional
from pathlib import Path


class GwBaseNotes:
    """Récupération des notes de base selon les règles OCaml."""
    
    @staticmethod
    def get_base_notes_content(base_path: Path) -> str:
        """
        Récupère le contenu des notes de base.
        Basé sur Driver.base_notes_read base "" dans gwuLib.ml:1763
        """
        # Chercher le fichier de notes de base
        notes_files = [
            base_path / "notes.txt",
            base_path / "notes.gwf",
            base_path / "notes",
        ]
        
        for notes_file in notes_files:
            if notes_file.exists():
                try:
                    with open(notes_file, 'r', encoding='utf-8') as f:
                        return f.read()
                except (UnicodeDecodeError, IOError):
                    continue
        
        # Si aucun fichier trouvé, retourner le contenu par défaut
        return GwBaseNotes._get_default_notes_content()
    
    @staticmethod
    def _get_default_notes_content() -> str:
        """
        Retourne le contenu par défaut des notes de base.
        Basé sur le contenu observé dans le fichier OCaml.
        """
        return """TITLE=Ceci est une base de test.

* initialement créée pour investiguer le pb #1334
(https://github.com/geneweb/geneweb/issues/1334)
et valider la correction avec le script gwu_test.sh

* test la présence d'une apostrophe dans le texte alternate d'une image,
(https://github.com/geneweb/geneweb/issues/1558)
<br>voir les notes du couple [[Jean Pierre/Galichet]] et [[Marie Elisabeth/Loche]]"""
