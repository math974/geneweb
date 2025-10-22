#!/usr/bin/env python3
"""
Test simple pour vérifier que le système fonctionne.
"""

import sys
import os
sys.path.append('/Users/lucasmaelarnassalom/Project/geneweb/geneweb-python/src')

from geneweb.gwu.adapters.input.gw_file_repository import GwFilePersonRepository, GwFileFamilyRepository
from geneweb.gwu.adapters.output.gw_writer_clean import GwWriterClean
from geneweb.gwu.adapters.output.gw_writer import GwWriterOptions


def test_basic_functionality():
    """Test basique du système."""
    print("=== TEST BASIQUE DU SYSTÈME GWU ===")
    
    # Test avec le fichier galichet.gw
    gw_file = "/Users/lucasmaelarnassalom/Project/geneweb/test/galichet.gw"
    
    if not os.path.exists(gw_file):
        print(f"❌ Fichier non trouvé: {gw_file}")
        return False
    
    try:
        # Charger les données
        print("📁 Chargement des données...")
        person_repo = GwFilePersonRepository(gw_file)
        family_repo = GwFileFamilyRepository(gw_file)
        
        persons = list(person_repo.get_all())
        families = list(family_repo.get_all())
        
        print(f"✅ Personnes chargées: {len(persons)}")
        print(f"✅ Familles chargées: {len(families)}")
        
        # Générer le fichier
        print("📝 Génération du fichier...")
        options = GwWriterOptions()
        writer = GwWriterClean(options)
        
        output_file = "/tmp/test_simple_output.gw"
        with open(output_file, 'w', encoding='utf-8') as f:
            writer.write_database(f, families, persons)
        
        # Vérifier le résultat
        print("🔍 Vérification du résultat...")
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
        
        print(f"📊 Résultats:")
        print(f"   Caractères: {len(content)}")
        print(f"   Lignes: {len(lines)}")
        print(f"   Sections: {sections}")
        
        # Vérifier les valeurs attendues
        expected = {
            'fam': 15,
            'notes': 7,
            'pevt': 28,
            'notes-db': 1,
            'end pevt': 28,
            'end notes': 7,
            'end': 65,
            'page-ext': 3
        }
        
        all_correct = True
        for section, expected_count in expected.items():
            actual_count = sections[section]
            status = "✅" if actual_count == expected_count else "❌"
            print(f"   {section:12}: {actual_count:2d} vs {expected_count:2d} {status}")
            if actual_count != expected_count:
                all_correct = False
        
        if all_correct:
            print("\n🎉🎉🎉 TOUS LES TESTS RÉUSSIS ! 🎉🎉🎉")
            print("🎉 SYSTÈME 100% FONCTIONNEL !")
            print("🎉 MISSION ACCOMPLIE !")
            return True
        else:
            print("\n❌ Certains tests ont échoué.")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Nettoyer
        if os.path.exists(output_file):
            os.unlink(output_file)


if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)
