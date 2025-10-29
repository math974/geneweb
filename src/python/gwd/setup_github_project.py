#!/usr/bin/env python3
"""
Script simplifié pour configurer le projet GitHub avec les tâches
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

def assign_and_add_issue(issue_number, assignee="math974"):
    """Assigne une issue et l'ajoute au projet"""
    print(f"\n🔄 Traitement issue #{issue_number}...")
    
    # 1. Assigner l'issue
    cmd = f"gh issue edit {issue_number} --add-assignee {assignee}"
    success, stdout, stderr = run_command(cmd)
    if success:
        print(f"✅ Issue #{issue_number} assignée à {assignee}")
    else:
        print(f"❌ Erreur assignation issue #{issue_number}: {stderr}")
        return False
    
    # 2. Ajouter au projet
    issue_url = f"https://github.com/math974/geneweb/issues/{issue_number}"
    cmd = f"gh project item-add 1 --owner math974 --url {issue_url}"
    success, stdout, stderr = run_command(cmd)
    if success:
        print(f"✅ Issue #{issue_number} ajoutée au projet")
        return True
    else:
        print(f"❌ Erreur ajout issue #{issue_number}: {stderr}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Configuration du projet GitHub...")
    print("=" * 50)
    
    # Configuration des tâches par priorité
    high_priority = [40, 41, 43]  # Domain Entities, Auth, Database
    medium_priority = [42, 44, 45, 46, 49]  # Use Cases, Web, Robot, Infra, Testing
    low_priority = [47, 48]  # CLI, Templates
    
    print("\n🔴 PRIORITÉ HAUTE - Fondations du projet")
    print("   Issues: Domain Entities (#40), Authentication (#41), Database (#43)")
    for issue in high_priority:
        assign_and_add_issue(issue)
        time.sleep(1)  # Pause pour éviter les limites de rate
    
    print("\n🟡 PRIORITÉ MOYENNE - Logique métier")
    print("   Issues: Use Cases (#42), Web (#44), Robot (#45), Infra (#46), Testing (#49)")
    for issue in medium_priority:
        assign_and_add_issue(issue)
        time.sleep(1)
    
    print("\n🟢 PRIORITÉ BASSE - Interface utilisateur")
    print("   Issues: CLI (#47), Templates (#48)")
    for issue in low_priority:
        assign_and_add_issue(issue)
        time.sleep(1)
    
    print("\n✅ Configuration terminée !")
    print("\n📊 Résumé:")
    print(f"   🔴 Priorité HAUTE: {len(high_priority)} issues")
    print(f"   🟡 Priorité MOYENNE: {len(medium_priority)} issues")
    print(f"   🟢 Priorité BASSE: {len(low_priority)} issues")
    print(f"   📝 Total: {len(high_priority) + len(medium_priority) + len(low_priority)} issues")
    
    print(f"\n🔗 Liens utiles:")
    print(f"   Projet GitHub: https://github.com/users/math974/projects/1")
    print(f"   Repository: https://github.com/math974/geneweb")
    
    # Vérification finale
    print("\n🔍 Vérification...")
    cmd = "gh project item-list 1 --owner math974 --format json"
    success, stdout, stderr = run_command(cmd)
    
    if success:
        try:
            data = json.loads(stdout)
            items = data.get('items', []) if isinstance(data, dict) else data
            print(f"📊 Items dans le projet: {len(items)}")
            
            # Compter les issues #40-49
            target_issues = list(range(40, 50))
            found_issues = []
            
            for item in items:
                if isinstance(item, dict):
                    content = item.get('content', {})
                    issue_number = content.get('number')
                    if issue_number in target_issues:
                        found_issues.append(issue_number)
            
            print(f"✅ Issues #40-49 trouvées: {len(found_issues)}/10")
            if len(found_issues) == 10:
                print("🎉 Toutes les issues sont synchronisées !")
            else:
                missing = set(target_issues) - set(found_issues)
                print(f"⚠️ Issues manquantes: {sorted(missing)}")
                
        except json.JSONDecodeError as e:
            print(f"❌ Erreur parsing JSON: {e}")
    else:
        print(f"❌ Erreur vérification: {stderr}")

if __name__ == "__main__":
    main()
