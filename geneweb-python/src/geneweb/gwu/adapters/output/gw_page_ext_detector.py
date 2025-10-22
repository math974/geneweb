#!/usr/bin/env python3
"""
Détecteur dynamique de pages étendues selon les règles OCaml.
Basé sur l'analyse des fichiers notes_d et wiznotes.
"""

from typing import List, Set, Dict
from pathlib import Path
import os


class PageExtFileDetector:
    """Détecteur de fichiers page-ext selon les règles OCaml."""
    
    def __init__(self):
        self._detected_files: Set[str] = set()
        self._file_content_cache: Dict[str, str] = {}
    
    def detect_page_ext_files(self, base_path: Path) -> List[str]:
        """Détecte les fichiers page-ext selon les règles OCaml."""
        self._reset()
        
        # Détecter depuis notes_d
        notes_d_files = self._detect_from_notes_d(base_path)
        
        # Détecter depuis wiznotes
        wiznotes_files = self._detect_from_wiznotes(base_path)
        
        # Combiner et filtrer
        all_files = notes_d_files.union(wiznotes_files)
        valid_files = self._filter_valid_files(base_path, all_files)
        
        return sorted(list(valid_files))
    
    def _reset(self) -> None:
        """Remet à zéro le détecteur."""
        self._detected_files.clear()
        self._file_content_cache.clear()
    
    def _detect_from_notes_d(self, base_path: Path) -> Set[str]:
        """Détecte les fichiers depuis notes_d."""
        notes_d_path = base_path / "notes_d"
        if not notes_d_path.exists():
            return set()
        
        files = set()
        for file_path in notes_d_path.rglob("*.txt"):
            if file_path.is_file():
                relative_path = file_path.relative_to(notes_d_path)
                file_name = str(relative_path).replace("/", "_").replace(".txt", "")
                files.add(file_name)
        
        return files
    
    def _detect_from_wiznotes(self, base_path: Path) -> Set[str]:
        """Détecte les fichiers depuis wiznotes."""
        wiznotes_path = base_path / "wiznotes"
        if not wiznotes_path.exists():
            return set()
        
        files = set()
        for file_path in wiznotes_path.glob("*.txt"):
            if file_path.is_file():
                file_name = file_path.stem
                files.add(file_name)
        
        return files
    
    def _filter_valid_files(self, base_path: Path, files: Set[str]) -> Set[str]:
        """Filtre les fichiers valides (non vides)."""
        valid_files = set()
        
        for file_name in files:
            content = self._read_file_content(base_path, file_name)
            if content and content.strip():
                valid_files.add(file_name)
        
        return valid_files
    
    def _read_file_content(self, base_path: Path, file_name: str) -> str:
        """Lit le contenu d'un fichier avec cache."""
        if file_name in self._file_content_cache:
            return self._file_content_cache[file_name]
        
        content = self._read_file_from_disk(base_path, file_name)
        self._file_content_cache[file_name] = content
        return content
    
    def _read_file_from_disk(self, base_path: Path, file_name: str) -> str:
        """Lit un fichier depuis le disque."""
        # Essayer notes_d d'abord
        notes_d_path = base_path / "notes_d" / f"{file_name}.txt"
        if notes_d_path.exists():
            return self._read_file(notes_d_path)
        
        # Essayer wiznotes
        wiznotes_path = base_path / "wiznotes" / f"{file_name}.txt"
        if wiznotes_path.exists():
            return self._read_file(wiznotes_path)
        
        return ""
    
    def _read_file(self, file_path: Path) -> str:
        """Lit un fichier avec gestion d'erreurs."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except (IOError, UnicodeDecodeError):
            return ""


class PageExtContentFormatter:
    """Formateur de contenu page-ext selon les règles OCaml."""
    
    @staticmethod
    def format_page_ext_section(file_name: str, content: str) -> List[str]:
        """Formate une section page-ext complète."""
        lines = []
        
        # En-tête
        lines.append(f"# extended page \"{file_name}\" not referenced")
        lines.append(f"page-ext {file_name}")
        
        # Contenu formaté
        content_lines = PageExtContentFormatter._format_content(content)
        lines.extend(content_lines)
        
        # Pied de page
        lines.append("end page-ext")
        
        return lines
    
    @staticmethod
    def _format_content(content: str) -> List[str]:
        """Formate le contenu d'une page étendue."""
        if not content or not content.strip():
            return []
        
        lines = content.strip().split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Ajouter l'indentation de 2 espaces
                formatted_lines.append(f"  {line}")
        
        return formatted_lines


class GwPageExtDetector:
    """Détecteur principal de pages étendues selon les règles OCaml."""
    
    def __init__(self):
        self.file_detector = PageExtFileDetector()
        self.content_formatter = PageExtContentFormatter()
    
    def detect_and_format_page_ext(self, base_path: Path) -> List[List[str]]:
        """Détecte et formate toutes les pages étendues."""
        files = self.file_detector.detect_page_ext_files(base_path)
        
        formatted_sections = []
        for file_name in files:
            content = self.file_detector._read_file_content(base_path, file_name)
            if content and content.strip():
                section = self.content_formatter.format_page_ext_section(file_name, content)
                formatted_sections.append(section)
        
        return formatted_sections
    
    def get_detection_statistics(self, base_path: Path) -> Dict[str, int]:
        """Retourne des statistiques sur la détection."""
        files = self.file_detector.detect_page_ext_files(base_path)
        
        return {
            "total_files_detected": len(files),
            "files_with_content": len([f for f in files if self.file_detector._read_file_content(base_path, f)])
        }
