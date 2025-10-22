# 📚 Index de la Documentation Tests GWD

> Infrastructure complète de tests pour GeneWeb - Version 1.0

## 🚀 Par où commencer ?

### Nouveau sur le projet ?
1. 📦 **[FINAL_DELIVERY.md](FINAL_DELIVERY.md)** - Vue d'ensemble complète
2. ⚡ **[QUICKREF.md](QUICKREF.md)** - Référence rapide
3. 🚀 **[QUICKSTART_gwd_golden.md](QUICKSTART_gwd_golden.md)** - Démarrage rapide

### Besoin d'aide ?
- 📖 **[README_gwd_golden.md](README_gwd_golden.md)** - Guide détaillé golden master
- 🔧 **[INTEGRATION_TESTS.md](INTEGRATION_TESTS.md)** - Guide tests d'intégration
- 📊 **[TEST_COVERAGE_SUMMARY.md](TEST_COVERAGE_SUMMARY.md)** - Synthèse de couverture

## 📂 Documentation par thème

### 1️⃣ Guides d'utilisation

| Document | Description | Lecteur cible |
|----------|-------------|---------------|
| **[FINAL_DELIVERY.md](FINAL_DELIVERY.md)** | 📦 Livraison complète v1.0 | Chef de projet, Lead dev |
| **[QUICKREF.md](QUICKREF.md)** | ⚡ Référence rapide | Développeur quotidien |
| **[QUICKSTART_gwd_golden.md](QUICKSTART_gwd_golden.md)** | 🚀 Démarrage en 5 min | Nouveau contributeur |
| **[README_gwd_golden.md](README_gwd_golden.md)** | 📖 Guide complet golden master | Développeur/Testeur |
| **[INTEGRATION_TESTS.md](INTEGRATION_TESTS.md)** | 🔧 Guide tests intégration | Développeur/Testeur |

### 2️⃣ Analyses et métriques

| Document | Description | Contenu |
|----------|-------------|---------|
| **[TEST_COVERAGE_SUMMARY.md](TEST_COVERAGE_SUMMARY.md)** | 📊 Synthèse de couverture | Métriques globales, graphiques |
| **[GWD_OPTIONS_COVERAGE.md](GWD_OPTIONS_COVERAGE.md)** | 🎯 Analyse des 43 options | Détail par option, priorités |
| **[INDEX_gwd_golden.md](INDEX_gwd_golden.md)** | 📑 Index des scénarios | Liste complète des tests |

### 3️⃣ Documentation technique

| Document | Description | Technique |
|----------|-------------|-----------|
| **[GOLDEN_MASTER_SUMMARY.md](GOLDEN_MASTER_SUMMARY.md)** | ✅ Implémentation golden master | Architecture, code |
| **[OPTIONS_VERIFICATION.md](OPTIONS_VERIFICATION.md)** | ✓ Vérification options | Checklist validation |

## 🔍 Navigation par besoin

### Je veux lancer les tests
```bash
# Quick start
./test/gwd_test.sh quick           # 30s
./test/run_all_tests.sh            # 3-4min

# Voir: QUICKREF.md
```

### Je veux comprendre l'architecture
1. **[FINAL_DELIVERY.md](FINAL_DELIVERY.md)** - Architecture globale
2. **[README_gwd_golden.md](README_gwd_golden.md)** - Golden master en détail
3. **[INTEGRATION_TESTS.md](INTEGRATION_TESTS.md)** - Tests d'intégration

### Je veux ajouter un test
1. **[README_gwd_golden.md](README_gwd_golden.md)** § "Ajouter un nouveau scénario"
2. **[INTEGRATION_TESTS.md](INTEGRATION_TESTS.md)** § "Ajouter un nouveau test"
3. **[QUICKSTART_gwd_golden.md](QUICKSTART_gwd_golden.md)** - Exemples rapides

### Je veux voir les métriques
- **[TEST_COVERAGE_SUMMARY.md](TEST_COVERAGE_SUMMARY.md)** - Vue d'ensemble
- **[GWD_OPTIONS_COVERAGE.md](GWD_OPTIONS_COVERAGE.md)** - Par option
- **[INDEX_gwd_golden.md](INDEX_gwd_golden.md)** - Liste des tests

### Je veux débugger un test
1. **[README_gwd_golden.md](README_gwd_golden.md)** § "Dépannage"
2. Logs dans `/tmp/gwd_golden_*.log`
3. Mode verbose : éditer les scripts

## 📊 Résumé des tests

### Golden Master (25 tests)
| Catégorie | Tests | Fichiers |
|-----------|-------|----------|
| basic | 12 | [basic/](golden/gwd/basic/) |
| trees | 5 | [trees/](golden/gwd/trees/) |
| person | 3 | [person/](golden/gwd/person/) |
| lists | 2 | [lists/](golden/gwd/lists/) |
| admin | 3 | [admin/](golden/gwd/admin/) |
| auth | 5 | [auth/](golden/gwd/auth/) |

**Script** : `gwd_golden.py`, wrapper `gwd_test.sh`

### Intégration (14 tests)
| Catégorie | Tests | Options |
|-----------|-------|---------|
| network | 3 | -a, -only, -no_host_address |
| mode | 1 | -daemon |
| limits | 2 | -max_clients, -login_tmout |
| files | 2 | -nolock, -wd |
| logs | 2 | -log_level, -trace_failed_passwd |
| cache | 4 | -cache_langs, -debug, etc. |

**Script** : `gwd_integration_tests.py`

## 🎯 Couverture

- ✅ **39/43 options testées** (91%)
- ✅ **100% options critiques**
- ✅ **25 tests golden master**
- ✅ **14 tests d'intégration**

## 📁 Structure des fichiers

```
test/
├── 📚 Documentation
│   ├── 00_INDEX.md                    # ← Vous êtes ici
│   ├── FINAL_DELIVERY.md              # Livraison v1.0
│   ├── TEST_COVERAGE_SUMMARY.md       # Synthèse
│   ├── README_gwd_golden.md           # Guide golden
│   ├── INTEGRATION_TESTS.md           # Guide intégration
│   ├── QUICKREF.md                    # Référence rapide
│   ├── QUICKSTART_gwd_golden.md       # Démarrage rapide
│   ├── INDEX_gwd_golden.md            # Index tests
│   ├── GWD_OPTIONS_COVERAGE.md        # Analyse options
│   ├── GOLDEN_MASTER_SUMMARY.md       # Résumé golden
│   └── OPTIONS_VERIFICATION.md        # Vérification
│
├── 🧪 Scripts de test
│   ├── gwd_golden.py                  # Tests golden master
│   ├── gwd_integration_tests.py       # Tests intégration
│   ├── gwd_test.sh                    # Wrapper shell
│   └── run_all_tests.sh               # Lance tout
│
├── 📸 Golden masters
│   └── golden/gwd/
│       ├── basic/                     # 12 snapshots
│       ├── trees/                     # 5 snapshots
│       ├── person/                    # 3 snapshots
│       ├── lists/                     # 2 snapshots
│       ├── admin/                     # 3 snapshots
│       └── auth/                      # 5 snapshots
│
└── 🔧 Fixtures
    ├── gwd_auth.txt                   # Auth test
    └── allowed_tags.txt               # Tags HTML
```

## 🔗 Liens rapides

### Commandes essentielles
```bash
./test/gwd_test.sh quick              # Quick test
./test/run_all_tests.sh               # Full test
./test/gwd_integration_tests.py       # Integration
```

### Documentation
- 📦 [Livraison finale](FINAL_DELIVERY.md)
- 📊 [Synthèse](TEST_COVERAGE_SUMMARY.md)
- ⚡ [Quick ref](QUICKREF.md)
- 🚀 [Quick start](QUICKSTART_gwd_golden.md)

### Support
1. Consulter la doc appropriée ci-dessus
2. Vérifier `/tmp/gwd_golden_*.log`
3. Tester avec `./test/gwd_test.sh quick`

## 📈 Progression

- [x] ✅ Tests golden master (25)
- [x] ✅ Tests d'intégration (14)
- [x] ✅ Documentation complète (11 fichiers)
- [x] ✅ Scripts d'automatisation (3)
- [x] ✅ 91% couverture options
- [ ] 🔜 Tests digest/wjf (v1.1)
- [ ] 🔜 Tests plugins (v1.2)
- [ ] 🔜 CI/CD integration (v1.3)

---

**Infrastructure de tests GeneWeb v1.0**  
**91% de couverture | 39 tests | Production ready**

📖 Commencer par **[FINAL_DELIVERY.md](FINAL_DELIVERY.md)** pour une vue complète
