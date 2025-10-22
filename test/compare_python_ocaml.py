#!/usr/bin/env python3
"""
Script pour comparer les fichiers générés par Python et OCaml.

Ce script génère des fichiers avec les options -k et --sep
et compare les résultats entre Python et OCaml.
"""

import subprocess
import tempfile
from pathlib import Path
import difflib
import sys
from typing import List, Tuple, Dict


def run_python_gwu(base_path: str, options: List[str], output_path: Path) -> Tuple[bool, str]:
    """Exécute le binaire Python GWU."""
    cmd = [
        "python", "test/run_gwu_python.py",
        base_path
    ] + options + ["-o", str(output_path)]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stderr


def run_ocaml_gwu(base_path: str, options: List[str], output_path: Path) -> Tuple[bool, str]:
    """Exécute le binaire OCaml GWU."""
    cmd = [
        "distribution/gw/gwu",
        base_path
    ] + options + ["-o", str(output_path)]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stderr


def compare_files(file1: Path, file2: Path) -> Dict[str, any]:
    """Compare deux fichiers et retourne les différences."""
    if not file1.exists():
        return {"error": f"Fichier 1 non trouvé: {file1}"}
    if not file2.exists():
        return {"error": f"Fichier 2 non trouvé: {file2}"}
    
    content1 = file1.read_text()
    content2 = file2.read_text()
    
    lines1 = content1.splitlines()
    lines2 = content2.splitlines()
    
    # Différences ligne par ligne
    diff = list(difflib.unified_diff(lines1, lines2, fromfile=str(file1), tofile=str(file2)))
    
    return {
        "identical": len(diff) == 0,
        "size_diff": len(lines1) - len(lines2),
        "diff_lines": diff,
        "content1_length": len(content1),
        "content2_length": len(content2)
    }


def test_key_option():
    """Test de l'option -k."""
    print("=== Test de l'option -k ===")
    
    base_path = "distribution/bases/galichet.raw.golden.gw"
    test_keys = [
        "Jean Pierre.0 Galichet",
        "Marie Elisabeth.0 Loche",
        "Jean Charles.0 Galichet"
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        for key in test_keys:
            print(f"\nTest avec la clé: {key}")
            
            python_file = temp_path / f"python_{key.replace(' ', '_').replace('.', '_')}.gw"
            ocaml_file = temp_path / f"ocaml_{key.replace(' ', '_').replace('.', '_')}.gw"
            
            # Exécuter Python
            success, error = run_python_gwu(base_path, ["-k", key], python_file)
            if not success:
                print(f"❌ Erreur Python: {error}")
                continue
            print(f"✅ Python réussi: {python_file}")
            
            # Exécuter OCaml
            success, error = run_ocaml_gwu(base_path, ["-k", key], ocaml_file)
            if not success:
                print(f"❌ Erreur OCaml: {error}")
                continue
            print(f"✅ OCaml réussi: {ocaml_file}")
            
            # Comparer les fichiers
            comparison = compare_files(python_file, ocaml_file)
            if "error" in comparison:
                print(f"❌ {comparison['error']}")
                continue
            
            if comparison["identical"]:
                print("✅ Fichiers identiques")
            else:
                print(f"⚠️  Fichiers différents:")
                print(f"   - Taille Python: {comparison['content1_length']} caractères")
                print(f"   - Taille OCaml: {comparison['content2_length']} caractères")
                print(f"   - Différence de lignes: {comparison['size_diff']}")
                
                # Afficher les premières différences
                diff_lines = comparison['diff_lines'][:10]  # Limiter à 10 lignes
                if diff_lines:
                    print("   - Premières différences:")
                    for line in diff_lines:
                        print(f"     {line}")


def test_sep_option():
    """Test de l'option --sep."""
    print("\n=== Test de l'option --sep ===")
    
    base_path = "distribution/bases/galichet.raw.golden.gw"
    test_persons = [
        "Jean Pierre.0 Galichet",
        "Marie Elisabeth.0 Loche"
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        for person in test_persons:
            print(f"\nTest avec la personne: {person}")
            
            python_dir = temp_path / f"python_sep_{person.replace(' ', '_').replace('.', '_')}"
            ocaml_dir = temp_path / f"ocaml_sep_{person.replace(' ', '_').replace('.', '_')}"
            
            # Exécuter Python
            success, error = run_python_gwu(base_path, ["--sep", person, "--odir", str(python_dir)], Path("/dev/null"))
            if not success:
                print(f"❌ Erreur Python: {error}")
                continue
            print(f"✅ Python réussi: {python_dir}")
            
            # Exécuter OCaml
            success, error = run_ocaml_gwu(base_path, ["--sep", person, "--odir", str(ocaml_dir)], Path("/dev/null"))
            if not success:
                print(f"❌ Erreur OCaml: {error}")
                continue
            print(f"✅ OCaml réussi: {ocaml_dir}")
            
            # Comparer les répertoires
            python_files = list(python_dir.glob("*.gw")) if python_dir.exists() else []
            ocaml_files = list(ocaml_dir.glob("*.gw")) if ocaml_dir.exists() else []
            
            print(f"   - Fichiers Python: {len(python_files)}")
            print(f"   - Fichiers OCaml: {len(ocaml_files)}")
            
            if len(python_files) > 0 and len(ocaml_files) > 0:
                # Comparer le premier fichier
                comparison = compare_files(python_files[0], ocaml_files[0])
                if "error" in comparison:
                    print(f"❌ {comparison['error']}")
                elif comparison["identical"]:
                    print("✅ Premier fichier identique")
                else:
                    print(f"⚠️  Premier fichier différent:")
                    print(f"   - Taille Python: {comparison['content1_length']} caractères")
                    print(f"   - Taille OCaml: {comparison['content2_length']} caractères")


def test_combinations():
    """Test des combinaisons d'options."""
    print("\n=== Test des combinaisons ===")
    
    base_path = "distribution/bases/galichet.raw.golden.gw"
    test_key = "Jean Pierre.0 Galichet"
    
    combinations = [
        (["-k", test_key, "-nn"], "key_nn"),
        (["-k", test_key, "-nnn"], "key_nnn"),
        (["-k", test_key, "-mem"], "key_mem"),
        (["-k", test_key, "--old-gw"], "key_old_gw"),
        (["-k", test_key, "--raw"], "key_raw"),
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        for combo, name in combinations:
            print(f"\nTest de la combinaison: {' '.join(combo)}")
            
            python_file = temp_path / f"python_{name}.gw"
            ocaml_file = temp_path / f"ocaml_{name}.gw"
            
            # Exécuter Python
            success, error = run_python_gwu(base_path, combo, python_file)
            if not success:
                print(f"❌ Erreur Python: {error}")
                continue
            print(f"✅ Python réussi: {python_file}")
            
            # Exécuter OCaml
            success, error = run_ocaml_gwu(base_path, combo, ocaml_file)
            if not success:
                print(f"❌ Erreur OCaml: {error}")
                continue
            print(f"✅ OCaml réussi: {ocaml_file}")
            
            # Comparer les fichiers
            comparison = compare_files(python_file, ocaml_file)
            if "error" in comparison:
                print(f"❌ {comparison['error']}")
                continue
            
            if comparison["identical"]:
                print("✅ Fichiers identiques")
            else:
                print(f"⚠️  Fichiers différents:")
                print(f"   - Différence de taille: {comparison['size_diff']} lignes")


def main():
    """Fonction principale."""
    print("Comparaison Python vs OCaml pour les options -k et --sep")
    print("=" * 60)
    
    try:
        test_key_option()
        test_sep_option()
        test_combinations()
        
        print("\n" + "=" * 60)
        print("Comparaison terminée")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
