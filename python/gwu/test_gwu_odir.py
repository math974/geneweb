import subprocess
import os
import shutil
import tempfile
import pytest

def test_gwu_odir():
    # Chemins vers les binaires gwu
    gwu_new = os.path.abspath("../../src/gw/gwu")
    gwu_old = os.path.abspath("../../src/gw/gwu.old")
    # Chemin vers une base de test (à adapter si besoin)
    base_file = os.path.abspath("../../examples/base.gwb")
    
    # Crée un dossier temporaire pour l'output
    with tempfile.TemporaryDirectory() as odir:
        # Exécute la commande avec le nouveau binaire
        result_new = subprocess.run(
            [gwu_new, "-odir", odir, base_file],
            capture_output=True, text=True
        )
        
        # Exécute la commande avec l'ancien binaire
        result_old = subprocess.run(
            [gwu_old, "-odir", odir, base_file],
            capture_output=True, text=True
        )
        
        print("=== NOUVEAU GWU ===")
        print("STDOUT:\n", result_new.stdout)
        print("STDERR:\n", result_new.stderr)
        
        print("\n=== ANCIEN GWU ===")
        print("STDOUT:\n", result_old.stdout)
        print("STDERR:\n", result_old.stderr)

        # Vérifie que les deux binaires s'exécutent correctement
        assert result_new.returncode == 0, f"Erreur avec le nouveau gwu: {result_new.stderr}"
        assert result_old.returncode == 0, f"Erreur avec l'ancien gwu: {result_old.stderr}"
        
        # Compare les outputs (on compare stderr car c'est là que l'output GWU est envoyé)
        assert result_new.stderr == result_old.stderr, "Les outputs des deux versions de gwu sont différents !"
        
        print("Test réussi ! Les deux versions produisent le même output.")
