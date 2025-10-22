"""
Gestionnaire amélioré des sections page-ext selon les règles OCaml.
Basé sur l'analyse de gwuLib.ml lignes 1808-1893.
"""

import os
from pathlib import Path
from typing import List, Dict, Set, Tuple
from geneweb.gwu.domain.entities.person import Person
from geneweb.gwu.domain.entities.family import Family


class GwPageExtManagerEnhanced:
    """Gestionnaire amélioré des sections page-ext selon OCaml."""
    
    def __init__(self, base_dir: str = "distribution/bases"):
        self.base_dir = Path(base_dir)
        self.ext_files: List[Tuple[str, List[str]]] = []
        self.notes_d_files: List[str] = []
        self.wiznotes_files: List[str] = []
    
    def collect_page_ext_files(self, families: List[Family], persons: List[Person]) -> List[str]:
        """
        Collecte les fichiers page-ext selon les règles OCaml.
        Basé sur gwuLib.ml lignes 1808-1893.
        """
        page_ext_files = []
        
        # 1. Fichiers référencés (gen.ext_files) - ligne 1808
        referenced_files = self._collect_referenced_files(families, persons)
        page_ext_files.extend(referenced_files)
        
        # 2. Fichiers dans notes_d non référencés - ligne 1830
        unreferenced_files = self._collect_unreferenced_files()
        page_ext_files.extend(unreferenced_files)
        
        # 3. Fichiers wiznotes - ligne 1910
        wiznotes_files = self._collect_wiznotes_files()
        page_ext_files.extend(wiznotes_files)
        
        return sorted(set(page_ext_files))
    
    def _collect_referenced_files(self, families: List[Family], persons: List[Person]) -> List[str]:
        """Collecte les fichiers référencés dans les notes."""
        referenced = set()
        
        # Analyser les notes des personnes
        for person in persons:
            if person.notes:
                referenced.update(self._extract_file_references(person.notes))
        
        # Analyser les notes des familles
        for family in families:
            if family.notes:
                # family.notes peut être une liste ou une chaîne
                notes_text = family.notes if isinstance(family.notes, str) else str(family.notes)
                referenced.update(self._extract_file_references(notes_text))
        
        return list(referenced)
    
    def _extract_file_references(self, notes: str) -> Set[str]:
        """Extrait les références de fichiers des notes."""
        references = set()
        
        # Chercher les liens wiki [file.txt]
        import re
        wiki_links = re.findall(r'\[([^]]+\.txt)\]', notes)
        references.update(wiki_links)
        
        # Chercher les liens directs file.txt
        direct_links = re.findall(r'\b([a-zA-Z0-9_-]+\.txt)\b', notes)
        references.update(direct_links)
        
        return references
    
    def _collect_unreferenced_files(self) -> List[str]:
        """Collecte les fichiers dans notes_d non référencés."""
        notes_d_dir = self.base_dir / "notes_d"
        if not notes_d_dir.exists():
            return []
        
        unreferenced = []
        for file_path in notes_d_dir.rglob("*.txt"):
            relative_path = file_path.relative_to(notes_d_dir)
            file_name = str(relative_path).replace(os.sep, "/")
            unreferenced.append(file_name)
        
        return unreferenced
    
    def _collect_wiznotes_files(self) -> List[str]:
        """Collecte les fichiers wiznotes."""
        wiznotes_dir = self.base_dir / "wiznotes"
        if not wiznotes_dir.exists():
            return []
        
        wiznotes = []
        for file_path in wiznotes_dir.rglob("*.txt"):
            relative_path = file_path.relative_to(wiznotes_dir)
            file_name = str(relative_path).replace(os.sep, "/")
            wiznotes.append(file_name)
        
        return wiznotes
    
    def format_page_ext_section(self, file_name: str, content: str) -> List[str]:
        """
        Formate une section page-ext selon OCaml.
        Basé sur gwuLib.ml lignes 1825-1827.
        """
        lines = []
        
        # Commentaire d'information
        lines.append(f"# extended page \"{file_name}\" used by:")
        lines.append(f"#  - {file_name}")
        
        # Section page-ext
        lines.append(f"page-ext {file_name}")
        lines.append(content)
        lines.append("end page-ext")
        
        return lines
    
    def get_page_ext_statistics(self) -> Dict[str, int]:
        """Retourne les statistiques des sections page-ext."""
        return {
            "referenced_files": len(self.ext_files),
            "unreferenced_files": len(self.notes_d_files),
            "wiznotes_files": len(self.wiznotes_files),
            "total": len(self.ext_files) + len(self.notes_d_files) + len(self.wiznotes_files)
        }
