# 📋 Instructions pour Configurer le Projet GitHub

## 🎯 Objectif
Organiser les tâches du projet "Geneweb python" avec les issues #40-49 et leurs branches correspondantes.

## ✅ État Actuel

### **Issues Créées et Assignées**
- ✅ **10 issues** (#40-49) créées avec succès
- ✅ **Toutes assignées** à `math974`
- ✅ **Toutes ouvertes** et prêtes

### **Branches Créées**
- ✅ **10 branches** correspondantes créées et poussées
- ✅ **Noms cohérents** avec les issues

## 🔧 Configuration Manuelle Requise

### **Étape 1: Ajouter les Issues au Projet**

1. **Aller sur le projet GitHub** : https://github.com/users/math974/projects/1
2. **Cliquer sur "Add items"** (bouton en haut à droite)
3. **Rechercher et ajouter** les issues suivantes une par une :

#### **🔴 PRIORITÉ HAUTE (In Progress)**
| Issue | Titre | Branche | Action |
|-------|-------|---------|--------|
| #40 | Domain Entities | `feature/domain-entities` | Ajouter + Déplacer vers "In Progress" |
| #41 | Authentication System | `feature/authentication-system` | Ajouter + Déplacer vers "In Progress" |
| #43 | Database Adapter | `feature/database-adapter` | Ajouter + Déplacer vers "In Progress" |

#### **🟡 PRIORITÉ MOYENNE (Todo)**
| Issue | Titre | Branche | Action |
|-------|-------|---------|--------|
| #42 | Use Cases Commands | `feature/use-cases-commands` | Ajouter + Laisser en "Todo" |
| #44 | Web Adapter | `feature/web-adapter` | Ajouter + Laisser en "Todo" |
| #45 | Robot Protection | `feature/robot-protection` | Ajouter + Laisser en "Todo" |
| #46 | Infrastructure | `feature/infrastructure` | Ajouter + Laisser en "Todo" |
| #49 | Testing Documentation | `feature/testing-documentation` | Ajouter + Laisser en "Todo" |

#### **🟢 PRIORITÉ BASSE (Todo)**
| Issue | Titre | Branche | Action |
|-------|-------|---------|--------|
| #47 | CLI Interface | `feature/cli-interface` | Ajouter + Laisser en "Todo" |
| #48 | Templates Assets | `feature/templates-assets` | Ajouter + Laisser en "Todo" |

### **Étape 2: Organiser par Priorité**

#### **Colonnes du Projet**
1. **Todo** - Issues #42, #44, #45, #46, #47, #48, #49
2. **In Progress** - Issues #40, #41, #43
3. **Done** - (vide pour l'instant)

#### **Champs à Configurer**
- **Priority** : High (issues #40, #41, #43), Medium (issues #42, #44, #45, #46, #49), Low (issues #47, #48)
- **Assignees** : math974 (déjà configuré)
- **Labels** : enhancement (déjà configuré)

## 🔗 Liens Utiles

### **Projet GitHub**
- **URL** : https://github.com/users/math974/projects/1
- **Repository** : https://github.com/math974/geneweb

### **Issues à Ajouter**
- **Liste complète** : https://github.com/math974/geneweb/issues?q=is%3Aopen+is%3Aissue+label%3Aenhancement
- **Issues #40-49** : https://github.com/math974/geneweb/issues/40, #41, #42, #43, #44, #45, #46, #47, #48, #49

### **Branches Correspondantes**
```bash
# Vérifier les branches
git branch -a | grep feature/

# Branches à vérifier :
feature/domain-entities
feature/authentication-system
feature/use-cases-commands
feature/database-adapter
feature/web-adapter
feature/robot-protection
feature/infrastructure
feature/cli-interface
feature/templates-assets
feature/testing-documentation
```

## 📊 Workflow de Développement

### **Phase 1 - Fondations (À commencer maintenant)**
```bash
# 1. Domain Entities (base de tout)
git checkout feature/domain-entities
# Développer Person, Family, GenealogyBase

# 2. Authentication System (sécurité)
git checkout feature/authentication-system  
# Développer Basic/Digest Auth

# 3. Database Adapter (données)
git checkout feature/database-adapter
# Développer MessagePack adapter
```

### **Phase 2 - Logique métier**
```bash
# 4. Use Cases Commands
git checkout feature/use-cases-commands

# 5. Web Adapter
git checkout feature/web-adapter

# 6. Robot Protection
git checkout feature/robot-protection
```

### **Phase 3 - Infrastructure**
```bash
# 7. Infrastructure
git checkout feature/infrastructure

# 8. Testing Documentation
git checkout feature/testing-documentation
```

### **Phase 4 - Interface utilisateur**
```bash
# 9. CLI Interface
git checkout feature/cli-interface

# 10. Templates Assets
git checkout feature/templates-assets
```

## 🎯 Résultat Attendu

### **Projet GitHub Organisé**
- **43+ items** au total (30 existants + 10 nouvelles issues)
- **3 issues** en "In Progress" (priorité haute)
- **7 issues** en "Todo" (priorité moyenne/basse)
- **Toutes assignées** à math974
- **Priorités définies** (High/Medium/Low)

### **Synchronisation Complète**
- ✅ Issues #40-49 dans le projet
- ✅ Branches correspondantes créées
- ✅ Assignations configurées
- ✅ Priorités organisées
- ✅ Workflow de développement défini

## 🚀 Commandes Utiles

```bash
# Voir les issues assignées
gh issue list --assignee math974

# Voir le statut du projet
gh project view 1 --owner math974

# Travailler sur une issue
git checkout feature/domain-entities
# ... développement ...
git add . && git commit -m "feat: implement domain entities"
git push
```

## 📝 Notes Importantes

1. **Ajout manuel requis** : L'API GitHub CLI a des limitations pour l'ajout automatique d'items au projet
2. **Interface web recommandée** : Utiliser l'interface web GitHub pour ajouter les issues
3. **Organisation par priorité** : Respecter l'ordre des priorités pour le développement
4. **Branches synchronisées** : Toutes les branches sont déjà créées et poussées
5. **Assignations complètes** : Toutes les issues sont assignées à math974

**Une fois la configuration manuelle terminée, le projet sera parfaitement organisé ! 🎉**

