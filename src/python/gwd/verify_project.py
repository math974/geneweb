#!/usr/bin/env python3
"""
Script pour vérifier et corriger l'état du projet GitHub
"""

import subprocess
import json
import time

def run_command(cmd):
    """Exécute une commande et retourne le résultat"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_issues_exist():
    """Vérifie que les issues #40-49 existent"""
    print("🔍 Vérification des issues #40-49...")
    
    for i in range(40, 50):
        cmd = f"gh issue view {i}"
        success, stdout, stderr = run_command(cmd)
        if success:
            print(f"✅ Issue #{i} existe")
        else:
            print(f"❌ Issue #{i} n'existe pas: {stderr}")
    
    return True

def check_project_items():
    """Vérifie les items du projet"""
    print("\n🔍 Vérification des items du projet...")
    
    cmd = "gh project item-list 1 --owner math974 --format json"
    success, stdout, stderr = run_command(cmd)
    
    if not success:
        print(f"❌ Erreur récupération items: {stderr}")
        return False
    
    try:
        data = json.loads(stdout)
        items = data.get('items', [])
        
        print(f"📊 Total items dans le projet: {len(items)}")
        
        # Chercher nos issues
        our_issues = []
        for item in items:
            content = item.get('content', {})
            if content.get('type') == 'Issue':
                number = content.get('number')
                if number and 40 <= number <= 49:
                    our_issues.append(number)
        
        print(f"🎯 Nos issues trouvées: {sorted(our_issues)}")
        
        missing = []
        for i in range(40, 50):
            if i not in our_issues:
                missing.append(i)
        
        if missing:
            print(f"❌ Issues manquantes: {missing}")
            return False
        else:
            print("✅ Toutes nos issues sont dans le projet!")
            return True
            
    except json.JSONDecodeError as e:
        print(f"❌ Erreur parsing JSON: {e}")
        return False

def add_missing_issues():
    """Ajoute les issues manquantes au projet"""
    print("\n➕ Ajout des issues manquantes...")
    
    for i in range(40, 50):
        cmd = f"gh project item-add 1 --owner math974 --url https://github.com/math974/geneweb/issues/{i}"
        success, stdout, stderr = run_command(cmd)
        if success:
            print(f"✅ Issue #{i} ajoutée")
        else:
            print(f"❌ Erreur ajout issue #{i}: {stderr}")
        
        # Petite pause pour éviter les limites de rate
        time.sleep(0.5)

def main():
    """Fonction principale"""
    print("🚀 Vérification du projet GitHub...")
    
    # 1. Vérifier que les issues existent
    check_issues_exist()
    
    # 2. Vérifier les items du projet
    if not check_project_items():
        print("\n🔄 Ajout des issues manquantes...")
        add_missing_issues()
        
        # Attendre un peu et revérifier
        print("\n⏳ Attente de synchronisation...")
        time.sleep(3)
        
        print("\n🔍 Vérification finale...")
        check_project_items()
    else:
        print("\n✅ Le projet est à jour!")

if __name__ == "__main__":
    main()

