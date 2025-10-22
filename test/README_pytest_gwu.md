# Tests Pytest pour GWU

Guide d'utilisation des tests pytest pour `gwu` (GeneWeb Unification/Export).

## 🚀 Démarrage rapide

### Installation des dépendances

```bash
# Créer un environnement virtuel
python3 -m venv .venv
source .venv/bin/activate  # Sur macOS/Linux
# .venv\Scripts\activate   # Sur Windows

# Installer pytest
pip install pytest pytest-xdist
```

### Lancer les tests

```bash
# Activer l'environnement virtuel
source .venv/bin/activate

# Tous les tests gwu
pytest -m gwu

# Tests avec sortie détaillée
pytest -m gwu -v

# Tests très verbeux (avec logs des commandes)
pytest -m gwu -vv -s

# Tests parallèles (plus rapide)
pytest -m gwu -n auto
```

## 📊 Statistiques

- **46 tests réussis** ✅
- **10 tests skippés** (scénarios nécessitant clés/séparations spécifiques)
- **Couverture**: Tous les scénarios golden automatiquement testés
- **Durée**: ~6 secondes (séquentiel), ~2 secondes (parallèle)

## 🎯 Types de tests

### 1. Tests paramétrés (découverte automatique)

Les tests paramétrés découvrent automatiquement tous les fichiers golden dans `test/golden/galichet/` et créent un test pour chaque scénario.

```python
# Un test par scénario golden
test_gwu_galichet_verify[default]
test_gwu_galichet_verify[charset-ASCII]
test_gwu_galichet_verify[raw]
test_gwu_galichet_verify[nn]
# ... etc
```

**Lancer les tests paramétrés:**

```bash
# Tous les scénarios
pytest test/test_gwu_golden.py::test_gwu_galichet_verify -v

# Un scénario spécifique
pytest test/test_gwu_golden.py::test_gwu_galichet_verify[charset-ASCII] -v

# Scénarios correspondant à un pattern
pytest test/test_gwu_golden.py::test_gwu_galichet_verify -k "charset" -v
```

### 2. Tests explicites (par catégorie)

Tests organisés en classes pour une meilleure organisation:

- **TestGwuBasics**: Tests de base
- **TestGwuCharsets**: Tests d'encodage (ASCII, ANSEL, ANSI)
- **TestGwuFiltering**: Tests de filtrage (isolated)
- **TestGwuNotes**: Tests des notes (nn, nnn, all_files)
- **TestGwuPictures**: Tests des images (nopicture, picture_path)
- **TestGwuCensorship**: Tests de censure
- **TestGwuFormats**: Tests de formats (old_gw, raw, mem)

**Lancer les tests par classe:**

```bash
# Tests d'une classe spécifique
pytest test/test_gwu_golden.py::TestGwuCharsets -v

# Test spécifique dans une classe
pytest test/test_gwu_golden.py::TestGwuNotes::test_no_notes_at_all -v
```

## 🔍 Filtrage des tests

### Par marker

```bash
# Tous les tests gwu
pytest -m gwu

# Tests lents uniquement
pytest -m slow

# Exclure les tests lents
pytest -m "gwu and not slow"
```

### Par mot-clé (-k)

```bash
# Tests contenant "charset"
pytest -m gwu -k "charset"

# Tests contenant "notes" ou "picture"
pytest -m gwu -k "notes or picture"

# Exclure certains tests
pytest -m gwu -k "not censor"
```

### Par fichier

```bash
# Seulement test_gwu_golden.py
pytest test/test_gwu_golden.py

# Plusieurs fichiers
pytest test/test_gwu_golden.py test/test_gwd_golden.py
```

## 📝 Scénarios testés

### Scénarios actifs (46 tests)

| Catégorie | Scénarios | Description |
|-----------|-----------|-------------|
| **Base** | default, dir | Export standard |
| **Charsets** | ASCII, ANSEL, ANSI, UTF-8 | Encodages de sortie |
| **Filtres** | isolated, surnames | Sélection de personnes |
| **Notes** | nn, nnn, all_files | Gestion des notes |
| **Images** | nopicture, picture_path | Gestion des images |
| **Censure** | c100 | Censure par âge |
| **Formats** | old_gw, raw, mem | Formats de sortie |
| **Source** | source-TEST | Remplacement source |

Chaque scénario est testé avec **2 variantes**:
- Export standard (`-o fichier.gw`)
- Export avec répertoire (`-o fichier.gw -odir outdir/`)

### Scénarios skippés (10 tests)

Les scénarios suivants nécessitent des valeurs spécifiques non récupérables depuis le nom de fichier:

- `key-1.a2.d1` - Nécessite une clé de personne spécifique
- `key-1.ad2` - Nécessite une clé de personne spécifique
- `key-2.parentship` - Nécessite deux clés de personnes
- `sep-1` - Nécessite une personne à séparer
- `sep-1.seplimit5` - Nécessite une personne à séparer

**Note**: Ces scénarios peuvent être testés manuellement avec `gwu_golden.py`.

## 🛠️ Commandes utiles

### Lister les tests disponibles

```bash
# Lister sans exécuter
pytest --collect-only test/test_gwu_golden.py

# Lister de manière concise
pytest --collect-only -q test/test_gwu_golden.py
```

### Exécution sélective

```bash
# Stopper au premier échec
pytest -m gwu -x

# Stopper après N échecs
pytest -m gwu --maxfail=3

# Relancer seulement les tests échoués
pytest -m gwu --lf

# Relancer d'abord les tests échoués
pytest -m gwu --ff
```

### Sortie et verbosité

```bash
# Mode quiet (moins de sortie)
pytest -m gwu -q

# Mode verbeux
pytest -m gwu -v

# Très verbeux avec stdout
pytest -m gwu -vv -s

# Avec traceback complet
pytest -m gwu --tb=long
```

### Tests parallèles

⚠️ **Note**: Les tests parallèles peuvent causer des conflits d'accès fichiers.  
Recommandé: Exécution séquentielle pour gwu.

```bash
# Auto-détection du nombre de CPU (peut causer des conflits)
pytest -m gwu -n auto

# Nombre spécifique de workers (peut causer des conflits)
pytest -m gwu -n 4

# Recommandé: séquentiel
pytest -m gwu -v
```

## 📂 Structure des fichiers

```
test/
├── conftest.py                 # Fixtures partagées
├── pytest.ini                  # Configuration pytest
├── test_gwu_golden.py         # Tests gwu avec pytest
├── gwu_golden.py              # Module de base (réutilisé)
├── gwu_test.sh                # Script shell (alternatif)
└── golden/
    └── galichet/              # Fichiers de référence
        ├── galichet.golden.gw
        ├── galichet.charset-ASCII.golden.gw
        └── ...
```

## 🔧 Fixtures disponibles

Les fixtures suivantes sont définies dans `conftest.py`:

- `dist_dir` - Chemin vers `./distribution`
- `gwu_bins` - Tuple (gwu_path, gwc_path)
- `bases_dir` - Chemin vers `distribution/bases`
- `galichet_base` - Base galichet prête pour les tests
- `ares_base` - Base ares prête pour les tests
- `golden_dir` - Chemin vers `test/golden`

## 🎨 Intégration IDE

### VSCode

Installer l'extension **Python Test Explorer** et configurer:

```json
{
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "test",
        "-m", "gwu"
    ]
}
```

### PyCharm

1. Ouvrir **Settings → Tools → Python Integrated Tools**
2. Sélectionner **pytest** comme test runner
3. Les tests apparaîtront dans le panneau "Run"

## 📈 Rapports et couverture

### Rapports HTML

```bash
# Installer pytest-html
pip install pytest-html

# Générer un rapport
pytest -m gwu --html=report.html --self-contained-html
```

### Couverture de code

```bash
# Installer pytest-cov
pip install pytest-cov

# Générer un rapport de couverture
pytest -m gwu --cov=gwu_golden --cov-report=html
```

## 🚨 Dépannage

### pytest n'est pas trouvé

```bash
# Vérifier l'environnement virtuel
which python
which pytest

# Réactiver l'environnement
source .venv/bin/activate
```

### Binaires gwu/gwc non trouvés

```bash
# Construire la distribution
make distrib

# Ou vérifier le chemin
ls -la distribution/gw/gwu
ls -la distribution/gw/gwc
```

### Tests échouent pour la base galichet

```bash
# Vérifier que le fichier source existe
ls -la test/galichet.gw

# Reconstruire la base manuellement
distribution/gw/gwc -v -f -cg -bd distribution/bases -o galichet test/galichet.gw
```

## 📚 Ressources

- [Documentation pytest](https://docs.pytest.org/)
- [pytest-xdist](https://pytest-xdist.readthedocs.io/)
- [Golden Master Testing](https://en.wikipedia.org/wiki/Characterization_test)
- `test/README.md` - Documentation générale des tests GeneWeb
- `test/gwu_test.sh` - Script shell alternatif

## 🤝 Contribution

Pour ajouter de nouveaux scénarios:

1. Créer le golden avec `gwu_golden.py record`
2. Les tests seront automatiquement découverts
3. Lancer `pytest -m gwu` pour valider

Pour ajouter de nouveaux tests explicites:

1. Éditer `test/test_gwu_golden.py`
2. Ajouter une méthode dans une classe `TestGwu*`
3. Marquer avec `@pytest.mark.gwu`

---

**Dernière mise à jour**: Octobre 2025  
**Version pytest**: 8.4.2  
**Python**: 3.13+
