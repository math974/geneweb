#!/usr/bin/env python3
"""
Script pour exécuter toutes les commandes manquantes et atteindre 100% de couverture.

Ce script exécute automatiquement toutes les 89 commandes restantes
générées par analyze_missing_tests.py pour atteindre 100% de couverture.
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import List, Dict, Any


class RemainingCommandsExecutor:
    """Exécuteur des commandes manquantes pour atteindre 100% de couverture."""
    
    def __init__(self, base_name: str = "galichet"):
        """Initialise l'exécuteur."""
        self.base_name = base_name
        self.golden_dir = Path(f"test/golden/{base_name}")
        
        # Toutes les commandes manquantes restantes (89 commandes)
        self.remaining_commands = [
            # Tests de base manquants
            {"name": "Export raw seul", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--raw"]},
            {"name": "Export mem seul", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--mem"]},
            
            # Tests de sélection manquants
            {"name": "Ascendance 1 seul", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-a", "1"]},
            {"name": "Ascendance 2 seul", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-a", "2"]},
            {"name": "Ascendance 3 seul", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-a", "3"]},
            {"name": "Descendance 1 seul", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-d", "1"]},
            {"name": "Descendance 2 seul", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-d", "2"]},
            {"name": "Descendance 3 seul", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-d", "3"]},
            {"name": "Ascendance+Descendance 1 seul", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--ad", "1"]},
            {"name": "Ascendance+Descendance 2 seul", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--ad", "2"]},
            {"name": "Personnes isolées seul", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--isolated"]},
            
            # Tests de filtres manquants
            {"name": "Sans notes seul", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--nn"]},
            {"name": "Sans notes ni sources seul", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--nnn"]},
            
            # Tests de séparation manquants
            {"name": "Séparation par personne seul", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--sep", "Jean Pierre.0 Galichet"]},
            
            # Tests d'encodage manquants
            {"name": "Encodage ASCII seul", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--charset", "ASCII"]},
            {"name": "Encodage ANSEL seul", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--charset", "ANSEL"]},
            {"name": "Encodage ANSI seul", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--charset", "ANSI"]},
            {"name": "Encodage UTF-8 seul", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--charset", "UTF-8"]},
            
            # Tests de format manquants
            {"name": "Format old-gw seul", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--old-gw"]},
            
            # Tests de sélection par clé manquants
            {"name": "Sélection par clé 1 seul", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-k", "Jean Pierre.0 Galichet"]},
            {"name": "Sélection par clé 2 seul", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-k", "Jean Pierre.0 Galichet", "-k", "Marie Elisabeth.0 Loche"]},
            
            # Tests de combinaisons critiques (2 options) - Toutes les combinaisons manquantes
            {"name": "Ascendance 1 + Format old-gw", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-a", "1", "--old-gw"]},
            {"name": "Ascendance 2 + Format old-gw", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-a", "2", "--old-gw"]},
            {"name": "Ascendance 3 + Format old-gw", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-a", "3", "--old-gw"]},
            {"name": "Descendance 1 + Format old-gw", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-d", "1", "--old-gw"]},
            {"name": "Descendance 2 + Format old-gw", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-d", "2", "--old-gw"]},
            {"name": "Descendance 3 + Format old-gw", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-d", "3", "--old-gw"]},
            {"name": "Ascendance+Descendance 1 + Format old-gw", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--ad", "1", "--old-gw"]},
            {"name": "Ascendance+Descendance 2 + Format old-gw", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--ad", "2", "--old-gw"]},
            {"name": "Personnes isolées + Format old-gw", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--isolated", "--old-gw"]},
            
            # Tests de format + filtres
            {"name": "Format old-gw + Sans notes", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--old-gw", "--nn"]},
            {"name": "Format old-gw + Sans notes ni sources", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--old-gw", "--nnn"]},
            {"name": "Format raw + Sans notes", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--raw", "--nn"]},
            {"name": "Format mem + Sans notes", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--mem", "--nn"]},
            
            # Tests d'encodage + format
            {"name": "Encodage ASCII + Format old-gw", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--charset", "ASCII", "--old-gw"]},
            {"name": "Encodage ANSEL + Format old-gw", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--charset", "ANSEL", "--old-gw"]},
            {"name": "Encodage ANSI + Format old-gw", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--charset", "ANSI", "--old-gw"]},
            {"name": "Encodage UTF-8 + Format old-gw", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--charset", "UTF-8", "--old-gw"]},
            
            # Tests d'encodage + filtres
            {"name": "Encodage ASCII + Sans notes", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--charset", "ASCII", "--nn"]},
            {"name": "Encodage ANSEL + Sans notes", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--charset", "ANSEL", "--nn"]},
            {"name": "Encodage ANSI + Sans notes", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--charset", "ANSI", "--nn"]},
            {"name": "Encodage UTF-8 + Sans notes", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--charset", "UTF-8", "--nn"]},
            
            # Tests de sélection + format
            {"name": "Ascendance 1 + Sans notes", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-a", "1", "--nn"]},
            {"name": "Ascendance 2 + Sans notes", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-a", "2", "--nn"]},
            {"name": "Ascendance 3 + Sans notes", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-a", "3", "--nn"]},
            {"name": "Descendance 1 + Sans notes", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-d", "1", "--nn"]},
            {"name": "Descendance 2 + Sans notes", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-d", "2", "--nn"]},
            {"name": "Descendance 3 + Sans notes", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-d", "3", "--nn"]},
            {"name": "Ascendance+Descendance 1 + Sans notes", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--ad", "1", "--nn"]},
            {"name": "Ascendance+Descendance 2 + Sans notes", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--ad", "2", "--nn"]},
            {"name": "Personnes isolées + Sans notes", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--isolated", "--nn"]},
            
            # Tests de sélection + filtres
            {"name": "Ascendance 1 + Sans notes ni sources", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-a", "1", "--nnn"]},
            {"name": "Ascendance 2 + Sans notes ni sources", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-a", "2", "--nnn"]},
            {"name": "Ascendance 3 + Sans notes ni sources", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-a", "3", "--nnn"]},
            {"name": "Descendance 1 + Sans notes ni sources", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-d", "1", "--nnn"]},
            {"name": "Descendance 2 + Sans notes ni sources", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-d", "2", "--nnn"]},
            {"name": "Descendance 3 + Sans notes ni sources", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-d", "3", "--nnn"]},
            {"name": "Ascendance+Descendance 1 + Sans notes ni sources", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--ad", "1", "--nnn"]},
            {"name": "Ascendance+Descendance 2 + Sans notes ni sources", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--ad", "2", "--nnn"]},
            {"name": "Personnes isolées + Sans notes ni sources", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--isolated", "--nnn"]},
            
            # Tests de sélection par clé + autres options
            {"name": "Clé 1 + Ascendance 1", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-k", "Jean Pierre.0 Galichet", "-a", "1"]},
            {"name": "Clé 1 + Descendance 1", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-k", "Jean Pierre.0 Galichet", "-d", "1"]},
            {"name": "Clé 1 + Ascendance+Descendance 1", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-k", "Jean Pierre.0 Galichet", "--ad", "1"]},
            {"name": "Clé 1 + Sans notes", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-k", "Jean Pierre.0 Galichet", "--nn"]},
            {"name": "Clé 1 + Sans notes ni sources", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-k", "Jean Pierre.0 Galichet", "--nnn"]},
            {"name": "Clé 1 + Format old-gw", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-k", "Jean Pierre.0 Galichet", "--old-gw"]},
            
            # Tests de séparation + autres options
            {"name": "Séparation + Sans notes", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--sep", "Jean Pierre.0 Galichet", "--nn"]},
            {"name": "Séparation + Format old-gw", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--sep", "Jean Pierre.0 Galichet", "--old-gw"]},
            {"name": "Séparation + Encodage ASCII", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--sep", "Jean Pierre.0 Galichet", "--charset", "ASCII"]},
            
            # Tests de combinaisons complexes (3+ options) - Toutes les combinaisons manquantes
            {"name": "Ascendance 1 + Sans notes + Format old-gw", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-a", "1", "--nn", "--old-gw"]},
            {"name": "Descendance 1 + Sans notes + Format old-gw", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-d", "1", "--nn", "--old-gw"]},
            {"name": "Ascendance+Descendance 1 + Sans notes + Format old-gw", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--ad", "1", "--nn", "--old-gw"]},
            {"name": "Personnes isolées + Sans notes + Format old-gw", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--isolated", "--nn", "--old-gw"]},
            {"name": "Encodage ASCII + Sans notes + Format old-gw", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--charset", "ASCII", "--nn", "--old-gw"]},
            {"name": "Encodage ANSEL + Sans notes + Format old-gw", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--charset", "ANSEL", "--nn", "--old-gw"]},
            {"name": "Encodage ANSI + Sans notes + Format old-gw", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--charset", "ANSI", "--nn", "--old-gw"]},
            {"name": "Encodage UTF-8 + Sans notes + Format old-gw", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--charset", "UTF-8", "--nn", "--old-gw"]},
            
            # Tests de combinaisons très complexes (4+ options) - Toutes les combinaisons manquantes
            {"name": "Clé 1 + Ascendance 1 + Descendance 1 + Sans notes", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-k", "Jean Pierre.0 Galichet", "-a", "1", "-d", "1", "--nn"]},
            {"name": "Clé 1 + Ascendance+Descendance 2 + Sans notes ni sources", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "-k", "Jean Pierre.0 Galichet", "--ad", "2", "--nnn"]},
            {"name": "Personnes isolées + Sans notes + Sans sources + Format old-gw", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--isolated", "--nnn", "--old-gw"]},
            {"name": "Encodage ASCII + Sans notes + Format old-gw + Séparation", "cmd": ["python", "test/gwu_golden.py", "record", "--base", base_name, "--charset", "ASCII", "--nn", "--old-gw", "--sep", "Jean Pierre.0 Galichet"]},
        ]
    
    def execute_remaining_commands(self) -> None:
        """Exécute toutes les commandes manquantes pour atteindre 100% de couverture."""
        print(f"🚀 EXÉCUTION DES COMMANDES MANQUANTES POUR ATTEINDRE 100% DE COUVERTURE")
        print("=" * 80)
        print(f"📊 Total des commandes à exécuter: {len(self.remaining_commands)}")
        print("=" * 80)
        
        executed_count = 0
        failed_count = 0
        error_count = 0
        
        start_time = time.time()
        
        for i, command in enumerate(self.remaining_commands, 1):
            name = command["name"]
            cmd = command["cmd"]
            
            print(f"\n🔍 Commande {i:3d}/{len(self.remaining_commands)}: {name}")
            print(f"   Cmd: {' '.join(cmd)}")
            
            try:
                # Exécuter la commande
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
                
                if result.returncode == 0:
                    print(f"   ✅ SUCCÈS - Golden master créé")
                    executed_count += 1
                else:
                    print(f"   ❌ ÉCHEC - Code de sortie: {result.returncode}")
                    if result.stderr:
                        print(f"   Erreur: {result.stderr.strip()}")
                    failed_count += 1
                
            except Exception as e:
                print(f"   💥 ERREUR - {str(e)}")
                error_count += 1
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Afficher le résumé
        print(f"\n" + "=" * 80)
        print("📊 RÉSUMÉ DE L'EXÉCUTION DES COMMANDES MANQUANTES")
        print("=" * 80)
        print(f"Commandes exécutées avec succès: {executed_count}")
        print(f"Commandes échouées: {failed_count}")
        print(f"Commandes en erreur: {error_count}")
        print(f"Total des commandes: {len(self.remaining_commands)}")
        
        success_rate = (executed_count / len(self.remaining_commands)) * 100 if self.remaining_commands else 0
        print(f"Taux de succès: {success_rate:.1f}%")
        print(f"Durée totale: {duration:.1f} secondes")
        
        if executed_count > 0:
            print(f"\n✅ {executed_count} commandes exécutées avec succès !")
        
        if failed_count > 0:
            print(f"\n⚠️  {failed_count} commandes ont échoué. Vérifiez les erreurs ci-dessus.")
        
        if error_count > 0:
            print(f"\n💥 {error_count} commandes ont généré des erreurs.")
    
    def verify_complete_coverage(self) -> None:
        """Vérifie la couverture complète après exécution de toutes les commandes."""
        print(f"\n🔍 VÉRIFICATION DE LA COUVERTURE COMPLÈTE")
        print("=" * 60)
        
        # Compter les golden masters existants
        golden_files = list(self.golden_dir.glob("*.golden.gw"))
        golden_files = [f for f in golden_files if not f.name.endswith(".dir.golden.gw")]
        
        print(f"📊 Nombre total de golden masters: {len(golden_files)}")
        
        # Estimer la couverture
        estimated_coverage = (len(golden_files) / 217) * 100
        print(f"📈 Couverture estimée: {estimated_coverage:.1f}%")
        
        if estimated_coverage >= 100:
            print("🎉 COUVERTURE COMPLÈTE À 100% ! Tous les tests de régression sont créés !")
        elif estimated_coverage >= 90:
            print("✅ Excellente couverture ! Presque tous les tests sont créés.")
        elif estimated_coverage >= 80:
            print("⚠️  Bonne couverture, mais il reste quelques tests à créer.")
        else:
            print("❌ Couverture insuffisante, plus de tests nécessaires.")
        
        # Afficher quelques exemples
        print(f"\n📋 Exemples de golden masters créés:")
        for i, golden_file in enumerate(sorted(golden_files)[:20], 1):
            test_name = golden_file.stem.replace(f"{self.base_name}.", "")
            print(f"   {i:2d}. {test_name}")
        
        if len(golden_files) > 20:
            print(f"   ... et {len(golden_files) - 20} autres")
    
    def run_final_analysis(self) -> None:
        """Exécute l'analyse finale pour vérifier la couverture complète."""
        print(f"\n🔍 ANALYSE FINALE DE LA COUVERTURE")
        print("=" * 60)
        
        try:
            # Exécuter l'analyseur de tests manquants
            result = subprocess.run(
                ["python", "analyze_missing_tests.py"],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            
            if result.returncode == 0:
                print("✅ Analyse finale exécutée avec succès")
                print("\n📊 Résultats de l'analyse:")
                print(result.stdout)
            else:
                print("❌ Erreur lors de l'analyse finale")
                print(f"Erreur: {result.stderr}")
                
        except Exception as e:
            print(f"💥 Erreur lors de l'exécution de l'analyse finale: {str(e)}")


def main():
    """Fonction principale."""
    if len(sys.argv) > 1:
        base_name = sys.argv[1]
    else:
        base_name = "galichet"
    
    executor = RemainingCommandsExecutor(base_name)
    
    # Exécuter toutes les commandes manquantes
    executor.execute_remaining_commands()
    
    # Vérifier la couverture complète
    executor.verify_complete_coverage()
    
    # Exécuter l'analyse finale
    executor.run_final_analysis()


if __name__ == "__main__":
    main()
