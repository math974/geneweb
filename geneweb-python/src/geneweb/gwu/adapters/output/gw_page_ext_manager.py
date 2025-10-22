#!/usr/bin/env python3
"""
Gestionnaire dynamique des pages étendues (page-ext) selon les règles OCaml.
Basé sur la logique page-ext dans gwuLib.ml:1820-1893
"""

from typing import List, Dict, Optional, Set
from pathlib import Path
import os
from geneweb.gwu.adapters.output.gw_page_ext_detector import GwPageExtDetector


class PageExtCollector:
    """Collecteur de pages étendues selon les règles OCaml."""
    
    def __init__(self):
        self._ext_files: Set[str] = set()
        self._referenced_files: Dict[str, List[str]] = {}
    
    def collect_from_base(self, base_path: Path) -> List[str]:
        """
        Collecte les pages étendues depuis la base de données.
        Basé sur la logique OCaml de collecte des fichiers.
        """
        self._reset()
        
        # Collecter depuis notes_d (comme OCaml)
        notes_d_path = base_path / "notes_d"
        if notes_d_path.exists():
            self._collect_from_notes_d(notes_d_path)
        
        # Collecter depuis wiznotes_dir (comme OCaml)
        wiznotes_path = base_path / "wiznotes"
        if wiznotes_path.exists():
            self._collect_from_wiznotes(wiznotes_path)
        
        # Filtrer les fichiers vides (comme OCaml)
        return self._filter_non_empty_files(base_path)
    
    def _reset(self) -> None:
        """Remet à zéro l'état du collecteur."""
        self._ext_files.clear()
        self._referenced_files.clear()
    
    def _collect_from_notes_d(self, notes_d_path: Path) -> None:
        """Collecte les fichiers depuis notes_d."""
        for file_path in notes_d_path.rglob("*.txt"):
            if file_path.is_file():
                relative_path = file_path.relative_to(notes_d_path)
                file_name = str(relative_path).replace("/", "_").replace(".txt", "")
                self._ext_files.add(file_name)
    
    def _collect_from_wiznotes(self, wiznotes_path: Path) -> None:
        """Collecte les fichiers depuis wiznotes."""
        for file_path in wiznotes_path.glob("*.txt"):
            if file_path.is_file():
                file_name = file_path.stem
                self._ext_files.add(file_name)
    
    def _filter_non_empty_files(self, base_path: Path) -> List[str]:
        """Filtre les fichiers non vides comme l'OCaml."""
        valid_files = []
        
        for file_name in self._ext_files:
            content = self.read_page_ext_content(base_path, file_name)
            if content and content.strip():
                valid_files.append(file_name)
        
        return sorted(valid_files)
    
    def add_reference(self, file_name: str, reference: str) -> None:
        """Ajoute une référence à un fichier."""
        if file_name not in self._referenced_files:
            self._referenced_files[file_name] = []
        self._referenced_files[file_name].append(reference)


class PageExtFormatter:
    """Formateur de pages étendues selon les règles OCaml."""
    
    @staticmethod
    def format_page_ext_header(file_name: str, references: List[str]) -> List[str]:
        """
        Formate l'en-tête d'une page étendue.
        Basé sur la logique OCaml:1820-1825
        """
        lines = []
        
        if references:
            lines.append(f"# extended page \"{file_name}\" used by:")
            for ref in sorted(references):
                lines.append(f"#  - {ref}")
        
        lines.append(f"page-ext {file_name}")
        return lines
    
    @staticmethod
    def format_page_ext_footer() -> str:
        """Formate le pied de page d'une page étendue."""
        return "end page-ext"
    
    @staticmethod
    def format_page_ext_content(content: str) -> List[str]:
        """
        Formate le contenu d'une page étendue.
        Basé sur rs_printf dans gwuLib.ml
        """
        if not content or not content.strip():
            return []
        
        # Diviser par lignes et formater
        lines = content.strip().split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Ajouter l'indentation de 2 espaces
                formatted_lines.append(f"  {line}")
        
        return formatted_lines


class GwPageExtManager:
    """Gestionnaire principal des pages étendues selon les règles OCaml."""
    
    def __init__(self, options):
        """
        Initialise le gestionnaire de pages étendues.
        
        Args:
            options: Options de configuration (GwWriterOptions)
        """
        self.options = options
        self.collector = PageExtCollector()
        self.formatter = PageExtFormatter()
        self.detector = GwPageExtDetector()
    
    def get_page_ext_files(self, base_path: Path) -> List[str]:
        """
        Retourne la liste des fichiers page-ext.
        Utilise le détecteur dynamique.
        """
        return self.detector.file_detector.detect_page_ext_files(base_path)
    
    def format_page_ext_section(self, file_name: str, content: str, 
                               references: List[str] = None) -> List[str]:
        """
        Formate une section page-ext complète.
        """
        lines = []
        
        # En-tête
        header_lines = self.formatter.format_page_ext_header(
            file_name, references or []
        )
        lines.extend(header_lines)
        
        # Contenu
        content_lines = self.formatter.format_page_ext_content(content)
        lines.extend(content_lines)
        
        # Pied de page
        lines.append(self.formatter.format_page_ext_footer())
        
        return lines
    
    def read_page_ext_content(self, base_path: Path, file_name: str) -> Optional[str]:
        """
        Lit le contenu d'un fichier page-ext.
        """
        # Essayer notes_d d'abord
        notes_d_path = base_path / "notes_d" / f"{file_name}.txt"
        if notes_d_path.exists():
            return self._read_file_content(notes_d_path)
        
        # Essayer wiznotes
        wiznotes_path = base_path / "wiznotes" / f"{file_name}.txt"
        if wiznotes_path.exists():
            return self._read_file_content(wiznotes_path)
        
        return None
    
    def _read_file_content(self, file_path: Path) -> Optional[str]:
        """Lit le contenu d'un fichier."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except (IOError, UnicodeDecodeError):
            return None
    
    def get_page_ext_statistics(self, base_path: Path) -> Dict[str, int]:
        """
        Retourne des statistiques sur les pages étendues.
        """
        files = self.get_page_ext_files(base_path)
        total_files = len(files)
        
        # Compter les fichiers avec contenu
        files_with_content = 0
        for file_name in files:
            content = self.read_page_ext_content(base_path, file_name)
            if content and content.strip():
                files_with_content += 1
        
        return {
            "total_page_ext_files": total_files,
            "files_with_content": files_with_content,
            "empty_files": total_files - files_with_content
        }
