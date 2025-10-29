# 🚀 Guide de Démarrage - GeneWeb GWD Python

## 👋 Bienvenue !

Ce document vous guide pour **démarrer le développement** du projet GeneWeb GWD Python.

## 📋 Documentation disponible

### 📘 Guides principaux

1. **`DEVELOPMENT_GUIDE.md`** - Guide complet de développement
   - Toutes les phases et issues
   - Critères de succès
   - Patterns à utiliser

2. **`PHASE_1_TASKS.md`** - Détails Phase 1 (Issues #40, #41, #43)
   - Domain Entities
   - Authentication System
   - Database Adapter

3. **`PHASE_2_3_4_TASKS.md`** - Détails Phases 2, 3, 4 (Issues #42-49)
   - Use Cases, Web Adapter, Robot Protection
   - Infrastructure, Testing
   - CLI, Templates

4. **`COMPLETE_DEVELOPMENT_PLAN.md`** - Plan complet avec branches
   - Liste de toutes les branches
   - Commandes Git exactes
   - Workflow complet

### 📐 Architecture

- **`ARCHITECTURE.md`** - Architecture du projet

## 🎯 Objectifs du projet

Implémenter **GeneWeb GWD** en Python avec :

- ✅ **10 issues** organisées par phases
- ✅ **20 lignes max** par fonction
- ✅ **Patterns de conception** (Strategy, Command, Repository, etc.)
- ✅ **Tests unitaires** complets
- ✅ **Format .msgpack** moderne

## 🏗️ Architecture

```
src/python/gwd/
├── domain/                    # 🎯 Cœur métier
│   ├── entities/             # Issue #40
│   │   ├── person.py
│   │   ├── family.py
│   │   └── base.py
│   ├── services/             # Issue #41
│   │   ├── auth_strategies.py
│   │   └── auth_factory.py
│   └── value_objects/
│       └── auth_result.py
│
├── use_cases/                # 🔄 Logique applicative
│   └── commands.py           # Issue #42
│
├── adapters/                  # 🔌 Interfaces
│   ├── web/                  # Issue #44
│   │   ├── fastapi_app.py
│   │   └── template_strategies.py
│   ├── database/             # Issue #43
│   │   └── base_repository.py
│   └── middleware/           # Issue #45
│       ├── robot_observer.py
│       └── middleware_chain.py
│
├── infrastructure/            # 🛠️ Services
│   ├── config.py             # Issue #46
│   └── server.py
│
├── cli/                       # 🖥️ Interface
│   └── main.py               # Issue #47
│
├── templates/                 # 📄 Templates
│   └── *.html                # Issue #48
│
└── static/                    # 🎨 Assets
    └── css/
        └── style.css
```

## 🚀 Démarrage rapide

### Étape 1 : Choisir une issue

Les issues sont organisées en **4 phases** :

| Phase | Issues | Priorité |
|-------|--------|----------|
| **1. Fondations** | #40, #41, #43 | 🔴 HIGH |
| **2. Logique métier** | #42, #44, #45 | 🟡 MEDIUM |
| **3. Infrastructure** | #46, #49 | 🟡 MEDIUM |
| **4. Interface** | #47, #48 | 🟢 LOW |

### Étape 2 : Basculer sur la branche

```bash
# Exemple : Issue #40
git checkout feature/domain-entities
git pull origin feature/domain-entities
```

### Étape 3 : Consulter les détails

Ouvrir le fichier approprié :
- **Phase 1** → `PHASE_1_TASKS.md`
- **Phases 2-4** → `PHASE_2_3_4_TASKS.md`

### Étape 4 : Développer

Suivre les TODOs dans les fichiers de tâches.

### Étape 5 : Tester

```bash
# Lancer les tests
pytest tests/

# Avec coverage
pytest --cov=src/python/gwd
```

### Étape 6 : Committer

```bash
git add .
git commit -m "feat: description du changement"
git push origin feature/nom-de-la-branche
```

## 📝 Exemple concret : Issue #40

### 1. Basculer sur la branche

```bash
git checkout feature/domain-entities
git pull origin feature/domain-entities
```

### 2. Ouvrir `PHASE_1_TASKS.md`

Section **Issue #40 : Domain Entities**

### 3. Ce qui existe déjà

- ✅ `person.py` est **déjà implémenté**

### 4. Ce qu'il faut faire

Créer/compléter :
- `family.py` ← **À créer**
- `base.py` ← **À créer**

### 5. Code à implémenter

Voir `PHASE_1_TASKS.md` - Section Issue #40 pour le code exact.

### 6. Tests

```bash
# Créer le fichier de tests
mkdir -p tests/test_domain
cat > tests/test_domain/test_entities.py << 'EOF'
# Voir PHASE_1_TASKS.md pour les tests
EOF

# Lancer les tests
pytest tests/test_domain/test_entities.py
```

### 7. Commit

```bash
git add src/python/gwd/domain/entities/
git add tests/test_domain/
git commit -m "feat(domain): complete entities implementation for #40"
git push origin feature/domain-entities
```

## 🎯 Contraintes à respecter

### ✅ 20 lignes max par fonction

```python
# ✅ BON
def get_person(self, person_id: int) -> Optional[Person]:
    """Obtenir une personne - MAX 20 LIGNES"""
    return self.persons.get(person_id)  # Simple et direct

# ❌ MAUVAIS
def get_person(self, person_id: int) -> Optional[Person]:
    """Obtenir une personne - TROP LONG"""
    if person_id is None:
        return None
    if person_id < 0:
        return None
    if person_id not in self.persons:
        return None
    person = self.persons[person_id]
    if person is None:
        return None
    return person  # Trop de conditions
```

### ✅ Utiliser les patterns

- **Strategy Pattern** pour l'authentification
- **Command Pattern** pour les use cases
- **Repository Pattern** pour la base de données
- **Observer Pattern** pour la protection robots
- **Factory Pattern** pour créer des objets

### ✅ Tests unitaires

```python
# Pour chaque fonction, créer un test
def test_get_person():
    """Test de la fonction get_person"""
    base = GenealogyBase(name="test")
    person = Person(1, "Jean", "Dupont")
    base.add_person(person)
    
    result = base.get_person(1)
    assert result is not None
    assert result.first_name == "Jean"
```

## 📊 État actuel

### ✅ Branches créées

Toutes les 10 branches sont déjà créées :

```bash
# Lister les branches
git branch -a | grep feature/

# Branches disponibles :
feature/authentication-system
feature/cli-interface
feature/database-adapter
feature/domain-entities
feature/infrastructure
feature/robot-protection
feature/templates-assets
feature/testing-documentation
feature/use-cases-commands
feature/web-adapter
```

### ✅ Issues GitHub

Toutes les 10 issues (#40-49) sont créées sur GitHub.

## 🎓 Ressources

### Documentation interne

- `ARCHITECTURE.md` - Architecture détaillée
- `DEVELOPMENT_GUIDE.md` - Guide de développement complet
- `PHASE_1_TASKS.md` - Tâches Phase 1
- `PHASE_2_3_4_TASKS.md` - Tâches Phases 2-4
- `TESTING_GUIDE.md` - Guide de tests

### Documentation externe

- [FastAPI](https://fastapi.tiangolo.com/)
- [Jinja2](https://jinja.palletsprojects.com/)
- [MessagePack](https://msgpack.org/)
- [Pytest](https://pytest.org/)

## 🚨 En cas de problème

### Branche divergente

```bash
# Mettre à jour la branche
git checkout feature/nom-branche
git pull origin feature/nom-branche

# Résoudre les conflits
git add .
git commit -m "fix: resolve conflicts"
git push origin feature/nom-branche
```

### Tests qui échouent

```bash
# Voir les détails
pytest -v tests/

# Avec output détaillé
pytest -vv --tb=short
```

### Questions ?

Consulter la documentation disponible dans ce dossier :
- Voir `COMPLETE_DEVELOPMENT_PLAN.md` pour le workflow complet
- Voir `PHASE_X_TASKS.md` pour les détails d'une phase
- Voir `ARCHITECTURE.md` pour comprendre l'architecture

## 🎉 Prochaines étapes

1. **Commencer par la Phase 1** (Issues #40, #41, #43)
2. **Consulter** `PHASE_1_TASKS.md` pour les détails
3. **Basculer** sur `feature/domain-entities`
4. **Développer** en suivant les TODOs
5. **Tester** avec pytest
6. **Committer** et pousser

**Bon développement ! 🚀**

