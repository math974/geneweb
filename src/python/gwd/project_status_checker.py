#!/usr/bin/env python3
"""
Script pour vérifier l'état du projet GitHub et générer un rapport complet
"""

import subprocess
import json
import sys
from datetime import datetime

def run_command(cmd):
    """Exécute une commande et retourne le résultat"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_issues():
    """Vérifie les issues #40-49"""
    print("🔍 Vérification des issues #40-49...")
    
    issues_status = {}
    target_issues = list(range(40, 50))
    
    for issue in target_issues:
        cmd = f"gh issue view {issue} --json number,title,assignees,state,labels"
        success, stdout, stderr = run_command(cmd)
        
        if success:
            try:
                data = json.loads(stdout)
                issues_status[issue] = {
                    'exists': True,
                    'title': data.get('title', ''),
                    'assignees': [a.get('login', '') for a in data.get('assignees', [])],
                    'state': data.get('state', ''),
                    'labels': [l.get('name', '') for l in data.get('labels', [])]
                }
                print(f"✅ Issue #{issue}: {data.get('title', '')[:50]}...")
            except json.JSONDecodeError:
                issues_status[issue] = {'exists': False, 'error': 'JSON parsing failed'}
                print(f"❌ Issue #{issue}: Erreur parsing JSON")
        else:
            issues_status[issue] = {'exists': False, 'error': stderr}
            print(f"❌ Issue #{issue}: {stderr}")
    
    return issues_status

def check_branches():
    """Vérifie les branches correspondantes"""
    print("\n🔍 Vérification des branches...")
    
    branch_names = [
        'feature/domain-entities',
        'feature/authentication-system',
        'feature/use-cases-commands',
        'feature/database-adapter',
        'feature/web-adapter',
        'feature/robot-protection',
        'feature/infrastructure',
        'feature/cli-interface',
        'feature/templates-assets',
        'feature/testing-documentation'
    ]
    
    branches_status = {}
    
    for branch in branch_names:
        cmd = f"git branch -a | grep {branch}"
        success, stdout, stderr = run_command(cmd)
        
        if success and branch in stdout:
            branches_status[branch] = {'exists': True}
            print(f"✅ Branche {branch} existe")
        else:
            branches_status[branch] = {'exists': False}
            print(f"❌ Branche {branch} manquante")
    
    return branches_status

def check_project_items():
    """Vérifie les items du projet GitHub"""
    print("\n🔍 Vérification du projet GitHub...")
    
    cmd = "gh project item-list 1 --owner math974 --format json"
    success, stdout, stderr = run_command(cmd)
    
    if not success:
        print(f"❌ Erreur récupération projet: {stderr}")
        return {}
    
    try:
        data = json.loads(stdout)
        items = data.get('items', []) if isinstance(data, dict) else data
        
        print(f"📊 Total d'items dans le projet: {len(items)}")
        
        # Chercher les issues #40-49
        target_issues = list(range(40, 50))
        found_issues = []
        
        for item in items:
            if isinstance(item, dict):
                content = item.get('content', {})
                if content.get('type') == 'Issue':
                    issue_number = content.get('number')
                    if issue_number in target_issues:
                        found_issues.append(issue_number)
        
        print(f"✅ Issues #40-49 dans le projet: {len(found_issues)}/10")
        print(f"   Issues trouvées: {sorted(found_issues)}")
        
        missing = set(target_issues) - set(found_issues)
        if missing:
            print(f"⚠️ Issues manquantes: {sorted(missing)}")
        
        return {
            'total_items': len(items),
            'found_issues': found_issues,
            'missing_issues': list(missing)
        }
        
    except json.JSONDecodeError as e:
        print(f"❌ Erreur parsing JSON: {e}")
        return {}

def generate_report(issues_status, branches_status, project_status):
    """Génère un rapport complet"""
    print("\n" + "="*80)
    print("📊 RAPPORT COMPLET DU PROJET GENEWEB PYTHON")
    print("="*80)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Résumé des issues
    print("\n🔍 ÉTAT DES ISSUES #40-49:")
    print("-" * 50)
    
    existing_issues = [k for k, v in issues_status.items() if v.get('exists')]
    missing_issues = [k for k, v in issues_status.items() if not v.get('exists')]
    
    print(f"✅ Issues existantes: {len(existing_issues)}/10")
    print(f"❌ Issues manquantes: {len(missing_issues)}/10")
    
    if existing_issues:
        print(f"   Issues trouvées: {sorted(existing_issues)}")
    if missing_issues:
        print(f"   Issues manquantes: {sorted(missing_issues)}")
    
    # Résumé des branches
    print("\n🌿 ÉTAT DES BRANCHES:")
    print("-" * 50)
    
    existing_branches = [k for k, v in branches_status.items() if v.get('exists')]
    missing_branches = [k for k, v in branches_status.items() if not v.get('exists')]
    
    print(f"✅ Branches existantes: {len(existing_branches)}/10")
    print(f"❌ Branches manquantes: {len(missing_branches)}/10")
    
    if existing_branches:
        print(f"   Branches trouvées: {len(existing_branches)}")
    if missing_branches:
        print(f"   Branches manquantes: {len(missing_branches)}")
    
    # Résumé du projet
    print("\n📋 ÉTAT DU PROJET GITHUB:")
    print("-" * 50)
    
    if project_status:
        print(f"📊 Total d'items: {project_status.get('total_items', 0)}")
        print(f"✅ Issues #40-49 dans le projet: {len(project_status.get('found_issues', []))}/10")
        
        if project_status.get('missing_issues'):
            print(f"⚠️ Issues manquantes dans le projet: {project_status['missing_issues']}")
    
    # Recommandations
    print("\n💡 RECOMMANDATIONS:")
    print("-" * 50)
    
    if missing_issues:
        print("🔧 Actions requises pour les issues:")
        print("   1. Créer les issues manquantes")
        print("   2. Les assigner à math974")
        print("   3. Les ajouter au projet GitHub")
    
    if missing_branches:
        print("🔧 Actions requises pour les branches:")
        print("   1. Créer les branches manquantes")
        print("   2. Les pousser vers le repository")
    
    if project_status.get('missing_issues'):
        print("🔧 Actions requises pour le projet:")
        print("   1. Aller sur https://github.com/users/math974/projects/1")
        print("   2. Cliquer sur 'Add items'")
        print("   3. Ajouter les issues manquantes")
        print("   4. Organiser par priorité")
    
    # Liens utiles
    print("\n🔗 LIENS UTILES:")
    print("-" * 50)
    print("   📋 Projet GitHub: https://github.com/users/math974/projects/1")
    print("   🏠 Repository: https://github.com/math974/geneweb")
    print("   📝 Issues: https://github.com/math974/geneweb/issues")
    
    # Statut final
    print("\n🎯 STATUT FINAL:")
    print("-" * 50)
    
    issues_ok = len(existing_issues) == 10
    branches_ok = len(existing_branches) == 10
    project_ok = len(project_status.get('found_issues', [])) == 10
    
    if issues_ok and branches_ok and project_ok:
        print("🎉 PROJET PARFAITEMENT CONFIGURÉ !")
        print("   ✅ Toutes les issues existent")
        print("   ✅ Toutes les branches existent")
        print("   ✅ Toutes les issues sont dans le projet")
    else:
        print("⚠️ CONFIGURATION INCOMPLÈTE")
        if not issues_ok:
            print("   ❌ Issues manquantes")
        if not branches_ok:
            print("   ❌ Branches manquantes")
        if not project_ok:
            print("   ❌ Issues manquantes dans le projet")

def main():
    """Fonction principale"""
    print("🚀 Vérificateur de Projet GitHub - Geneweb Python")
    print("=" * 60)
    
    # Vérifications
    issues_status = check_issues()
    branches_status = check_branches()
    project_status = check_project_items()
    
    # Génération du rapport
    generate_report(issues_status, branches_status, project_status)

if __name__ == "__main__":
    main()

