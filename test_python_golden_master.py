#!/usr/bin/env python3
"""
Script de test Golden Master pour le binaire Python GWU.

Ce script teste le binaire Python contre tous les golden masters OCaml
pour vérifier la compatibilité complète.
"""

import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import List, Tuple, Dict, Any
import difflib

# Ajouter le chemin du module Python
sys.path.insert(0, 'geneweb-python/src')

from geneweb.gwu.cli.gwu_cli import GwuCLI


class GoldenMasterTester:
    """Testeur de Golden Master pour GWU Python."""
    
    def __init__(self, base_name: str = "galichet"):
        """Initialise le testeur."""
        self.base_name = base_name
        self.golden_dir = Path(f"test/golden/{base_name}")
        self.results: List[Dict[str, Any]] = []
        
    def test_all_scenarios(self) -> None:
        """Teste tous les scénarios de golden master."""
        print(f"🧪 TEST GOLDEN MASTER POUR LA BASE: {self.base_name}")
        print("=" * 60)
        
        # Scénarios de test
        scenarios = [
            # Tests de base
            {"name": "Export standard", "args": []},
            {"name": "Export avec --odir", "args": ["--odir", "test_output_dir"]},
            
            # Tests de sélection par clés
            {"name": "Sélection par clé (1)", "args": ["-k", "Jean Pierre.0 Galichet"]},
            {"name": "Sélection par clé (2)", "args": ["-k", "Jean Pierre.0 Galichet", "-k", "Marie Elisabeth.0 Loche"]},
            
            # Tests d'ascendance
            {"name": "Ascendance profondeur 1", "args": ["-a", "1"]},
            {"name": "Ascendance profondeur 2", "args": ["-a", "2"]},
            {"name": "Ascendance profondeur 3", "args": ["-a", "3"]},
            
            # Tests de descendance
            {"name": "Descendance profondeur 1", "args": ["-d", "1"]},
            {"name": "Descendance profondeur 2", "args": ["-d", "2"]},
            {"name": "Descendance profondeur 3", "args": ["-d", "3"]},
            
            # Tests combinés
            {"name": "Ascendance+Descendance 1", "args": ["-ad", "1"]},
            {"name": "Ascendance+Descendance 2", "args": ["-ad", "2"]},
            {"name": "Clé + Ascendance + Descendance", "args": ["-k", "Jean Pierre.0 Galichet", "-a", "2", "-d", "1"]},
            
            # Tests de filtres
            {"name": "Personnes isolées", "args": ["--isolated"]},
            {"name": "Sans notes", "args": ["--no-notes"]},
            {"name": "Sans notes ni sources", "args": ["--no-notes", "--no-src"]},
            
            # Tests de séparation
            {"name": "Séparation par personne", "args": ["--sep", "Jean Pierre.0 Galichet"]},
            
            # Tests d'encodage
            {"name": "Encodage ASCII", "args": ["-enc", "ASCII"]},
            {"name": "Encodage ANSEL", "args": ["-enc", "ANSEL"]},
            {"name": "Encodage ANSI", "args": ["-enc", "ANSI"]},
            
            # Tests de format
            {"name": "Format old-gw", "args": ["--old-gw"]},
            
            # Tests de combinaisons
            {"name": "Séparation + ASCII", "args": ["--sep", "Jean Pierre.0 Galichet", "-enc", "ASCII"]},
        ]
        
        # Exécuter tous les tests
        for scenario in scenarios:
            self._test_scenario(scenario)
        
        # Afficher le résumé
        self._print_summary()
    
    def _test_scenario(self, scenario: Dict[str, Any]) -> None:
        """Teste un scénario spécifique."""
        name = scenario["name"]
        args = scenario["args"]
        
        print(f"\n🔍 Test: {name}")
        print(f"   Args: {' '.join(args)}")
        
        try:
            # Créer un répertoire temporaire pour les tests
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Adapter les arguments pour le répertoire temporaire
                adapted_args = []
                for arg in args:
                    if arg == "test_output_dir":
                        adapted_args.append(str(temp_path / "output_dir"))
                    else:
                        adapted_args.append(arg)
                
                # Construire la commande complète
                full_args = [f"distribution/bases/{self.base_name}.gw"] + adapted_args
                
                # Ajouter -o seulement si pas d'odir
                if "--odir" not in adapted_args:
                    full_args.extend(["-o", str(temp_path / "output.gw")])
                
                # Exécuter le binaire Python
                cli = GwuCLI()
                result_code = cli.run(full_args)
                
                # Vérifier le résultat
                if "--odir" in adapted_args:
                    # Pour --odir, vérifier le répertoire de sortie
                    output_dir = temp_path / "output_dir"
                    success = result_code == 0 and output_dir.exists()
                    # Chercher le fichier .gw dans le répertoire
                    if success:
                        gw_files = list(output_dir.glob("*.gw"))
                        output_file = gw_files[0] if gw_files else None
                    else:
                        output_file = None
                else:
                    # Pour -o, vérifier le fichier de sortie
                    output_file = temp_path / "output.gw"
                    success = result_code == 0 and output_file.exists()
                
                if success and output_file and output_file.exists():
                    # Lire le contenu généré
                    generated_content = output_file.read_text(encoding='utf-8')
                    
                    # Comparer avec le golden master
                    golden_file = self._find_golden_file(args)
                    if golden_file and golden_file.exists():
                        golden_content = golden_file.read_text(encoding='utf-8')
                        is_identical = generated_content == golden_content
                        
                        if is_identical:
                            print(f"   ✅ SUCCÈS - Identique au golden master")
                            status = "SUCCESS"
                        else:
                            print(f"   ⚠️  DIFFÉRENCE - Contenu différent du golden master")
                            print(f"   📊 Taille généré: {len(generated_content)} chars")
                            print(f"   📊 Taille golden: {len(golden_content)} chars")
                            status = "DIFFERENT"
                    else:
                        print(f"   ❓ GOLDEN MANQUANT - Pas de golden master trouvé")
                        status = "NO_GOLDEN"
                else:
                    print(f"   ❌ ÉCHEC - Code de sortie: {result_code}")
                    status = "FAILED"
                
                # Enregistrer le résultat
                self.results.append({
                    "name": name,
                    "args": args,
                    "status": status,
                    "result_code": result_code,
                    "success": success
                })
                
        except Exception as e:
            print(f"   💥 ERREUR - {str(e)}")
            self.results.append({
                "name": name,
                "args": args,
                "status": "ERROR",
                "result_code": -1,
                "success": False,
                "error": str(e)
            })
    
    def _find_golden_file(self, args: List[str]) -> Path:
        """Trouve le fichier golden master correspondant aux arguments."""
        # Construire le nom de fichier golden
        filename_parts = [self.base_name]
        
        # Ajouter les suffixes selon les arguments
        if "-k" in args:
            key_count = args.count("-k")
            filename_parts.append(f"key-{key_count}")
        
        if "-a" in args:
            asc_idx = args.index("-a")
            if asc_idx + 1 < len(args):
                asc_val = args[asc_idx + 1]
                filename_parts.append(f"a{asc_val}")
        
        if "-d" in args:
            desc_idx = args.index("-d")
            if desc_idx + 1 < len(args):
                desc_val = args[desc_idx + 1]
                filename_parts.append(f"d{desc_val}")
        
        if "-ad" in args:
            ad_idx = args.index("-ad")
            if ad_idx + 1 < len(args):
                ad_val = args[ad_idx + 1]
                filename_parts.append(f"ad{ad_val}")
        
        if "--isolated" in args:
            filename_parts.append("isolated")
        
        if "--no-notes" in args:
            filename_parts.append("nn")
        
        if "--no-notes" in args and "--no-src" in args:
            filename_parts.append("nnn")
        
        if "--sep" in args:
            filename_parts.append("sep-1")
        
        if "-enc" in args:
            enc_idx = args.index("-enc")
            if enc_idx + 1 < len(args):
                enc_val = args[enc_idx + 1]
                filename_parts.append(f"charset-{enc_val}")
        
        if "--old-gw" in args:
            filename_parts.append("old_gw")
        
        
        # Construire le nom de fichier
        filename = ".".join(filename_parts) + ".golden.gw"
        golden_file = self.golden_dir / filename
        
        return golden_file
    
    def _print_summary(self) -> None:
        """Affiche le résumé des tests."""
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES TESTS GOLDEN MASTER")
        print("=" * 60)
        
        # Compter les résultats
        total = len(self.results)
        success = sum(1 for r in self.results if r["status"] == "SUCCESS")
        different = sum(1 for r in self.results if r["status"] == "DIFFERENT")
        no_golden = sum(1 for r in self.results if r["status"] == "NO_GOLDEN")
        failed = sum(1 for r in self.results if r["status"] == "FAILED")
        error = sum(1 for r in self.results if r["status"] == "ERROR")
        
        print(f"Total des tests: {total}")
        print(f"✅ Succès (identique): {success}")
        print(f"⚠️  Différent: {different}")
        print(f"❓ Golden manquant: {no_golden}")
        print(f"❌ Échec: {failed}")
        print(f"💥 Erreur: {error}")
        
        # Calculer le pourcentage de succès
        success_rate = (success / total) * 100 if total > 0 else 0
        print(f"\n🎯 Taux de succès: {success_rate:.1f}%")
        
        # Afficher les détails des échecs
        if different > 0 or failed > 0 or error > 0:
            print("\n🔍 DÉTAILS DES ÉCHECS:")
            for result in self.results:
                if result["status"] in ["DIFFERENT", "FAILED", "ERROR"]:
                    print(f"   - {result['name']}: {result['status']}")
                    if "error" in result:
                        print(f"     Erreur: {result['error']}")
        
        print("\n" + "=" * 60)


def main():
    """Fonction principale."""
    if len(sys.argv) > 1:
        base_name = sys.argv[1]
    else:
        base_name = "galichet"
    
    tester = GoldenMasterTester(base_name)
    tester.test_all_scenarios()


if __name__ == "__main__":
    main()
