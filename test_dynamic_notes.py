#!/usr/bin/env python3
"""
Test du système dynamique de gestion des notes.
Validation du nouveau système modulaire et avancé.
"""

import sys
import os
sys.path.append('/Users/lucasmaelarnassalom/Project/geneweb/geneweb-python/src')

from geneweb.gwu.adapters.input.gw_file_repository import GwFilePersonRepository, GwFileFamilyRepository
from geneweb.gwu.adapters.output.gw_writer_clean import GwWriterClean
from geneweb.gwu.adapters.output.gw_writer import GwWriterOptions
from geneweb.gwu.adapters.output.gw_notes_manager import GwNotesManager
from geneweb.gwu.adapters.output.gw_notes_order import GwNotesOrder


def test_dynamic_notes_system():
    """Test du système dynamique de notes."""
    print("=== TEST SYSTÈME DYNAMIQUE DE NOTES ===")
    
    # Charger les données
    from pathlib import Path
    base_path = Path("/Users/lucasmaelarnassalom/Project/geneweb/test")
    person_repo = GwFilePersonRepository(base_path / "galichet.gw")
    family_repo = GwFileFamilyRepository(base_path / "galichet.gw")
    
    persons = list(person_repo.get_all())
    families = list(family_repo.get_all())
    
    print(f"Personnes chargées: {len(persons)}")
    print(f"Familles chargées: {len(families)}")
    
    # Test du gestionnaire de notes
    options = GwWriterOptions()
    notes_manager = GwNotesManager(options)
    
    # Test de l'ordre dynamique
    print("\n=== TEST ORDRE DYNAMIQUE ===")
    ordered_persons = notes_manager.get_ordered_persons_with_notes(families, persons)
    
    print(f"Personnes avec notes (ordre dynamique): {len(ordered_persons)}")
    for i, person in enumerate(ordered_persons, 1):
        print(f"  {i:2d}. {person.surname} {person.first_name}")
    
    # Test des statistiques
    print("\n=== STATISTIQUES ===")
    stats = notes_manager.get_notes_statistics(families, persons)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test de validation
    print("\n=== VALIDATION ===")
    errors = notes_manager.validate_all_notes(families, persons)
    for error_type, error_list in errors.items():
        if error_list:
            print(f"  {error_type}: {len(error_list)} erreurs")
            for error in error_list[:3]:  # Afficher les 3 premières
                print(f"    - {error}")
        else:
            print(f"  {error_type}: ✅ Aucune erreur")
    
    # Test de génération
    print("\n=== GÉNÉRATION ===")
    try:
        writer = GwWriterClean(options)
        
        with open('/tmp/python_dynamic_notes.gw', 'w', encoding='utf-8') as f:
            writer.write_database(f, families, persons)
        
        print("✅ Fichier généré: /tmp/python_dynamic_notes.gw")
        
        # Comparer avec l'OCaml
        with open('/tmp/ocaml_full.gw', 'r', encoding='utf-8') as f:
            ocaml_content = f.read()
        with open('/tmp/python_dynamic_notes.gw', 'r', encoding='utf-8') as f:
            python_content = f.read()
        
        ocaml_lines = ocaml_content.split('\n')
        python_lines = python_content.split('\n')
        
        print(f"\n=== COMPARAISON ===")
        print(f"OCaml:  {len(ocaml_content)} caractères, {len(ocaml_lines)} lignes")
        print(f"Python: {len(python_content)} caractères, {len(python_lines)} lignes")
        print(f"Progression: {len(python_content)/len(ocaml_content)*100:.1f}% des caractères")
        print(f"Progression: {len(python_lines)/len(ocaml_lines)*100:.1f}% des lignes")
        
        # Compter les sections notes
        notes_oc = len([l for l in ocaml_lines if l.startswith('notes ')])
        notes_py = len([l for l in python_lines if l.startswith('notes ')])
        print(f"Notes: OCaml={notes_oc}, Python={notes_py}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération: {e}")
        import traceback
        traceback.print_exc()


def test_notes_order_strategies():
    """Test des différentes stratégies d'ordre."""
    print("\n=== TEST STRATÉGIES D'ORDRE ===")
    
    # Charger les données
    from pathlib import Path
    base_path = Path("/Users/lucasmaelarnassalom/Project/geneweb/test")
    person_repo = GwFilePersonRepository(base_path / "galichet.gw")
    family_repo = GwFileFamilyRepository(base_path / "galichet.gw")
    
    persons = list(person_repo.get_all())
    families = list(family_repo.get_all())
    
    strategies = ["family_based", "chronological", "alphabetical"]
    
    for strategy in strategies:
        print(f"\n--- Stratégie: {strategy} ---")
        notes_order = GwNotesOrder(strategy=strategy)
        ordered_persons = notes_order.get_ordered_persons_with_notes(families, persons)
        
        print(f"Personnes avec notes: {len(ordered_persons)}")
        for i, person in enumerate(ordered_persons[:5], 1):  # Afficher les 5 premières
            print(f"  {i}. {person.surname} {person.first_name}")


if __name__ == "__main__":
    test_dynamic_notes_system()
    test_notes_order_strategies()
