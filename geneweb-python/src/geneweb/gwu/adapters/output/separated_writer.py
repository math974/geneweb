"""Writer pour export séparé."""

from pathlib import Path
from typing import Set, List, Optional

from geneweb.common.types import PersonId, FamilyId
from geneweb.gwu.domain.entities import Person, Family
from geneweb.gwu.domain.config import ExportOptions
from .gw_file_writer import GwFileWriter
from .console_writer import ConsoleWriter


class SeparatedWriter:
    """
    Writer pour export séparé.
    
    Gère l'export de données avec séparation par personne
    ou par famille selon les options.
    """

    def __init__(self, options: ExportOptions, console_writer: Optional[ConsoleWriter] = None):
        """
        Initialise le writer.
        
        Args:
            options: Options d'export
            console_writer: Writer console pour logs
        """
        self.options = options
        self.console_writer = console_writer or ConsoleWriter()
        self.gw_writer = GwFileWriter(options)

    def write_separated(
        self,
        output_dir: Path,
        persons: List[Person],
        families: List[Family],
        selected_person_ids: Set[PersonId],
        selected_family_ids: Set[FamilyId]
    ) -> List[str]:
        """
        Écrit les données avec séparation.
        
        Args:
            output_dir: Répertoire de destination
            persons: Liste des personnes
            families: Liste des familles
            selected_person_ids: IDs des personnes sélectionnées
            selected_family_ids: IDs des familles sélectionnées
            
        Returns:
            Liste des fichiers générés
        """
        # Créer le répertoire s'il n'existe pas
        output_dir.mkdir(parents=True, exist_ok=True)
        
        generated_files = []
        
        # Filtrer les données sélectionnées
        selected_persons = [p for p in persons if p.person_id in selected_person_ids]
        selected_families = [f for f in families if f.family_id in selected_family_ids]
        
        # Export par personne
        for person in selected_persons:
            person_file = output_dir / f"{person.person_id}.gw"
            self.gw_writer.write_person(person_file, person)
            generated_files.append(str(person_file))
        
        # Export par famille
        for family in selected_families:
            family_file = output_dir / f"{family.family_id}.gw"
            self.gw_writer.write_family(family_file, family)
            generated_files.append(str(family_file))
        
        # Logs
        self.console_writer.log_info(f"Export séparé vers: {output_dir}")
        self.console_writer.log_info(f"Fichiers générés: {len(generated_files)}")
        
        return generated_files