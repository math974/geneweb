#!/usr/bin/env python3
"""
Test du nouveau système de formatage basé sur les règles OCaml.
"""

import sys
from pathlib import Path
sys.path.append('geneweb-python/src')

from geneweb.gwu.adapters.input.gw_file_repository import GwFileRepository
from geneweb.gwu.adapters.output.gw_writer_clean import GwWriterClean
from geneweb.gwu.adapters.output.gw_writer import GwWriterOptions
import subprocess


def test_clean_formatting():
    """Test du nouveau système de formatage."""
    print("🧪 Test du nouveau système de formatage basé sur les règles OCaml")
    
    # Charger les données
    print("📁 Chargement des données...")
    repo = GwFileRepository(Path('distribution/bases/galichet.raw.current.gw'))
    
    # Créer les options
    options = GwWriterOptions()
    
    # Créer le writer propre
    writer = GwWriterClean(options)
    
    # Générer le fichier
    print("✍️  Génération du fichier avec les règles OCaml...")
    output_path = Path('/tmp/python_clean.gw')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        writer.write_database(f, list(repo.families.get_all()), list(repo.persons.get_all()))
    
    # Comparer avec OCaml
    print("🔍 Comparaison avec OCaml...")
    ocaml_path = Path('/tmp/ocaml_full.gw')
    
    if not ocaml_path.exists():
        print("❌ Fichier OCaml manquant. Génération...")
        subprocess.run([
            "distribution/gw/gwu", 
            "distribution/bases/galichet.raw.current.gw", 
            "-o", str(ocaml_path)
        ], check=True)
    
    # Comparaison
    result = subprocess.run(['cmp', str(output_path), str(ocaml_path)], 
                           capture_output=True, text=True)
    
    if result.returncode == 0:
        print("🎉 SUCCÈS ! Fichiers identiques byte-à-byte !")
        return True
    else:
        print("❌ Différences détectées")
        
        # Analyser les différences
        py_content = output_path.read_text(encoding='utf-8', errors='replace')
        oc_content = ocaml_path.read_text(encoding='utf-8', errors='replace')
        
        py_lines = py_content.split('\n')
        oc_lines = oc_content.split('\n')
        
        print(f"📊 Taille: Python={len(py_content)}, OCaml={len(oc_content)}")
        print(f"📝 Lignes: Python={len(py_lines)}, OCaml={len(oc_lines)}")
        
        # Première différence
        for i in range(max(len(py_lines), len(oc_lines))):
            py_line = py_lines[i] if i < len(py_lines) else ''
            oc_line = oc_lines[i] if i < len(oc_lines) else ''
            if py_line != oc_line:
                print(f"\n❌ Première différence à la ligne {i+1}:")
                print(f"  PY: {repr(py_line[:100])}")
                print(f"  OC: {repr(oc_line[:100])}")
                break
        
        return False


if __name__ == "__main__":
    success = test_clean_formatting()
    sys.exit(0 if success else 1)
