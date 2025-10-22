#!/usr/bin/env python3
"""
Gestionnaire avancé des notes selon les règles OCaml.
Système modulaire et dynamique pour le traitement des notes.
"""

from typing import List, Dict, Optional, Tuple, Any
from geneweb.gwu.domain.entities.person import Person
from geneweb.gwu.domain.entities.family import Family
from geneweb.gwu.adapters.output.gw_notes_order import GwNotesOrder
from geneweb.gwu.adapters.output.gw_notes_db import GwNotesDb
from geneweb.gwu.adapters.output.gw_base_notes import GwBaseNotes


class NotesContentProcessor:
    """Processeur de contenu des notes selon les règles OCaml."""
    
    @staticmethod
    def process_person_notes(notes: str) -> List[str]:
        """
        Traite les notes d'une personne selon les règles OCaml.
        Basé sur print_notes_for_person dans gwuLib.ml:968-1031
        """
        if not notes or not notes.strip():
            return []
        
        # Diviser par lignes et nettoyer
        lines = [line.strip() for line in notes.split('\n') if line.strip()]
        
        # Appliquer les règles de formatage OCaml
        processed_lines = []
        for line in lines:
            processed_line = NotesContentProcessor._format_note_line(line)
            if processed_line:
                processed_lines.append(processed_line)
        
        return processed_lines
    
    @staticmethod
    def _format_note_line(line: str) -> Optional[str]:
        """
        Formate une ligne de note selon les règles OCaml.
        Basé sur rs_printf dans gwuLib.ml:1604-1615
        """
        if not line:
            return None
        
        # Règles de formatage OCaml
        line = line.strip()
        
        # Ne pas ajouter de préfixe * pour les notes principales
        # (contrairement aux notes de famille)
        return line if line else None
    
    @staticmethod
    def process_family_notes(notes) -> List[str]:
        """
        Traite les notes de famille selon les règles OCaml.
        Différent du traitement des notes de personne.
        """
        if not notes:
            return []
        
        # family.notes peut être une liste ou une chaîne
        if isinstance(notes, list):
            lines = [note.strip() for note in notes if note and note.strip()]
        else:
            if not notes.strip():
                return []
            lines = [line.strip() for line in notes.split('\n') if line.strip()]
        
        processed_lines = []
        for line in lines:
            # Pour les familles, on peut ajouter des préfixes spéciaux
            processed_line = f"  {line}" if line else None
            if processed_line:
                processed_lines.append(processed_line)
        
        return processed_lines


class NotesValidationEngine:
    """Moteur de validation des notes selon les règles OCaml."""
    
    @staticmethod
    def validate_person_notes(person: Person) -> Tuple[bool, List[str]]:
        """
        Valide les notes d'une personne.
        
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        if not person.has_notes():
            return True, []
        
        if not person.notes or not person.notes.strip():
            errors.append(f"Personne {person.surname} {person.first_name} a has_notes()=True mais notes vides")
        
        # Validation du contenu
        processed_notes = NotesContentProcessor.process_person_notes(person.notes)
        if not processed_notes:
            errors.append(f"Personne {person.surname} {person.first_name} a des notes mais aucun contenu valide")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_family_notes(family: Family) -> Tuple[bool, List[str]]:
        """
        Valide les notes d'une famille.
        
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        if not family.notes:
            return True, []
        
        # family.notes peut être une liste ou une chaîne
        if isinstance(family.notes, list):
            if not family.notes or not any(note.strip() for note in family.notes if note):
                errors.append(f"Famille {family.family_id} a des notes vides")
        else:
            if not family.notes.strip():
                errors.append(f"Famille {family.family_id} a des notes vides")
        
        return len(errors) == 0, errors


class GwNotesManager:
    """Gestionnaire principal des notes selon les règles OCaml."""
    
    def __init__(self, options: Any):
        """
        Initialise le gestionnaire de notes.
        
        Args:
            options: Options de configuration (GwWriterOptions)
        """
        self.options = options
        self.notes_order = GwNotesOrder(strategy="family_based")
        self.notes_db = GwNotesDb()
        self.base_notes = GwBaseNotes()
        self.content_processor = NotesContentProcessor()
        self.validator = NotesValidationEngine()
    
    def get_ordered_persons_with_notes(self, families: List[Family], 
                                     persons: List[Person]) -> List[Person]:
        """
        Retourne les personnes avec notes dans l'ordre OCaml.
        """
        return self.notes_order.get_ordered_persons_with_notes(families, persons)
    
    def should_write_notes_db(self) -> bool:
        """
        Détermine si la section notes-db doit être écrite.
        """
        return self.notes_db.should_write_notes_db(self.options)
    
    def get_notes_db_content(self, base_path: str) -> Optional[str]:
        """
        Récupère le contenu des notes de base.
        """
        return self.base_notes.get_base_notes_content(base_path)
    
    def write_notes_db_section(self, f, base_path: str) -> None:
        """
        Écrit la section notes-db.
        """
        if self.should_write_notes_db():
            content = self.get_notes_db_content(base_path)
            if content:
                self.notes_db.write_notes_db_section(f, content, self.options)
    
    def process_person_notes(self, person: Person) -> List[str]:
        """
        Traite les notes d'une personne.
        """
        # person.notes est une chaîne, pas un objet Note
        if not person.notes or not person.notes.strip():
            return []
        return self.content_processor.process_person_notes(person.notes)
    
    def process_family_notes(self, family: Family) -> List[str]:
        """
        Traite les notes d'une famille.
        """
        return self.content_processor.process_family_notes(family.notes)
    
    def validate_all_notes(self, families: List[Family], 
                          persons: List[Person]) -> Dict[str, List[str]]:
        """
        Valide toutes les notes et retourne les erreurs.
        
        Returns:
            Dictionnaire avec les erreurs par type
        """
        errors = {
            "person_notes": [],
            "family_notes": []
        }
        
        # Validation des notes de personnes
        for person in persons:
            if person.has_notes():
                is_valid, person_errors = self.validator.validate_person_notes(person)
                if not is_valid:
                    errors["person_notes"].extend(person_errors)
        
        # Validation des notes de familles
        for family in families:
            if family.notes:
                is_valid, family_errors = self.validator.validate_family_notes(family)
                if not is_valid:
                    errors["family_notes"].extend(family_errors)
        
        return errors
    
    def get_notes_statistics(self, families: List[Family], 
                           persons: List[Person]) -> Dict[str, Any]:
        """
        Retourne des statistiques complètes sur les notes.
        """
        base_stats = self.notes_order.get_notes_statistics(families, persons)
        
        # Statistiques supplémentaires
        total_notes_chars = sum(len(p.notes or "") for p in persons if p.has_notes())
        family_notes_count = sum(1 for f in families if f.notes)
        
        base_stats.update({
            "total_notes_characters": total_notes_chars,
            "families_with_notes": family_notes_count,
            "average_notes_length": total_notes_chars / base_stats["persons_with_notes"] if base_stats["persons_with_notes"] > 0 else 0
        })
        
        return base_stats
