# 🚀 Démarrage Rapide - Tests GWU Golden Master

## Commandes Essentielles

### Test Simple (Recommandé pour Débuter)
```bash
python3 test/gwu_golden.py verify --base galichet
```

### Lancer TOUS les Tests (16 tests)
```bash
# Test de base
python3 test/gwu_golden.py verify --base galichet

# Formats et encodage
python3 test/gwu_golden.py verify --base galichet --charset ASCII
python3 test/gwu_golden.py verify --base galichet --charset ANSEL
python3 test/gwu_golden.py verify --base galichet --charset ANSI
python3 test/gwu_golden.py verify --base galichet --raw

# Sélection et filtres
python3 test/gwu_golden.py verify --base galichet -s "Galichet"
python3 test/gwu_golden.py verify --base galichet --isolated

# Gestion des notes
python3 test/gwu_golden.py verify --base galichet --nn
python3 test/gwu_golden.py verify --base galichet --nnn
python3 test/gwu_golden.py verify --base galichet --all-files

# Gestion des images
python3 test/gwu_golden.py verify --base galichet --nopicture
python3 test/gwu_golden.py verify --base galichet --picture-path

# Options avancées
python3 test/gwu_golden.py verify --base galichet --source "TEST"
python3 test/gwu_golden.py verify --base galichet -c 100
python3 test/gwu_golden.py verify --base galichet --old-gw
python3 test/gwu_golden.py verify --base galichet --mem
```

### Script Pour Tout Lancer d'un Coup
```bash
# Créer un script de test complet
cat > /tmp/test_gwu_all.sh << 'EOF'
#!/bin/bash
echo "🧪 Lancement des tests GWU..."
FAILED=0
for opt in "" "--charset ASCII" "--charset ANSEL" "--charset ANSI" "--raw" \
           "-s Galichet" "--isolated" "--nn" "--nnn" "--all-files" \
           "--nopicture" "--picture-path" "--source TEST" "-c 100" \
           "--old-gw" "--mem"; do
    echo "Test: $opt"
    python3 test/gwu_golden.py verify --base galichet $opt || FAILED=$((FAILED+1))
done
echo ""
echo "Résultat: $FAILED échec(s)"
exit $FAILED
EOF

chmod +x /tmp/test_gwu_all.sh
bash /tmp/test_gwu_all.sh
```

## Enregistrer de Nouveaux Golden Masters

```bash
# Enregistrer un golden pour l'option de base
python3 test/gwu_golden.py record --base galichet

# Avec une option spécifique
python3 test/gwu_golden.py record --base galichet --charset ASCII

# Avec plusieurs options combinées
python3 test/gwu_golden.py record --base galichet --charset UTF-8 -c 100
```

## Options Principales

| Option | Description | Exemple |
|--------|-------------|---------|
| `--base` | Nom de la base (requis) | `--base galichet` |
| `--charset` | Encodage de sortie | `--charset ASCII` |
| `--raw` | Sortie brute | `--raw` |
| `-s` | Filtre par patronyme | `-s "Dupont"` |
| `--isolated` | Inclure personnes isolées | `--isolated` |
| `--nn` | Sans notes de base | `--nn` |
| `--nnn` | Sans aucune note | `--nnn` |
| `--all-files` | Tous les fichiers notes | `--all-files` |
| `--nopicture` | Sans images | `--nopicture` |
| `--picture-path` | Chemins d'images | `--picture-path` |
| `--source` | Remplacer sources | `--source "TEST"` |
| `-c` | Censure par âge | `-c 100` |
| `--old-gw` | Format ancien | `--old-gw` |
| `--mem` | Mode économie mémoire | `--mem` |

## Aide

```bash
# Aide générale
python3 test/gwu_golden.py -h

# Aide pour record
python3 test/gwu_golden.py record -h

# Aide pour verify
python3 test/gwu_golden.py verify -h
```

## Structure des Fichiers

```
test/
├── gwu_golden.py                    # Script principal
├── golden/
│   └── galichet/
│       ├── galichet.golden.gw       # Golden master standard
│       ├── galichet.golden.stderr   # Logs golden
│       ├── galichet.charset-ASCII.golden.gw
│       └── ...
distribution/
├── bases/
│   └── galichet.gwb/                # Base de test
└── gw/
    └── gwu                          # Binaire gwu
```

## Résultats Attendus

```
Scenario: base=galichet source=None c=None ...
RUN: distribution/gw/gwu distribution/bases/galichet -v -o ...
RUN: distribution/gw/gwu distribution/bases/galichet -v -o ... -odir ...
OK: export standard conforme au golden.
OK: export -odir conforme au golden.
OK: logs standard (-v) conformes au golden.
OK: logs -odir (-v) conformes au golden.
```

## Dépannage

### Erreur "Golden manquant"
```bash
# Le golden n'existe pas, il faut d'abord le créer
python3 test/gwu_golden.py record --base galichet [OPTIONS]
```

### Erreur "Impossible de localiser gwu/gwc"
```bash
# Construire la distribution d'abord
make distrib
```

### Échec de test
```bash
# Voir les différences détaillées
python3 test/gwu_golden.py verify --base galichet [OPTIONS] 2>&1
```

## Couverture des Tests

- ✅ **16 options testées automatiquement** (70%)
- ⚠️  **7 options nécessitent configuration manuelle** (30%)
- 🎯 **100% des options implémentées**

Les options nécessitant configuration :
- `-key`, `-a`, `-d`, `--ad` : nécessitent clés valides
- `--parentship` : nécessite paires de clés
- `--sep`, `--sep-limit`, `--sep-only-file` : nécessitent -odir + clé

## Voir Aussi

- `test/README_gwu_golden.md` - Documentation complète
- `test/INDEX_gwu_golden.md` - Index des fonctionnalités

