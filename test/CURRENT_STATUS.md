# État actuel des tests GWD - Golden Master

## ✅ Statut actuel : FONCTIONNEL

**Date** : Octobre 2025  
**Tests passants** : 22/25 (88%)  
**Couverture options gwd** : 8/36 (22%)

---

## 📊 Tests existants

### Tests de base (8 scénarios) ✅
| # | Scénario | Description | Statut |
|---|----------|-------------|--------|
| 1 | `homepage` | Page d'accueil | ✅ OK |
| 2 | `person_by_name` | Personne par nom/prénom | ✅ OK |
| 3 | `person_not_found` | Personne inexistante | ✅ OK |
| 4 | `search` | Recherche par nom | ✅ OK |
| 5 | `statistics` | Page de statistiques | ✅ OK |
| 6 | `surnames_alpha` | Liste noms alphabétique | ✅ OK |
| 7 | `surnames_freq` | Liste noms par fréquence | ✅ OK |
| 8 | `firstnames_alpha` | Liste prénoms alphabétique | ✅ OK |

### Tests d'arbres (6 scénarios) ✅
| # | Scénario | Description | Statut |
|---|----------|-------------|--------|
| 9 | `ancestors_tree` | Arbre des ancêtres | ✅ OK |
| 10 | `ancestors_table` | Tableau des ancêtres | ✅ OK |
| 11 | `ancestors_vertical` | Ancêtres vertical | ✅ OK |
| 12 | `ancestors_compact` | Ancêtres compact | ✅ OK |
| 13 | `descendants` | Arbre des descendants | ✅ OK |
| 14 | `descendants_vertical` | Descendants vertical | ✅ OK |

### Tests de personnes (4 scénarios) ✅
| # | Scénario | Description | Statut |
|---|----------|-------------|--------|
| 15 | `person_details` | Fiche détaillée personne | ✅ OK |
| 16 | `person_relations` | Relations d'une personne | ✅ OK |
| 17 | `person_chronology` | Chronologie personne | ✅ OK |
| 18 | `person_family` | Famille d'une personne | ✅ OK |

### Tests de listes (4 scénarios) ✅
| # | Scénario | Description | Statut |
|---|----------|-------------|--------|
| 19 | `list_recent_births` | Naissances récentes | ✅ OK |
| 20 | `list_recent_deaths` | Décès récents | ✅ OK |
| 21 | `list_recent_marriages` | Mariages récents | ✅ OK |
| 22 | `list_oldest` | Plus âgés | ✅ OK |

### Tests admin (3 scénarios) ⚠️
| # | Scénario | Description | Statut |
|---|----------|-------------|--------|
| 23 | `welcome` | Page accueil wizard | ⚠️ Golden manquant |
| 24 | `add_individual` | Formulaire ajout individu | ⚠️ Golden manquant |
| 25 | `add_family` | Formulaire ajout famille | ⚠️ Golden manquant |

---

## 🎯 Tests à implémenter (priorité)

### Priorité HAUTE

#### 1. Langues et internationalisation (5 scénarios)
Commande : `./test/gwd_test.sh record i18n`

```python
SCENARIO_SETS["i18n"] = [
    {
        "name": "lang_fr",
        "params": {},
        "gwd_options": {"lang": "fr"},
        "description": "Page d'accueil en français",
    },
    {
        "name": "lang_en",
        "params": {},
        "gwd_options": {"lang": "en"},
        "description": "Page d'accueil en anglais",
    },
    {
        "name": "lang_de",
        "params": {},
        "gwd_options": {"lang": "de"},
        "description": "Page d'accueil en allemand",
    },
    {
        "name": "blang_fr",
        "params": {},
        "gwd_options": {"blang": True},
        "headers": {"Accept-Language": "fr-FR,fr;q=0.9"},
        "description": "Détection langue navigateur FR",
    },
    {
        "name": "blang_en",
        "params": {},
        "gwd_options": {"blang": True},
        "headers": {"Accept-Language": "en-US,en;q=0.9"},
        "description": "Détection langue navigateur EN",
    },
]
```

#### 2. Authentification et sécurité (6 scénarios)
Commande : `./test/gwd_test.sh record auth`

```python
SCENARIO_SETS["auth"] = [
    {
        "name": "auth_no_credentials",
        "params": {},
        "gwd_options": {"auth_file": "fixtures/gwd_auth.txt"},
        "expect_status": 401,
        "description": "Accès sans authentification",
    },
    {
        "name": "auth_valid_user",
        "params": {},
        "gwd_options": {"auth_file": "fixtures/gwd_auth.txt"},
        "credentials": {"username": "testuser", "password": "testpass"},
        "expect_status": 200,
        "description": "Accès avec credentials valides",
    },
    {
        "name": "auth_invalid_password",
        "params": {},
        "gwd_options": {"auth_file": "fixtures/gwd_auth.txt"},
        "credentials": {"username": "testuser", "password": "wrong"},
        "expect_status": 401,
        "description": "Accès avec mauvais mot de passe",
    },
    {
        "name": "auth_friend_password",
        "params": {},
        "gwd_options": {"friend_passwd": "friendpass"},
        "credentials": {"username": "friend", "password": "friendpass"},
        "expect_status": 200,
        "description": "Accès avec mot de passe ami",
    },
    {
        "name": "auth_wizard_password",
        "params": {"m": "CONN_WIZ"},
        "gwd_options": {"wizard_passwd": "wizardpass"},
        "credentials": {"username": "wizard", "password": "wizardpass"},
        "description": "Accès wizard",
    },
    {
        "name": "auth_wjf_mode",
        "params": {"m": "CONN_WIZ"},
        "gwd_options": {
            "wizard_passwd": "wizpass",
            "friend_passwd": "wizpass",
            "wjf": True
        },
        "credentials": {"username": "friend", "password": "wizpass"},
        "description": "Wizard Just Friend mode",
    },
]
```

### Priorité MOYENNE

#### 3. Interface et liens (3 scénarios)
Commande : `./test/gwd_test.sh record interface`

```python
SCENARIO_SETS["interface"] = [
    {
        "name": "setup_link_enabled",
        "params": {},
        "gwd_options": {"setup_link": True},
        "description": "Lien gwsetup visible",
    },
    {
        "name": "images_custom_url",
        "params": {},
        "gwd_options": {"images_url": "http://cdn.example.com/gw-images"},
        "description": "URLs d'images personnalisées",
    },
    {
        "name": "allowed_tags_restricted",
        "params": {},
        "gwd_options": {"allowed_tags": "fixtures/allowed_tags.txt"},
        "description": "Tags HTML restreints",
    },
]
```

---

## 🚀 Commandes rapides

### Tests actuels
```bash
# Tous les tests existants (quick)
./test/gwd_test.sh quick

# Tous les tests existants (full)
./test/gwd_test.sh full

# Tests basiques
./test/gwd_test.sh verify basic

# Tests des arbres
./test/gwd_test.sh verify trees
```

### Créer les golden masters manquants
```bash
# Admin (golden manquants)
./test/gwd_test.sh record admin

# Langues (à créer)
./test/gwd_test.sh record i18n

# Authentification (à créer)
./test/gwd_test.sh record auth

# Interface (à créer)
./test/gwd_test.sh record interface
```

---

## 📋 Fichiers de configuration créés

### ✅ Déjà créés
- `test/fixtures/gwd_auth.txt` - Fichier d'autorisation
- `test/fixtures/allowed_tags.txt` - Tags HTML autorisés

### 🔜 À créer
- `test/fixtures/custom_lexicon.txt` - Lexique personnalisé (optionnel)
- `test/fixtures/images/` - Répertoire d'images personnalisé (optionnel)

---

## 🎓 Prochaines étapes recommandées

### Étape 1 : Compléter les tests admin (5 min)
```bash
./test/gwd_test.sh record admin
./test/gwd_test.sh verify admin
```

### Étape 2 : Implémenter les tests de langues (30 min)
1. Modifier `gwd_golden.py` pour supporter `-lang` et `-blang`
2. Ajouter les scénarios i18n
3. Enregistrer les golden masters
4. Vérifier les tests

### Étape 3 : Implémenter les tests d'authentification (45 min)
1. Modifier `gwd_golden.py` pour supporter les options d'auth
2. Ajouter les scénarios auth
3. Enregistrer les golden masters
4. Vérifier les tests

### Étape 4 : Implémenter les tests d'interface (20 min)
1. Modifier `gwd_golden.py` pour supporter setup_link, images_url, allowed_tags
2. Ajouter les scénarios interface
3. Enregistrer les golden masters
4. Vérifier les tests

---

## 📊 Objectif final

**Après implémentation complète :**
- 🎯 45+ scénarios de test
- 🎯 23/36 options gwd couvertes (64%)
- 🎯 ~80% des fonctionnalités visibles testées
- 🎯 Temps d'exécution : ~2-3 minutes

---

## ✅ Validation

**Commande de validation complète :**
```bash
# Lancer tous les tests
./test/gwd_test.sh full

# Devrait afficher :
# ✓ XX/XX scénarios conformes aux golden masters
```

**Commande de validation rapide :**
```bash
# Tests de base uniquement
./test/gwd_test.sh quick

# Devrait afficher :
# ✓ 8/8 scénarios conformes aux golden masters
```
