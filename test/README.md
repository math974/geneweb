# Tests Golden Master pour GeneWeb

**Infrastructure de tests de non-régression pour `gwd` (serveur web) et `gwu` (utilitaire d'export)**

---

## 🚀 Démarrage rapide

### Test rapide (30 secondes)
```bash
./test/gwd_test.sh quick
```

### Test complet (2 minutes)
```bash
./test/gwd_test.sh full
```

### Statut actuel
✅ **25 scénarios de test**  
✅ **100% de réussite**  
✅ **8 options gwd couvertes**

---

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Tests GWD](#tests-gwd)
3. [Tests GWU](#tests-gwu)
4. [Documentation](#documentation)
5. [Prochaines étapes](#prochaines-étapes)

---

## 🎯 Vue d'ensemble

### Qu'est-ce qu'un Golden Master ?

Un **Golden Master** (ou test de régression par capture) est une technique de test qui :
1. Capture la sortie actuelle d'un programme (le "golden master")
2. Compare les sorties futures avec cette référence
3. Détecte automatiquement tout changement non intentionnel

### Architecture des tests

```
test/
├── gwd_golden.py          # Tests du serveur web gwd
├── gwd_test.sh            # Wrapper shell pour gwd
├── gwu_golden.py          # Tests de l'utilitaire gwu
├── gwu_test.sh            # Wrapper shell pour gwu
├── golden/                # Golden masters de référence
│   ├── gwd/              # 25 fichiers HTML (gwd)
│   └── gwu/              # Fichiers GW (gwu)
├── fixtures/              # Fichiers de configuration
│   ├── gwd_auth.txt      # Authentification
│   └── allowed_tags.txt  # Tags HTML
└── [Documentation]        # Voir ci-dessous
```

---

## 🌐 Tests GWD (Serveur Web)

### Scénarios disponibles (25 tests)

#### Tests de base (8)
- `homepage` - Page d'accueil
- `person_by_name` - Recherche personne
- `person_not_found` - Personne inexistante
- `search` - Recherche
- `statistics` - Statistiques
- `surnames_alpha` - Noms alphabétique
- `surnames_freq` - Noms par fréquence
- `firstnames_alpha` - Prénoms

#### Tests d'arbres (6)
- `ancestors_tree` - Arbre ancêtres
- `ancestors_table` - Tableau ancêtres
- `ancestors_vertical` - Ancêtres vertical
- `ancestors_compact` - Ancêtres compact
- `descendants` - Descendants
- `descendants_vertical` - Descendants vertical

#### Tests de personnes (4)
- `person_details` - Fiche détaillée
- `person_relations` - Relations
- `person_chronology` - Chronologie
- `person_family` - Famille

#### Tests de listes (4)
- `list_recent_births` - Naissances récentes
- `list_recent_deaths` - Décès récents
- `list_recent_marriages` - Mariages récents
- `list_oldest` - Plus âgés

#### Tests admin (3)
- `welcome` - Page wizard
- `add_individual` - Ajout individu
- `add_family` - Ajout famille

### Commandes

```bash
# Tests complets
./test/gwd_test.sh full

# Tests rapides (basic uniquement)
./test/gwd_test.sh quick

# Tests par catégorie
./test/gwd_test.sh verify basic
./test/gwd_test.sh verify trees
./test/gwd_test.sh verify person
./test/gwd_test.sh verify lists
./test/gwd_test.sh verify admin

# Enregistrement de golden masters
./test/gwd_test.sh record basic
./test/gwd_test.sh record all
```

### Options gwd testées

| Option | Utilisation | Catégorie |
|--------|-------------|-----------|
| `-p <PORT>` | Port serveur | Base |
| `-bd <DIR>` | Répertoire bases | Base |
| `-hd <DIR>` | Répertoire templates | Base |
| `-log <FILE>` | Fichier log | Base |
| `-conn_tmout <SEC>` | Timeout connexion | Base |
| `-robot_xcl <N>,<S>` | Exclusion robots | Base |
| `-n_workers <N>` | Nombre de workers | Base |
| `-predictable_mode` | Mode prédictible | Test |

**À venir** : `-lang`, `-blang`, `-auth`, `-friend`, `-wizard`, `-setup_link`, etc.

---

## 📤 Tests GWU (Utilitaire Export)

### Scénarios disponibles

Le script `gwu_golden.py` teste les différentes options d'export :
- Export complet GW
- Export avec filtres
- Formats de sortie

### Commandes

```bash
# Lancer les tests gwu
./test/gwu_test.sh verify

# Enregistrer les golden masters
./test/gwu_test.sh record
```

---

## 📚 Documentation

### Documents disponibles

| Fichier | Description |
|---------|-------------|
| **[SUMMARY.md](SUMMARY.md)** | 📊 **Résumé complet** de l'état actuel |
| **[CURRENT_STATUS.md](CURRENT_STATUS.md)** | 📈 État détaillé et prochaines étapes |
| **[GWD_OPTIONS_COVERAGE.md](GWD_OPTIONS_COVERAGE.md)** | 🎯 Couverture complète des 36 options gwd |
| **[GOLDEN_MASTER_SUMMARY.md](GOLDEN_MASTER_SUMMARY.md)** | 📝 Guide golden master pour gwu |
| **[INDEX_gwd_golden.md](INDEX_gwd_golden.md)** | 📑 Index des tests gwd |
| **[QUICKSTART_gwd_golden.md](QUICKSTART_gwd_golden.md)** | ⚡ Guide de démarrage rapide |
| **[README_gwd_golden.md](README_gwd_golden.md)** | 📖 Documentation détaillée gwd |

### Lecture recommandée

1. **Débutant** : Commencez par [SUMMARY.md](SUMMARY.md)
2. **Utilisateur** : Consultez [QUICKSTART_gwd_golden.md](QUICKSTART_gwd_golden.md)
3. **Développeur** : Lisez [CURRENT_STATUS.md](CURRENT_STATUS.md)
4. **Architecte** : Étudiez [GWD_OPTIONS_COVERAGE.md](GWD_OPTIONS_COVERAGE.md)

---

## 🔧 Configuration

### Prérequis

- Python 3.6+
- GeneWeb compilé (`make distrib`)
- Base de données GeneWeb (par défaut : `galichet`)

### Variables d'environnement

```bash
# Base de données à tester
export GWD_TEST_BASE=galichet

# Répertoire distribution
export GWD_TEST_DIST=./distribution

# Lancer les tests
./test/gwd_test.sh quick
```

### Fichiers de configuration

#### `fixtures/gwd_auth.txt`
Fichier d'autorisation pour tests d'authentification :
```
testuser:testpass
friend:friendpass
wizard:wizardpass
admin:admin123
```

#### `fixtures/allowed_tags.txt`
Tags HTML autorisés pour filtrage :
```
p
div
span
a
strong
...
```

---

## 🎓 Prochaines étapes

### Phase 1 : Internationalisation (Priorité HAUTE)
**Effort** : 2-3 heures  
**Gain** : Tester `-lang` et `-blang` (+5 scénarios)

```bash
# Après implémentation
./test/gwd_test.sh record i18n
./test/gwd_test.sh verify i18n
```

### Phase 2 : Authentification (Priorité HAUTE)
**Effort** : 3-4 heures  
**Gain** : Tester `-auth`, `-friend`, `-wizard`, `-digest`, `-wjf` (+6 scénarios)

```bash
# Après implémentation
./test/gwd_test.sh record auth
./test/gwd_test.sh verify auth
```

### Phase 3 : Interface (Priorité MOYENNE)
**Effort** : 2 heures  
**Gain** : Tester `-setup_link`, `-images_url`, `-allowed_tags` (+3 scénarios)

```bash
# Après implémentation
./test/gwd_test.sh record interface
./test/gwd_test.sh verify interface
```

### Objectif final
- **45+ scénarios** de test
- **23/36 options** gwd couvertes (64%)
- **~80%** des fonctionnalités testées

---

## 🛠️ Développement

### Ajouter un nouveau scénario

1. **Éditer `gwd_golden.py`** :
```python
SCENARIO_SETS["basic"].append({
    "name": "mon_nouveau_test",
    "params": {"m": "STAT"},
    "description": "Description du test",
})
```

2. **Enregistrer le golden master** :
```bash
./test/gwd_test.sh record basic
```

3. **Vérifier** :
```bash
./test/gwd_test.sh verify basic
```

### Structure d'un scénario

```python
{
    "name": "nom_unique",              # Identifiant
    "params": {"m": "STAT"},           # Paramètres URL
    "description": "Description",       # Documentation
    "expect_status": 200,               # Code HTTP attendu (optionnel)
}
```

---

## 🐛 Troubleshooting

### Erreur : "gwd non trouvé"
```bash
# Construire la distribution
make distrib

# Vérifier
ls -la distribution/gw/gwd
```

### Erreur : "Base galichet.gwb n'existe pas"
```bash
# Vérifier la base
ls -la distribution/bases/galichet.gwb

# Utiliser une autre base
GWD_TEST_BASE=autre_base ./test/gwd_test.sh quick
```

### Différences inattendues
```bash
# Comparer manuellement
diff test/golden/gwd/galichet/homepage.html \
     /tmp/gwd_golden_verify_galichet/homepage.html

# Mettre à jour si intentionnel
./test/gwd_test.sh record basic
```

---

## 📊 Statistiques

### État actuel (Octobre 2025)

| Métrique | Valeur |
|----------|--------|
| **Tests GWD** | 25 scénarios ✅ |
| **Tests GWU** | Multiple scénarios ✅ |
| **Options testées** | 8/36 (22%) |
| **Temps d'exécution** | ~1.5s (quick), ~5s (full) |
| **Taux de réussite** | 100% |
| **Coverage** | ~40% fonctionnel |

### Objectif (Après Phase 1-3)

| Métrique | Valeur projetée |
|----------|-----------------|
| **Tests GWD** | 39 scénarios |
| **Options testées** | 21/36 (58%) |
| **Temps d'exécution** | ~2.5s |
| **Coverage** | ~75% fonctionnel |

---

## 🏆 Validation

### Test de santé
```bash
# Vérifier que tout fonctionne
./test/gwd_test.sh quick

# Résultat attendu :
# ✓ 8/8 scénarios conformes aux golden masters
```

### Test complet
```bash
# Vérifier tous les scénarios
./test/gwd_test.sh full

# Résultat attendu :
# ✓ 25/25 scénarios conformes aux golden masters
```

---

## 📝 Contribution

Pour ajouter des tests ou améliorer la couverture :

1. Consultez [GWD_OPTIONS_COVERAGE.md](GWD_OPTIONS_COVERAGE.md) pour voir les options non testées
2. Étudiez [CURRENT_STATUS.md](CURRENT_STATUS.md) pour les prochaines étapes
3. Suivez le guide de développement ci-dessus
4. Mettez à jour la documentation

---

## 📞 Ressources

- **Documentation GeneWeb** : [documentation/](../documentation/)
- **Script shell gwd** : `test/gwd_test.sh`
- **Script Python gwd** : `test/gwd_golden.py`
- **Script shell gwu** : `test/gwu_test.sh`
- **Script Python gwu** : `test/gwu_golden.py`

---

**Dernière mise à jour** : Octobre 2025  
**Version** : 1.0  
**Statut** : ✅ Stable et fonctionnel
