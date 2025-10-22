#!/usr/bin/env python3
"""
Test de tous les fichiers .gw disponibles.
Validation du système avec différents jeux de données.
"""

import sys
import os
from pathlib import Path
sys.path.append('/Users/lucasmaelarnassalom/Project/geneweb/geneweb-python/src')

from geneweb.gwu.adapters.input.gw_file_repository import GwFilePersonRepository, GwFileFamilyRepository
from geneweb.gwu.adapters.output.gw_writer_clean import GwWriterClean
from geneweb.gwu.adapters.output.gw_writer import GwWriterOptions


def test_gw_file(gw_file_path: str) -> dict:
    """Test un fichier .gw spécifique."""
    try:
        print(f"\n=== TEST: {gw_file_path} ===")
        
        # Charger les données
        person_repo = GwFilePersonRepository(gw_file_path)
        family_repo = GwFileFamilyRepository(gw_file_path)
        
        persons = list(person_repo.get_all())
        families = list(family_repo.get_all())
        
        print(f"Personnes: {len(persons)}")
        print(f"Familles: {len(families)}")
        
        # Générer le fichier
        options = GwWriterOptions()
        writer = GwWriterClean(options)
        
        output_file = f"/tmp/test_{Path(gw_file_path).stem}.gw"
        with open(output_file, 'w', encoding='utf-8') as f:
            writer.write_database(f, families, persons)
        
        # Analyser le résultat
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Compter les sections
        sections = {
            'fam': len([l for l in lines if l.startswith('fam ')]),
            'notes': len([l for l in lines if l.startswith('notes ')]),
            'pevt': len([l for l in lines if l.startswith('pevt ')]),
            'notes-db': len([l for l in lines if l.startswith('notes-db')]),
            'end pevt': len([l for l in lines if l.startswith('end pevt')]),
            'end notes': len([l for l in lines if l == 'end notes']),
            'end': len([l for l in lines if l == 'end']),
            'page-ext': len([l for l in lines if l.startswith('page-ext ')])
        }
        
        result = {
            'file': gw_file_path,
            'persons': len(persons),
            'families': len(families),
            'characters': len(content),
            'lines': len(lines),
            'sections': sections,
            'success': True
        }
        
        print(f"✅ Succès: {len(content)} caractères, {len(lines)} lignes")
        print(f"   Sections: {sections}")
        
        return result
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return {
            'file': gw_file_path,
            'success': False,
            'error': str(e)
        }


def test_multiple_gw_files():
    """Test plusieurs fichiers .gw."""
    print("=== TEST DE TOUS LES FICHIERS .GW ===")
    
    # Fichiers de test principaux
    test_files = [
        "./test/galichet.gw",
        "./test/install-cgi/test.gw", 
        "./test/distribution/bases/test1.golden.gw",
        "./test/distribution/bases/galichet.gw"
    ]
    
    results = []
    
    for gw_file in test_files:
        if os.path.exists(gw_file):
            result = test_gw_file(gw_file)
            results.append(result)
        else:
            print(f"⚠️  Fichier non trouvé: {gw_file}")
    
    # Résumé
    print("\n=== RÉSUMÉ DES TESTS ===")
    successful = [r for r in results if r.get('success', False)]
    failed = [r for r in results if not r.get('success', False)]
    
    print(f"Tests réussis: {len(successful)}")
    print(f"Tests échoués: {len(failed)}")
    
    if successful:
        print("\n=== FICHIERS RÉUSSIS ===")
        for result in successful:
            print(f"✅ {result['file']}")
            print(f"   Personnes: {result['persons']}, Familles: {result['families']}")
            print(f"   Caractères: {result['characters']}, Lignes: {result['lines']}")
            print(f"   Sections: {result['sections']}")
            print()
    
    if failed:
        print("\n=== FICHIERS ÉCHOUÉS ===")
        for result in failed:
            print(f"❌ {result['file']}: {result.get('error', 'Erreur inconnue')}")
    
    return results


if __name__ == "__main__":
    test_multiple_gw_files()
