#!/usr/bin/env python3
"""
Script pour étendre la couverture des tests de régression à d'autres bases de données.
"""

import subprocess
import os
import time
from pathlib import Path
from typing import List, Dict, Any

class CoverageExtender:
    """Extendeur de couverture pour les tests de régression GWU."""
    
    def __init__(self):
        """Initialise l'extendeur."""
        self.available_bases = self._discover_available_bases()
        self.base_tests = self._define_base_tests()
        self.selective_tests = self._define_selective_tests()
    
    def _discover_available_bases(self) -> List[str]:
        """Découvre les bases de données disponibles."""
        bases = []
        
        # Chercher dans distribution/bases/
        dist_bases = Path("distribution/bases")
        if dist_bases.exists():
            for gwb_dir in dist_bases.glob("*.gwb"):
                if gwb_dir.is_dir():
                    base_name = gwb_dir.stem
                    bases.append(base_name)
        
        # Chercher dans src/bases/
        src_bases = Path("src/bases")
        if src_bases.exists():
            for gwb_dir in src_bases.glob("*.gwb"):
                if gwb_dir.is_dir():
                    base_name = gwb_dir.stem
                    if base_name not in bases:
                        bases.append(base_name)
        
        return bases
    
    def _define_base_tests(self) -> List[Dict[str, Any]]:
        """Définit les tests de base pour chaque nouvelle base."""
        return [
            {"name": "standard", "args": []},
            {"name": "old_gw", "args": ["--old-gw"]},
            {"name": "raw", "args": ["--raw"]},
            {"name": "mem", "args": ["--mem"]},
            {"name": "nn", "args": ["--nn"]},
            {"name": "nnn", "args": ["--nnn"]},
            {"name": "isolated", "args": ["--isolated"]},
            {"name": "nopicture", "args": ["--nopicture"]},
            {"name": "source-TEST", "args": ["--source", "TEST"]},
            {"name": "s-Name", "args": ["-s", "Name"]},  # Sera adapté selon la base
            {"name": "c100", "args": ["-c", "100"]},
            {"name": "key-1", "args": ["-k", "KEY"]},  # Sera adapté selon la base
            {"name": "key-2", "args": ["-k", "KEY1", "-k", "KEY2"]},  # Sera adapté
            {"name": "sep-1", "args": ["--sep", "KEY"]},  # Sera adapté
            {"name": "charset-ASCII", "args": ["--charset", "ASCII"]},
            {"name": "charset-UTF-8", "args": ["--charset", "UTF-8"]},
        ]
    
    def _define_selective_tests(self) -> List[Dict[str, Any]]:
        """Définit les tests sélectifs pour les bases importantes."""
        return [
            # Tests d'encodage
            {"name": "charset-ANSEL", "args": ["--charset", "ANSEL"]},
            {"name": "charset-ANSI", "args": ["--charset", "ANSI"]},
            
            # Tests de sélection
            {"name": "a1", "args": ["-a", "1"]},
            {"name": "d1", "args": ["-d", "1"]},
            {"name": "ad1", "args": ["--ad", "1"]},
            
            # Tests de combinaisons
            {"name": "a1.nn", "args": ["-a", "1", "--nn"]},
            {"name": "d1.old_gw", "args": ["-d", "1", "--old-gw"]},
            {"name": "charset-UTF-8.isolated", "args": ["--charset", "UTF-8", "--isolated"]},
        ]
    
    def run_command(self, command: str, description: str) -> tuple[bool, str]:
        """Exécute une commande et retourne le résultat."""
        print(f"🔍 Test {description}: {command.split('--base ')[-1] if '--base' in command else command}")
        process = subprocess.run(command, shell=True, capture_output=True, text=True)
        if process.returncode == 0:
            print(f"   ✅ SUCCÈS - Golden master créé")
            return True, ""
        else:
            error_message = process.stderr.strip()
            print(f"   ❌ ÉCHEC - Code de sortie: {process.returncode}")
            print(f"   Erreur: {error_message}")
            return False, error_message
    
    def count_golden_masters(self, base_name: str) -> int:
        """Compte le nombre de golden masters pour une base."""
        golden_dir = Path(f"test/golden/{base_name}")
        if not golden_dir.exists():
            return 0
        return len(list(golden_dir.glob("*.golden.gw")))
    
    def get_sample_keys(self, base_name: str) -> tuple[str, str, str]:
        """Récupère des clés d'exemple pour une base."""
        # Pour l'instant, retourne des clés génériques
        # Dans une implémentation complète, on analyserait la base pour trouver des clés réelles
        return "Person.0 Name", "Person.1 Name", "Person.2 Name"
    
    def extend_base_coverage(self, base_name: str, test_level: str = "base") -> Dict[str, Any]:
        """Étend la couverture pour une base spécifique."""
        print(f"\n🚀 EXTENSION DE LA COUVERTURE POUR: {base_name}")
        print("=" * 60)
        
        # Vérifier si la base existe
        if base_name not in self.available_bases:
            print(f"❌ Base '{base_name}' non trouvée")
            return {"success": False, "error": f"Base '{base_name}' non trouvée"}
        
        # Compter les golden masters existants
        initial_count = self.count_golden_masters(base_name)
        print(f"📊 Golden masters existants: {initial_count}")
        
        # Déterminer les tests à exécuter
        if test_level == "base":
            tests_to_run = self.base_tests
        elif test_level == "selective":
            tests_to_run = self.base_tests + self.selective_tests
        else:
            tests_to_run = self.base_tests
        
        # Adapter les tests pour la base
        adapted_tests = []
        key1, key2, key3 = self.get_sample_keys(base_name)
        
        for test in tests_to_run:
            adapted_test = test.copy()
            adapted_args = []
            
            for arg in test["args"]:
                if arg == "KEY":
                    adapted_args.append(key1)
                elif arg == "KEY1":
                    adapted_args.append(key1)
                elif arg == "KEY2":
                    adapted_args.append(key2)
                elif arg == "Name":
                    adapted_args.append(base_name)  # Utiliser le nom de la base
                else:
                    adapted_args.append(arg)
            
            adapted_test["args"] = adapted_args
            adapted_tests.append(adapted_test)
        
        print(f"📊 Tests à exécuter: {len(adapted_tests)}")
        print("=" * 60)
        
        # Exécuter les tests
        successful_executions = 0
        failed_executions = 0
        start_time = time.time()
        
        for i, test in enumerate(adapted_tests):
            # Construire la commande
            cmd_parts = ["python", "test/gwu_golden.py", "record", "--base", base_name] + test["args"]
            command = " ".join(cmd_parts)
            
            description = f"{i+1}/{len(adapted_tests)}: {test['name']}"
            success, error_msg = self.run_command(command, description)
            
            if success:
                successful_executions += 1
            else:
                failed_executions += 1
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Compter les golden masters finaux
        final_count = self.count_golden_masters(base_name)
        new_golden_masters = final_count - initial_count
        
        print(f"\n📊 RÉSUMÉ POUR {base_name}")
        print("=" * 60)
        print(f"Tests exécutés avec succès: {successful_executions}")
        print(f"Tests échoués: {failed_executions}")
        print(f"Total des tests: {len(adapted_tests)}")
        print(f"Taux de succès: {successful_executions / len(adapted_tests) * 100:.1f}%")
        print(f"Durée totale: {total_duration:.1f} secondes")
        print(f"Golden masters créés: {new_golden_masters}")
        print(f"Golden masters totaux: {final_count}")
        
        return {
            "success": True,
            "base_name": base_name,
            "initial_count": initial_count,
            "final_count": final_count,
            "new_golden_masters": new_golden_masters,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "total_tests": len(adapted_tests),
            "duration": total_duration
        }
    
    def extend_all_bases(self, test_level: str = "base") -> Dict[str, Any]:
        """Étend la couverture pour toutes les bases disponibles."""
        print(f"🚀 EXTENSION DE LA COUVERTURE POUR TOUTES LES BASES")
        print("=" * 60)
        print(f"Bases disponibles: {', '.join(self.available_bases)}")
        print(f"Niveau de test: {test_level}")
        print("=" * 60)
        
        results = {}
        total_successful = 0
        total_failed = 0
        total_new_golden_masters = 0
        
        for base_name in self.available_bases:
            if base_name == "galichet":
                print(f"⏭️  Ignorant {base_name} (déjà testée)")
                continue
            
            result = self.extend_base_coverage(base_name, test_level)
            results[base_name] = result
            
            if result["success"]:
                total_successful += result["successful_executions"]
                total_failed += result["failed_executions"]
                total_new_golden_masters += result["new_golden_masters"]
        
        print(f"\n📊 RÉSUMÉ GLOBAL")
        print("=" * 60)
        print(f"Bases traitées: {len([r for r in results.values() if r['success']])}")
        print(f"Tests exécutés avec succès: {total_successful}")
        print(f"Tests échoués: {total_failed}")
        print(f"Golden masters créés: {total_new_golden_masters}")
        
        return {
            "results": results,
            "total_successful": total_successful,
            "total_failed": total_failed,
            "total_new_golden_masters": total_new_golden_masters
        }

def main():
    """Fonction principale."""
    extender = CoverageExtender()
    
    print("🔍 BASES DE DONNÉES DISPONIBLES")
    print("=" * 40)
    for i, base in enumerate(extender.available_bases, 1):
        count = extender.count_golden_masters(base)
        status = "✅ Testée" if count > 0 else "❌ Non testée"
        print(f"{i}. {base} - {count} golden masters - {status}")
    
    print(f"\n🎯 OPTIONS D'EXTENSION")
    print("=" * 40)
    print("1. Étendre pour toutes les bases (niveau base)")
    print("2. Étendre pour toutes les bases (niveau sélectif)")
    print("3. Étendre pour une base spécifique")
    print("4. Quitter")
    
    choice = input("\nChoisissez une option (1-4): ").strip()
    
    if choice == "1":
        extender.extend_all_bases("base")
    elif choice == "2":
        extender.extend_all_bases("selective")
    elif choice == "3":
        base_name = input("Nom de la base: ").strip()
        test_level = input("Niveau de test (base/selective): ").strip() or "base"
        extender.extend_base_coverage(base_name, test_level)
    elif choice == "4":
        print("Au revoir !")
    else:
        print("Option invalide")

if __name__ == "__main__":
    main()
