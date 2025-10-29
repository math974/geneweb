#!/usr/bin/env python3
"""
Script pour assigner les tâches et organiser le projet GitHub
"""

import subprocess
import json
import sys

def run_command(cmd):
    """Exécute une commande et retourne le résultat"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def assign_issue(issue_number, assignee="math974"):
    """Assigne une issue à un utilisateur"""
    cmd = f"gh issue edit {issue_number} --add-assignee {assignee}"
    success, stdout, stderr = run_command(cmd)
    if success:
        print(f"✅ Issue #{issue_number} assignée à {assignee}")
    else:
        print(f"❌ Erreur assignation issue #{issue_number}: {stderr}")
    return success

def add_issue_to_project(issue_number):
    """Ajoute une issue au projet"""
    cmd = f"gh project item-add 1 --owner math974 --url https://github.com/math974/geneweb/issues/{issue_number}"
    success, stdout, stderr = run_command(cmd)
    if success:
        print(f"✅ Issue #{issue_number} ajoutée au projet")
    else:
        print(f"❌ Erreur ajout issue #{issue_number}: {stderr}")
    return success

def set_issue_status(issue_number, status="In Progress"):
    """Met à jour le statut d'une issue dans le projet"""
    # Récupérer l'ID de l'item du projet
    cmd = "gh project item-list 1 --owner math974 --format json"
    success, stdout, stderr = run_command(cmd)
    
    if not success:
        print(f"❌ Erreur récupération items: {stderr}")
        return False
    
    try:
        items = json.loads(stdout)
        item_id = None
        
        # Trouver l'item correspondant à l'issue
        for item in items.get('items', []):
            if item.get('content', {}).get('number') == issue_number:
                item_id = item.get('id')
                break
        
        if not item_id:
            print(f"❌ Item pour issue #{issue_number} non trouvé")
            return False
        
        # Mettre à jour le statut
        cmd = f"gh project item-edit {item_id} --field-id PVTSSF_lAHOA3c4wM4BECU0zg1x7ic --single-select-option-id 47fc9ee4"
        success, stdout, stderr = run_command(cmd)
        
        if success:
            print(f"✅ Issue #{issue_number} mise en statut '{status}'")
        else:
            print(f"❌ Erreur mise à jour statut issue #{issue_number}: {stderr}")
        
        return success
        
    except json.JSONDecodeError as e:
        print(f"❌ Erreur parsing JSON: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Organisation des tâches GitHub...")
    
    # Issues prioritaires (Phase 1)
    priority_issues = [40, 41, 43]
    
    # Issues moyennes (Phase 2)
    medium_issues = [42, 44, 45, 46, 49]
    
    # Issues basses (Phase 3)
    low_issues = [47, 48]
    
    print("\n📋 Phase 1 - Issues prioritaires (In Progress):")
    for issue in priority_issues:
        print(f"\n🔄 Traitement issue #{issue}...")
        assign_issue(issue)
        add_issue_to_project(issue)
        set_issue_status(issue, "In Progress")
    
    print("\n📋 Phase 2 - Issues moyennes (Todo):")
    for issue in medium_issues:
        print(f"\n🔄 Traitement issue #{issue}...")
        assign_issue(issue)
        add_issue_to_project(issue)
        set_issue_status(issue, "Todo")
    
    print("\n📋 Phase 3 - Issues basses (Todo):")
    for issue in low_issues:
        print(f"\n🔄 Traitement issue #{issue}...")
        assign_issue(issue)
        add_issue_to_project(issue)
        set_issue_status(issue, "Todo")
    
    print("\n✅ Organisation terminée !")
    print("\n📊 Résumé:")
    print(f"   🔴 Priorité HAUTE (In Progress): {len(priority_issues)} issues")
    print(f"   🟡 Priorité MOYENNE (Todo): {len(medium_issues)} issues")
    print(f"   🟢 Priorité BASSE (Todo): {len(low_issues)} issues")
    print(f"   📝 Total: {len(priority_issues) + len(medium_issues) + len(low_issues)} issues")

if __name__ == "__main__":
    main()

