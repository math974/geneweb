import subprocess
import os
import shutil
import tempfile
import pytest

#pytest test_gwu_odir.py -v -s

# Tableau des commandes à tester
TEST_COMMANDS = [
    {
        "name": "test_odir",
        "args": ["-odir", "OUTPUT_DIR"],
        "description": "Test de l'option -odir"
    },
    # Ajouter d'autres commandes ici si besoin
    # {
    #     "name": "test_raw", 
    #     "args": ["-raw"],
    #     "description": "Test de l'option -raw"
    # },
]

@pytest.mark.parametrize("command", TEST_COMMANDS, ids=lambda cmd: cmd["name"])
def test_gwu_commands(command):
    """Test générique pour comparer les outputs entre gwu et gwu.old"""
    # Chemins vers les binaires gwu
    gwu_new = os.path.abspath("../../src/gw/gwu")
    gwu_old = os.path.abspath("../../src/gw/gwu.old")
    # Chemin vers une base de test
    base_file = os.path.abspath("../../examples/base.gwb")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Prépare les arguments en remplaçant OUTPUT_DIR par le vrai chemin
        args = []
        for arg in command["args"]:
            if arg == "OUTPUT_DIR":
                args.append(temp_dir)
            else:
                args.append(arg)
        
        # Commandes complètes
        cmd_new = [gwu_new] + args + [base_file]
        cmd_old = [gwu_old] + args + [base_file]
        
        print(f"\n=== Test: {command['description']} ===")
        print(f"Commande testée: {' '.join(args)}")
        
        # Exécute le nouveau binaire
        result_new = subprocess.run(cmd_new, capture_output=True, text=True)
        
        # Exécute l'ancien binaire
        result_old = subprocess.run(cmd_old, capture_output=True, text=True)
        
        # Affiche les résultats pour debug
        print(f"\n--- NOUVEAU GWU (return code: {result_new.returncode}) ---")
        if result_new.stdout:
            print(f"STDOUT:\n{result_new.stdout}")
        if result_new.stderr:
            print(f"STDERR:\n{result_new.stderr}")
        
        print(f"\n--- ANCIEN GWU (return code: {result_old.returncode}) ---")
        if result_old.stdout:
            print(f"STDOUT:\n{result_old.stdout}")
        if result_old.stderr:
            print(f"STDERR:\n{result_old.stderr}")
        
        # Vérifications
        assert result_new.returncode == result_old.returncode, \
            f"Les codes de retour diffèrent: nouveau={result_new.returncode}, ancien={result_old.returncode}"
        
        assert result_new.stdout == result_old.stdout, \
            f"STDOUT différent!\nNouveau:\n{result_new.stdout}\nAncien:\n{result_old.stdout}"
        
        assert result_new.stderr == result_old.stderr, \
            f"STDERR différent!\nNouveau:\n{result_new.stderr}\nAncien:\n{result_old.stderr}"
        
        print(f"Test réussi pour {command['name']}: les deux versions produisent le même output.")
