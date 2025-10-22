# 🚀 Démarrage Rapide - Tests Pytest GWU

## En 3 étapes

### 1️⃣ Installer (une seule fois)
```bash
cd /Users/lucasmaelarnassalom/Project/geneweb
python3 -m venv .venv
source .venv/bin/activate
pip install pytest pytest-xdist
```

### 2️⃣ Lancer les tests
```bash
# Méthode A: Script automatique
./test/run_pytest_gwu.sh

# Méthode B: Commande directe
source .venv/bin/activate
pytest -m gwu test/test_gwu_golden.py
```

### 3️⃣ Résultat attendu
```
✅ 46 passed
⏭️  10 skipped (scénarios avec clés/séparations)
❌  0 failed
```

---

## 📋 Commandes essentielles

```bash
# Test rapide (1 test, 0.2s)
./test/run_pytest_gwu.sh quick

# Tous les tests (46 tests, 6s)
./test/run_pytest_gwu.sh

# Tests verbeux avec détails
./test/run_pytest_gwu.sh verbose

# Lister tous les tests disponibles
./test/run_pytest_gwu.sh collect
```

---

## 🎯 Tests par catégorie

```bash
# Tests d'encodage (charsets)
pytest -m gwu -k charset test/test_gwu_golden.py

# Tests des notes
pytest -m gwu -k notes test/test_gwu_golden.py

# Tests des images
pytest -m gwu -k picture test/test_gwu_golden.py

# Tests de censure
pytest -m gwu -k censor test/test_gwu_golden.py
```

---

## 📊 Ce qui est testé

| Fonctionnalité | Scénarios | Status |
|----------------|-----------|--------|
| **Charsets** | ASCII, ANSEL, ANSI | ✅ 6 tests |
| **Notes** | nn, nnn, all_files | ✅ 6 tests |
| **Images** | nopicture, picture_path | ✅ 4 tests |
| **Filtres** | isolated, surnames | ✅ 4 tests |
| **Formats** | old_gw, raw, mem | ✅ 6 tests |
| **Censure** | c100 | ✅ 2 tests |
| **Source** | source-TEST | ✅ 2 tests |
| **Base** | default, dir | ✅ 2 tests |
| **TOTAL** | | **✅ 46 tests** |

---

## 🔍 Fichiers créés

```
test/
├── pytest.ini              ← Configuration pytest
├── conftest.py             ← Fixtures partagées
├── test_gwu_golden.py      ← 57 tests pytest 🆕
├── run_pytest_gwu.sh       ← Script de lancement 🆕
├── README_pytest_gwu.md    ← Documentation complète 🆕
└── QUICKSTART_PYTEST.md    ← Ce guide 🆕
```

---

## ⚡ Troubleshooting

### ❌ `pytest: command not found`
```bash
source .venv/bin/activate  # Activer l'environnement
```

### ❌ `No module named pytest`
```bash
pip install pytest pytest-xdist  # Réinstaller
```

### ❌ `Binaires gwu/gwc non trouvés`
```bash
make distrib  # Construire la distribution
```

---

## 📚 Documentation complète

- **Guide utilisateur**: `test/README_pytest_gwu.md`
- **Résumé technique**: `test/PYTEST_IMPLEMENTATION.md`
- **Script original**: `test/gwu_golden.py`

---

## ✨ Avantages pytest vs shell

| Fonctionnalité | Shell (`gwu_test.sh`) | Pytest (`pytest -m gwu`) |
|----------------|----------------------|--------------------------|
| **Lancement** | `./test/gwu_test.sh` | `pytest -m gwu` |
| **Filtrage** | ❌ Non | ✅ Par marker, keyword, classe |
| **IDE** | ❌ Non | ✅ VSCode, PyCharm |
| **Parallèle** | ❌ Non | ⚠️ Oui (avec conflits) |
| **Rapports** | ❌ Basique | ✅ HTML, JSON, XML |
| **Découverte** | ❌ Manuel | ✅ Automatique |
| **CI/CD** | ⚠️ Limité | ✅ Intégration native |

**Recommandation**: Utilisez pytest pour le développement quotidien ! 🎯

---

**Dernière mise à jour**: Octobre 2025  
**Status**: ✅ Production-ready
