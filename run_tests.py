#!/usr/bin/env python3
"""
Script de lancement des tests GWU.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_tests(test_type="all", verbose=False):
    """Lance les tests selon le type spécifié."""
    
    # Configuration de base
    base_cmd = ["python", "-m", "pytest"]
    
    if verbose:
        base_cmd.append("-v")
    
    # Configuration par type de test
    if test_type == "unit":
        cmd = base_cmd + ["tests/unit/", "-m", "unit"]
    elif test_type == "functional":
        cmd = base_cmd + ["tests/functional/", "-m", "functional"]
    elif test_type == "integration":
        cmd = base_cmd + ["tests/integration/", "-m", "integration"]
    elif test_type == "golden":
        cmd = base_cmd + ["tests/golden/", "-m", "golden"]
    elif test_type == "performance":
        cmd = base_cmd + ["tests/performance/", "-m", "performance"]
    elif test_type == "all":
        cmd = base_cmd + ["tests/"]
    else:
        print(f"Type de test inconnu: {test_type}")
        return False
    
    # Ajouter des options supplémentaires
    cmd.extend([
        "--tb=short",
        "--color=yes",
        "--durations=10"
    ])
    
    print(f"Lancement des tests: {' '.join(cmd)}")
    print("=" * 60)
    
    # Lancer les tests
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    
    return result.returncode == 0


def main():
    """Fonction principale."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Lanceur de tests GWU")
    parser.add_argument(
        "test_type",
        nargs="?",
        default="all",
        choices=["unit", "functional", "integration", "golden", "performance", "all"],
        help="Type de tests à lancer"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Mode verbeux"
    )
    
    args = parser.parse_args()
    
    # Vérifier que pytest est installé
    try:
        subprocess.run(["python", "-m", "pytest", "--version"], 
                      capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("❌ pytest n'est pas installé. Installez-le avec: pip install pytest")
        return 1
    
    # Lancer les tests
    success = run_tests(args.test_type, args.verbose)
    
    if success:
        print("\n🎉 Tous les tests sont passés !")
        return 0
    else:
        print("\n❌ Certains tests ont échoué.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
