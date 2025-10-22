#!/usr/bin/env python3
"""
Script pour créer les tests de régression restants les plus importants.

Ce script se concentre sur les combinaisons restantes les plus critiques
pour atteindre une couverture de test optimale.
"""

import subprocess
import sys
from pathlib import Path


class RemainingTestCreator:
    """Créateur de tests restants importants."""
    
    def __init__(self, base_name: str = "galichet"):
        """Initialise le créateur."""
        self.base_name = base_name
        self.golden_dir = Path(f"test/golden/{base_name}")
        
        # Tests restants prioritaires (les plus importants)
        self.remaining_tests = [
            # Tests de base manquants
            {"name": "Export raw seul", "args": ["--raw"]},
            {"name": "Export mem seul", "args": ["--mem"]},
            
            # Tests de sélection manquants
            {"name": "Ascendance 1 seul", "args": ["-a", "1"]},
            {"name": "Ascendance 2 seul", "args": ["-a", "2"]},
            {"name": "Ascendance 3 seul", "args": ["-a", "3"]},
            {"name": "Descendance 1 seul", "args": ["-d", "1"]},
            {"name": "Descendance 2 seul", "args": ["-d", "2"]},
            {"name": "Descendance 3 seul", "args": ["-d", "3"]},
            {"name": "Ascendance+Descendance 1 seul", "args": ["--ad", "1"]},
            {"name": "Ascendance+Descendance 2 seul", "args": ["--ad", "2"]},
            {"name": "Personnes isolées seul", "args": ["--isolated"]},
            
            # Tests de filtres manquants
            {"name": "Sans notes seul", "args": ["--nn"]},
            {"name": "Sans notes ni sources seul", "args": ["--nnn"]},
            
            # Tests de séparation manquants
            {"name": "Séparation par personne seul", "args": ["--sep", "Jean Pierre.0 Galichet"]},
            
            # Tests d'encodage manquants
            {"name": "Encodage ASCII seul", "args": ["--charset", "ASCII"]},
            {"name": "Encodage ANSEL seul", "args": ["--charset", "ANSEL"]},
            {"name": "Encodage ANSI seul", "args": ["--charset", "ANSI"]},
            {"name": "Encodage UTF-8 seul", "args": ["--charset", "UTF-8"]},
            
            # Tests de format manquants
            {"name": "Format old-gw seul", "args": ["--old-gw"]},
            
            # Tests de sélection par clé manquants
            {"name": "Sélection par clé 1 seul", "args": ["-k", "Jean Pierre.0 Galichet"]},
            {"name": "Sélection par clé 2 seul", "args": ["-k", "Jean Pierre.0 Galichet", "-k", "Marie Elisabeth.0 Loche"]},
            
            # Tests de combinaisons critiques (2 options) - les plus importantes
            {"name": "Ascendance 1 + Format old-gw", "args": ["-a", "1", "--old-gw"]},
            {"name": "Ascendance 2 + Format old-gw", "args": ["-a", "2", "--old-gw"]},
            {"name": "Ascendance 3 + Format old-gw", "args": ["-a", "3", "--old-gw"]},
            {"name": "Descendance 1 + Format old-gw", "args": ["-d", "1", "--old-gw"]},
            {"name": "Descendance 2 + Format old-gw", "args": ["-d", "2", "--old-gw"]},
            {"name": "Descendance 3 + Format old-gw", "args": ["-d", "3", "--old-gw"]},
            {"name": "Ascendance+Descendance 1 + Format old-gw", "args": ["--ad", "1", "--old-gw"]},
            {"name": "Ascendance+Descendance 2 + Format old-gw", "args": ["--ad", "2", "--old-gw"]},
            {"name": "Personnes isolées + Format old-gw", "args": ["--isolated", "--old-gw"]},
            
            # Tests de format + filtres
            {"name": "Format old-gw + Sans notes", "args": ["--old-gw", "--nn"]},
            {"name": "Format old-gw + Sans notes ni sources", "args": ["--old-gw", "--nnn"]},
            {"name": "Format raw + Sans notes", "args": ["--raw", "--nn"]},
            {"name": "Format mem + Sans notes", "args": ["--mem", "--nn"]},
            
            # Tests d'encodage + format
            {"name": "Encodage ASCII + Format old-gw", "args": ["--charset", "ASCII", "--old-gw"]},
            {"name": "Encodage ANSEL + Format old-gw", "args": ["--charset", "ANSEL", "--old-gw"]},
            {"name": "Encodage ANSI + Format old-gw", "args": ["--charset", "ANSI", "--old-gw"]},
            {"name": "Encodage UTF-8 + Format old-gw", "args": ["--charset", "UTF-8", "--old-gw"]},
            
            # Tests d'encodage + filtres
            {"name": "Encodage ASCII + Sans notes", "args": ["--charset", "ASCII", "--nn"]},
            {"name": "Encodage ANSEL + Sans notes", "args": ["--charset", "ANSEL", "--nn"]},
            {"name": "Encodage ANSI + Sans notes", "args": ["--charset", "ANSI", "--nn"]},
            {"name": "Encodage UTF-8 + Sans notes", "args": ["--charset", "UTF-8", "--nn"]},
            
            # Tests de sélection + format
            {"name": "Ascendance 1 + Sans notes", "args": ["-a", "1", "--nn"]},
            {"name": "Ascendance 2 + Sans notes", "args": ["-a", "2", "--nn"]},
            {"name": "Ascendance 3 + Sans notes", "args": ["-a", "3", "--nn"]},
            {"name": "Descendance 1 + Sans notes", "args": ["-d", "1", "--nn"]},
            {"name": "Descendance 2 + Sans notes", "args": ["-d", "2", "--nn"]},
            {"name": "Descendance 3 + Sans notes", "args": ["-d", "3", "--nn"]},
            {"name": "Ascendance+Descendance 1 + Sans notes", "args": ["--ad", "1", "--nn"]},
            {"name": "Ascendance+Descendance 2 + Sans notes", "args": ["--ad", "2", "--nn"]},
            {"name": "Personnes isolées + Sans notes", "args": ["--isolated", "--nn"]},
            
            # Tests de sélection + filtres
            {"name": "Ascendance 1 + Sans notes ni sources", "args": ["-a", "1", "--nnn"]},
            {"name": "Ascendance 2 + Sans notes ni sources", "args": ["-a", "2", "--nnn"]},
            {"name": "Ascendance 3 + Sans notes ni sources", "args": ["-a", "3", "--nnn"]},
            {"name": "Descendance 1 + Sans notes ni sources", "args": ["-d", "1", "--nnn"]},
            {"name": "Descendance 2 + Sans notes ni sources", "args": ["-d", "2", "--nnn"]},
            {"name": "Descendance 3 + Sans notes ni sources", "args": ["-d", "3", "--nnn"]},
            {"name": "Ascendance+Descendance 1 + Sans notes ni sources", "args": ["--ad", "1", "--nnn"]},
            {"name": "Ascendance+Descendance 2 + Sans notes ni sources", "args": ["--ad", "2", "--nnn"]},
            {"name": "Personnes isolées + Sans notes ni sources", "args": ["--isolated", "--nnn"]},
            
            # Tests de sélection par clé + autres options
            {"name": "Clé 1 + Ascendance 1", "args": ["-k", "Jean Pierre.0 Galichet", "-a", "1"]},
            {"name": "Clé 1 + Descendance 1", "args": ["-k", "Jean Pierre.0 Galichet", "-d", "1"]},
            {"name": "Clé 1 + Ascendance+Descendance 1", "args": ["-k", "Jean Pierre.0 Galichet", "--ad", "1"]},
            {"name": "Clé 1 + Sans notes", "args": ["-k", "Jean Pierre.0 Galichet", "--nn"]},
            {"name": "Clé 1 + Sans notes ni sources", "args": ["-k", "Jean Pierre.0 Galichet", "--nnn"]},
            {"name": "Clé 1 + Format old-gw", "args": ["-k", "Jean Pierre.0 Galichet", "--old-gw"]},
            
            # Tests de séparation + autres options
            {"name": "Séparation + Sans notes", "args": ["--sep", "Jean Pierre.0 Galichet", "--nn"]},
            {"name": "Séparation + Format old-gw", "args": ["--sep", "Jean Pierre.0 Galichet", "--old-gw"]},
            {"name": "Séparation + Encodage ASCII", "args": ["--sep", "Jean Pierre.0 Galichet", "--charset", "ASCII"]},
            
            # Tests de combinaisons complexes (3+ options) - les plus importantes
            {"name": "Ascendance 1 + Sans notes + Format old-gw", "args": ["-a", "1", "--nn", "--old-gw"]},
            {"name": "Descendance 1 + Sans notes + Format old-gw", "args": ["-d", "1", "--nn", "--old-gw"]},
            {"name": "Ascendance+Descendance 1 + Sans notes + Format old-gw", "args": ["--ad", "1", "--nn", "--old-gw"]},
            {"name": "Personnes isolées + Sans notes + Format old-gw", "args": ["--isolated", "--nn", "--old-gw"]},
            {"name": "Encodage ASCII + Sans notes + Format old-gw", "args": ["--charset", "ASCII", "--nn", "--old-gw"]},
            {"name": "Encodage ANSEL + Sans notes + Format old-gw", "args": ["--charset", "ANSEL", "--nn", "--old-gw"]},
            {"name": "Encodage ANSI + Sans notes + Format old-gw", "args": ["--charset", "ANSI", "--nn", "--old-gw"]},
            {"name": "Encodage UTF-8 + Sans notes + Format old-gw", "args": ["--charset", "UTF-8", "--nn", "--old-gw"]},
            
            # Tests de combinaisons très complexes (4+ options) - les plus importantes
            {"name": "Clé 1 + Ascendance 1 + Descendance 1 + Sans notes", "args": ["-k", "Jean Pierre.0 Galichet", "-a", "1", "-d", "1", "--nn"]},
            {"name": "Clé 1 + Ascendance+Descendance 2 + Sans notes ni sources", "args": ["-k", "Jean Pierre.0 Galichet", "--ad", "2", "--nnn"]},
            {"name": "Personnes isolées + Sans notes + Sans sources + Format old-gw", "args": ["--isolated", "--nnn", "--old-gw"]},
            {"name": "Encodage ASCII + Sans notes + Format old-gw + Séparation", "args": ["--charset", "ASCII", "--nn", "--old-gw", "--sep", "Jean Pierre.0 Galichet"]},
        ]
    
    def create_remaining_tests(self) -> None:
        """Crée les tests restants importants."""
        print(f"🚀 CRÉATION DES TESTS RESTANTS IMPORTANTS POUR: {self.base_name}")
        print("=" * 70)
        
        created_count = 0
        failed_count = 0
        
        for i, test in enumerate(self.remaining_tests, 1):
            name = test["name"]
            args = test["args"]
            
            print(f"\n🔍 Test {i:2d}/{len(self.remaining_tests)}: {name}")
            print(f"   Args: {' '.join(args)}")
            
            try:
                # Construire la commande
                cmd = ["python", "test/gwu_golden.py", "record", "--base", self.base_name] + args
                
                # Exécuter la commande
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
                
                if result.returncode == 0:
                    print(f"   ✅ SUCCÈS - Golden master créé")
                    created_count += 1
                else:
                    print(f"   ❌ ÉCHEC - Code de sortie: {result.returncode}")
                    if result.stderr:
                        print(f"   Erreur: {result.stderr.strip()}")
                    failed_count += 1
                
            except Exception as e:
                print(f"   💥 ERREUR - {str(e)}")
                failed_count += 1
        
        # Afficher le résumé
        print(f"\n" + "=" * 70)
        print("📊 RÉSUMÉ DE LA CRÉATION DES TESTS RESTANTS")
        print("=" * 70)
        print(f"Tests créés avec succès: {created_count}")
        print(f"Tests échoués: {failed_count}")
        print(f"Total des tests: {len(self.remaining_tests)}")
        
        success_rate = (created_count / len(self.remaining_tests)) * 100 if self.remaining_tests else 0
        print(f"Taux de succès: {success_rate:.1f}%")
        
        if created_count > 0:
            print(f"\n✅ {created_count} tests restants créés avec succès !")
        
        if failed_count > 0:
            print(f"\n⚠️  {failed_count} tests ont échoué. Vérifiez les erreurs ci-dessus.")
    
    def verify_final_coverage(self) -> None:
        """Vérifie la couverture finale après création des tests."""
        print(f"\n🔍 VÉRIFICATION DE LA COUVERTURE FINALE")
        print("=" * 50)
        
        # Compter les golden masters existants
        golden_files = list(self.golden_dir.glob("*.golden.gw"))
        golden_files = [f for f in golden_files if not f.name.endswith(".dir.golden.gw")]
        
        print(f"📊 Nombre total de golden masters: {len(golden_files)}")
        
        # Afficher quelques exemples
        print(f"\n📋 Exemples de golden masters créés:")
        for i, golden_file in enumerate(sorted(golden_files)[:15], 1):
            test_name = golden_file.stem.replace(f"{self.base_name}.", "")
            print(f"   {i:2d}. {test_name}")
        
        if len(golden_files) > 15:
            print(f"   ... et {len(golden_files) - 15} autres")
        
        # Estimer la couverture
        estimated_coverage = (len(golden_files) / 217) * 100
        print(f"\n📈 Couverture estimée: {estimated_coverage:.1f}%")
        
        if estimated_coverage >= 80:
            print("✅ Excellente couverture des tests de régression !")
        elif estimated_coverage >= 60:
            print("⚠️  Bonne couverture, mais il reste des tests à créer.")
        else:
            print("❌ Couverture insuffisante, plus de tests nécessaires.")


def main():
    """Fonction principale."""
    if len(sys.argv) > 1:
        base_name = sys.argv[1]
    else:
        base_name = "galichet"
    
    creator = RemainingTestCreator(base_name)
    
    # Créer les tests restants
    creator.create_remaining_tests()
    
    # Vérifier la couverture finale
    creator.verify_final_coverage()


if __name__ == "__main__":
    main()
