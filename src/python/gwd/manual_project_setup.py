#!/usr/bin/env python3
"""
Script pour ajouter manuellement les issues au projet GitHub
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

def check_issue_exists(issue_number):
    """Vérifie si une issue existe"""
    cmd = f"gh issue view {issue_number}"
    success, stdout, stderr = run_command(cmd)
    return success

def add_issue_to_project_manual(issue_number):
    """Ajoute une issue au projet avec plusieurs tentatives"""
    print(f"\n🔄 Ajout manuel de l'issue #{issue_number}...")
    
    # Méthode 1: URL directe
    issue_url = f"https://github.com/math974/geneweb/issues/{issue_number}"
    cmd = f"gh project item-add 1 --owner math974 --url {issue_url}"
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print(f"✅ Issue #{issue_number} ajoutée (méthode URL)")
        return True
    else:
        print(f"❌ Méthode URL échouée: {stderr}")
    
    # Méthode 2: ID de l'issue
    cmd = f"gh issue view {issue_number} --json id"
    success, stdout, stderr = run_command(cmd)
    
    if success:
        try:
            data = json.loads(stdout)
            issue_id = data.get('id')
            if issue_id:
                cmd = f"gh project item-add 1 --owner math974 --id {issue_id}"
                success, stdout, stderr = run_command(cmd)
                
                if success:
                    print(f"✅ Issue #{issue_number} ajoutée (méthode ID)")
                    return True
                else:
                    print(f"❌ Méthode ID échouée: {stderr}")
        except json.JSONDecodeError:
            print(f"❌ Erreur parsing JSON pour issue #{issue_number}")
    
    return False

def main():
    """Fonction principale"""
    print("🚀 Ajout manuel des issues au projet GitHub...")
    print("=" * 60)
    
    # Issues à ajouter
    issues = list(range(40, 50))
    
    print(f"📋 Issues à ajouter: {issues}")
    
    # Vérifier que les issues existent
    print("\n🔍 Vérification des issues...")
    existing_issues = []
    for issue in issues:
        if check_issue_exists(issue):
            existing_issues.append(issue)
            print(f"✅ Issue #{issue} existe")
        else:
            print(f"❌ Issue #{issue} n'existe pas")
    
    print(f"\n📊 Issues existantes: {len(existing_issues)}/{len(issues)}")
    
    if not existing_issues:
        print("❌ Aucune issue à ajouter")
        return
    
    # Ajouter les issues au projet
    print(f"\n🔄 Ajout des issues au projet...")
    added_count = 0
    
    for issue in existing_issues:
        if add_issue_to_project_manual(issue):
            added_count += 1
        time.sleep(2)  # Pause entre les ajouts
    
    print(f"\n✅ Ajout terminé: {added_count}/{len(existing_issues)} issues ajoutées")
    
    # Vérification finale
    print("\n🔍 Vérification finale...")
    cmd = "gh project item-list 1 --owner math974 --format json"
    success, stdout, stderr = run_command(cmd)
    
    if success:
        try:
            data = json.loads(stdout)
            items = data.get('items', []) if isinstance(data, dict) else data
            
            print(f"📊 Total d'items dans le projet: {len(items)}")
            
            # Chercher les issues #40-49
            found_issues = []
            for item in items:
                if isinstance(item, dict):
                    content = item.get('content', {})
                    if content.get('type') == 'Issue':
                        issue_number = content.get('number')
                        if issue_number in issues:
                            found_issues.append(issue_number)
            
            print(f"✅ Issues #40-49 trouvées: {len(found_issues)}")
            print(f"   Issues trouvées: {sorted(found_issues)}")
            
            missing = set(issues) - set(found_issues)
            if missing:
                print(f"⚠️ Issues manquantes: {sorted(missing)}")
                print("\n💡 Solution recommandée:")
                print("   1. Aller sur https://github.com/users/math974/projects/1")
                print("   2. Cliquer sur 'Add items'")
                print("   3. Rechercher et ajouter les issues manquantes")
            else:
                print("🎉 Toutes les issues sont dans le projet !")
                
        except json.JSONDecodeError as e:
            print(f"❌ Erreur parsing JSON: {e}")
    else:
        print(f"❌ Erreur vérification: {stderr}")

if __name__ == "__main__":
    main()

