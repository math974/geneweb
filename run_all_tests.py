#!/usr/bin/env python3
"""
Script pour lancer tous les tests GWU de manière systématique.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Exécute une commande et retourne le résultat."""
    print(f"\n{'='*60}")
    print(f"🔍 {description}")
    print(f"{'='*60}")
    print(f"Commande: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd="/Users/lucasmaelarnassalom/Project/geneweb")
        print(f"Code de sortie: {result.returncode}")
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
            
        return result.returncode == 0, result
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        return False, None

def main():
    """Lance tous les tests GWU."""
    print("🚀 LANCEMENT DE TOUS LES TESTS GWU")
    print("="*60)
    
    # Configuration
    env = os.environ.copy()
    env['PYTHONPATH'] = '/Users/lucasmaelarnassalom/Project/geneweb/geneweb-python/src'
    
    # Activer l'environnement virtuel
    activate_cmd = "source /Users/lucasmaelarnassalom/Project/geneweb/test_env/bin/activate"
    
    # Tests à exécuter
    test_commands = [
        {
            "cmd": ["python", "-m", "pytest", "tests/unit/test_entities.py", "-v"],
            "description": "Tests des entités (Person, Family, Date, Event, Note)"
        },
        {
            "cmd": ["python", "-m", "pytest", "tests/golden/test_golden_master.py", "-v"],
            "description": "Tests Golden Master (correspondance OCaml)"
        },
        {
            "cmd": ["python", "-m", "pytest", "tests/unit/test_gw_formatting_rules.py", "-v"],
            "description": "Tests des règles de formatage"
        },
        {
            "cmd": ["python", "-m", "pytest", "tests/unit/test_gw_managers.py", "-v"],
            "description": "Tests des gestionnaires"
        },
        {
            "cmd": ["python", "-m", "pytest", "tests/unit/test_gw_writer_clean.py", "-v"],
            "description": "Tests du writer principal"
        },
        {
            "cmd": ["python", "-m", "pytest", "tests/functional/test_gw_export.py", "-v"],
            "description": "Tests fonctionnels d'export"
        },
        {
            "cmd": ["python", "-m", "pytest", "tests/integration/test_cli.py", "-v"],
            "description": "Tests d'intégration CLI"
        },
        {
            "cmd": ["python", "-m", "pytest", "tests/performance/test_performance.py", "-v", "-k", "not memory"],
            "description": "Tests de performance (sans mémoire)"
        }
    ]
    
    # Résultats
    results = []
    total_tests = len(test_commands)
    passed_tests = 0
    
    # Exécuter chaque groupe de tests
    for i, test_cmd in enumerate(test_commands, 1):
        print(f"\n📊 Test {i}/{total_tests}")
        success, result = run_command(test_cmd["cmd"], test_cmd["description"])
        
        results.append({
            "name": test_cmd["description"],
            "success": success,
            "result": result
        })
        
        if success:
            passed_tests += 1
            print(f"✅ {test_cmd['description']} - RÉUSSI")
        else:
            print(f"❌ {test_cmd['description']} - ÉCHOUÉ")
    
    # Résumé final
    print(f"\n{'='*60}")
    print("📊 RÉSUMÉ FINAL")
    print(f"{'='*60}")
    print(f"Tests exécutés: {total_tests}")
    print(f"Tests réussis: {passed_tests}")
    print(f"Tests échoués: {total_tests - passed_tests}")
    print(f"Taux de succès: {(passed_tests/total_tests)*100:.1f}%")
    
    # Détail des échecs
    failed_tests = [r for r in results if not r["success"]]
    if failed_tests:
        print(f"\n❌ TESTS ÉCHOUÉS ({len(failed_tests)}):")
        for test in failed_tests:
            print(f"  - {test['name']}")
    
    # Tests réussis
    successful_tests = [r for r in results if r["success"]]
    if successful_tests:
        print(f"\n✅ TESTS RÉUSSIS ({len(successful_tests)}):")
        for test in successful_tests:
            print(f"  - {test['name']}")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
