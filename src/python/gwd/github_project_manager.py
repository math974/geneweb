#!/usr/bin/env python3
"""
Script pour gérer les tâches GitHub Project et les lier aux issues et branches
"""

import subprocess
import json
import sys
import time
from typing import List, Dict, Optional

class GitHubProjectManager:
    def __init__(self, owner: str = "math974", project_id: str = "1"):
        self.owner = owner
        self.project_id = project_id
        self.project_url = f"https://github.com/users/{owner}/projects/{project_id}"
        
    def run_command(self, cmd: str) -> tuple[bool, str, str]:
        """Exécute une commande et retourne le résultat"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def get_project_fields(self) -> Dict[str, str]:
        """Récupère les champs du projet pour les IDs"""
        cmd = f"gh project view {self.project_id} --owner {self.owner} --format json"
        success, stdout, stderr = self.run_command(cmd)
        
        if not success:
            print(f"❌ Erreur récupération projet: {stderr}")
            return {}
        
        try:
            data = json.loads(stdout)
            fields = {}
            
            # Extraire les IDs des champs
            for field in data.get('fields', []):
                field_name = field.get('name', '')
                field_id = field.get('id', '')
                
                if field_name == 'Status':
                    fields['status_field_id'] = field_id
                elif field_name == 'Priority':
                    fields['priority_field_id'] = field_id
                elif field_name == 'Assignees':
                    fields['assignees_field_id'] = field_id
                    
            return fields
        except json.JSONDecodeError as e:
            print(f"❌ Erreur parsing JSON: {e}")
            return {}
    
    def get_status_options(self) -> Dict[str, str]:
        """Récupère les options de statut"""
        return {
            'Todo': '47fc9ee4',  # ID pour Todo
            'In Progress': '47fc9ee5',  # ID pour In Progress
            'Done': '47fc9ee6'  # ID pour Done
        }
    
    def get_priority_options(self) -> Dict[str, str]:
        """Récupère les options de priorité"""
        return {
            'High': '47fc9ee7',  # ID pour High
            'Medium': '47fc9ee8',  # ID pour Medium
            'Low': '47fc9ee9'  # ID pour Low
        }
    
    def add_issue_to_project(self, issue_number: int) -> bool:
        """Ajoute une issue au projet"""
        issue_url = f"https://github.com/{self.owner}/geneweb/issues/{issue_number}"
        cmd = f"gh project item-add {self.project_id} --owner {self.owner} --url {issue_url}"
        
        success, stdout, stderr = self.run_command(cmd)
        if success:
            print(f"✅ Issue #{issue_number} ajoutée au projet")
            return True
        else:
            print(f"❌ Erreur ajout issue #{issue_number}: {stderr}")
            return False
    
    def assign_issue(self, issue_number: int, assignee: str = "math974") -> bool:
        """Assigne une issue à un utilisateur"""
        cmd = f"gh issue edit {issue_number} --add-assignee {assignee}"
        success, stdout, stderr = self.run_command(cmd)
        
        if success:
            print(f"✅ Issue #{issue_number} assignée à {assignee}")
            return True
        else:
            print(f"❌ Erreur assignation issue #{issue_number}: {stderr}")
            return False
    
    def get_project_items(self) -> List[Dict]:
        """Récupère tous les items du projet"""
        cmd = f"gh project item-list {self.project_id} --owner {self.owner} --format json"
        success, stdout, stderr = self.run_command(cmd)
        
        if not success:
            print(f"❌ Erreur récupération items: {stderr}")
            return []
        
        try:
            return json.loads(stdout)
        except json.JSONDecodeError as e:
            print(f"❌ Erreur parsing JSON: {e}")
            return []
    
    def update_item_status(self, item_id: str, status: str) -> bool:
        """Met à jour le statut d'un item"""
        fields = self.get_project_fields()
        status_options = self.get_status_options()
        
        if 'status_field_id' not in fields:
            print("❌ Champ Status non trouvé")
            return False
        
        status_option_id = status_options.get(status)
        if not status_option_id:
            print(f"❌ Option de statut '{status}' non trouvée")
            return False
        
        cmd = f"gh project item-edit {item_id} --field-id {fields['status_field_id']} --single-select-option-id {status_option_id}"
        success, stdout, stderr = self.run_command(cmd)
        
        if success:
            print(f"✅ Statut mis à jour vers '{status}'")
            return True
        else:
            print(f"❌ Erreur mise à jour statut: {stderr}")
            return False
    
    def update_item_priority(self, item_id: str, priority: str) -> bool:
        """Met à jour la priorité d'un item"""
        fields = self.get_project_fields()
        priority_options = self.get_priority_options()
        
        if 'priority_field_id' not in fields:
            print("❌ Champ Priority non trouvé")
            return False
        
        priority_option_id = priority_options.get(priority)
        if not priority_option_id:
            print(f"❌ Option de priorité '{priority}' non trouvée")
            return False
        
        cmd = f"gh project item-edit {item_id} --field-id {fields['priority_field_id']} --single-select-option-id {priority_option_id}"
        success, stdout, stderr = self.run_command(cmd)
        
        if success:
            print(f"✅ Priorité mise à jour vers '{priority}'")
            return True
        else:
            print(f"❌ Erreur mise à jour priorité: {stderr}")
            return False
    
    def organize_tasks(self):
        """Organise toutes les tâches selon les priorités"""
        print("🚀 Organisation des tâches GitHub Project...")
        
        # Configuration des tâches par priorité
        tasks_config = {
            # Priorité HAUTE (In Progress)
            'high_priority': {
                'issues': [40, 41, 43],
                'status': 'In Progress',
                'priority': 'High',
                'description': '🔴 PRIORITÉ HAUTE - Fondations du projet'
            },
            # Priorité MOYENNE (Todo)
            'medium_priority': {
                'issues': [42, 44, 45, 46, 49],
                'status': 'Todo',
                'priority': 'Medium',
                'description': '🟡 PRIORITÉ MOYENNE - Logique métier'
            },
            # Priorité BASSE (Todo)
            'low_priority': {
                'issues': [47, 48],
                'status': 'Todo',
                'priority': 'Low',
                'description': '🟢 PRIORITÉ BASSE - Interface utilisateur'
            }
        }
        
        # Traitement par priorité
        for priority_level, config in tasks_config.items():
            print(f"\n📋 {config['description']}")
            print(f"   Issues: {config['issues']}")
            print(f"   Statut: {config['status']}")
            print(f"   Priorité: {config['priority']}")
            
            for issue_number in config['issues']:
                print(f"\n🔄 Traitement issue #{issue_number}...")
                
                # 1. Assigner l'issue
                self.assign_issue(issue_number)
                
                # 2. Ajouter au projet
                if self.add_issue_to_project(issue_number):
                    # Attendre un peu pour que l'item soit créé
                    time.sleep(2)
                    
                    # 3. Récupérer l'ID de l'item
                    items = self.get_project_items()
                    item_id = None
                    
                    for item in items:
                        content = item.get('content', {})
                        if content.get('number') == issue_number:
                            item_id = item.get('id')
                            break
                    
                    if item_id:
                        # 4. Mettre à jour le statut
                        self.update_item_status(item_id, config['status'])
                        
                        # 5. Mettre à jour la priorité
                        self.update_item_priority(item_id, config['priority'])
                        
                        print(f"✅ Issue #{issue_number} complètement configurée")
                    else:
                        print(f"⚠️ Item pour issue #{issue_number} non trouvé dans le projet")
                else:
                    print(f"❌ Impossible d'ajouter l'issue #{issue_number} au projet")
        
        print("\n✅ Organisation terminée !")
        self.print_summary()
    
    def print_summary(self):
        """Affiche un résumé de l'organisation"""
        print("\n📊 Résumé de l'organisation:")
        print("=" * 50)
        
        # Récupérer les items du projet
        items = self.get_project_items()
        
        high_count = 0
        medium_count = 0
        low_count = 0
        
        for item in items:
            content = item.get('content', {})
            if content.get('number') in [40, 41, 42, 43, 44, 45, 46, 47, 48, 49]:
                # Vérifier la priorité (simplifié)
                if content.get('number') in [40, 41, 43]:
                    high_count += 1
                elif content.get('number') in [42, 44, 45, 46, 49]:
                    medium_count += 1
                else:
                    low_count += 1
        
        print(f"🔴 Priorité HAUTE (In Progress): {high_count} issues")
        print(f"🟡 Priorité MOYENNE (Todo): {medium_count} issues")
        print(f"🟢 Priorité BASSE (Todo): {low_count} issues")
        print(f"📝 Total organisé: {high_count + medium_count + low_count} issues")
        
        print(f"\n🔗 Liens utiles:")
        print(f"   Projet GitHub: {self.project_url}")
        print(f"   Repository: https://github.com/{self.owner}/geneweb")
    
    def verify_sync(self):
        """Vérifie que tout est synchronisé"""
        print("🔍 Vérification de la synchronisation...")
        
        # Vérifier les issues assignées
        cmd = f"gh issue list --assignee {self.owner} --state open --limit 20"
        success, stdout, stderr = self.run_command(cmd)
        
        if success:
            print("✅ Issues assignées récupérées")
            print(stdout)
        else:
            print(f"❌ Erreur récupération issues: {stderr}")
        
        # Vérifier les items du projet
        items = self.get_project_items()
        print(f"\n📊 Items dans le projet: {len(items)}")
        
        # Compter les issues #40-49
        target_issues = [40, 41, 42, 43, 44, 45, 46, 47, 48, 49]
        found_issues = []
        
        for item in items:
            content = item.get('content', {})
            issue_number = content.get('number')
            if issue_number in target_issues:
                found_issues.append(issue_number)
        
        print(f"✅ Issues #40-49 trouvées dans le projet: {len(found_issues)}/10")
        print(f"   Issues trouvées: {sorted(found_issues)}")
        
        missing = set(target_issues) - set(found_issues)
        if missing:
            print(f"⚠️ Issues manquantes: {sorted(missing)}")
        else:
            print("🎉 Toutes les issues sont synchronisées !")

def main():
    """Fonction principale"""
    print("🚀 Gestionnaire de Projet GitHub - Geneweb Python")
    print("=" * 60)
    
    manager = GitHubProjectManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "organize":
            manager.organize_tasks()
        elif command == "verify":
            manager.verify_sync()
        elif command == "summary":
            manager.print_summary()
        else:
            print(f"❌ Commande inconnue: {command}")
            print("Commandes disponibles: organize, verify, summary")
    else:
        # Par défaut, organiser les tâches
        manager.organize_tasks()

if __name__ == "__main__":
    main()

