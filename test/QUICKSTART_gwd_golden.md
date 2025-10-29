# 🚀 Guide de démarrage rapide - Golden Master Testing pour gwd

## ⚡ Utilisation en 30 secondes

### Pour tester rapidement (développement quotidien)
```bash
./test/gwd_test.sh quick
```
✅ Teste les 8 scénarios de base en ~5 secondes

### Pour tester complètement (avant commit)
```bash
./test/gwd_test.sh full
```
✅ Teste tous les scénarios en ~10 secondes

## 📚 Commandes principales

| Commande | Description | Cas d'usage |
|----------|-------------|-------------|
| `./test/gwd_test.sh quick` | Test rapide | Développement quotidien |
| `./test/gwd_test.sh full` | Test complet | Avant commit/release |
| `./test/gwd_test.sh record basic` | Enregistrer golden masters | Après changement intentionnel |
| `./test/gwd_test.sh verify trees` | Vérifier un set spécifique | Test ciblé |
| `./test/gwd_test.sh help` | Aide | Documentation |

## 🎯 Scénarios disponibles

- **basic** : Tests de base (homepage, search, stats) - *8 scénarios*
- **trees** : Arbres généalogiques - *6 scénarios*
- **person** : Pages de personnes - *4 scénarios*
- **lists** : Listes diverses - *4 scénarios*
- **admin** : Administration - *3 scénarios*
- **all** : Tous les scénarios - *25 scénarios*

## 📖 Workflow typique

### 1. Avant de modifier du code
```bash
# S'assurer que tout fonctionne actuellement
./test/gwd_test.sh quick
```

### 2. Après modification du code
```bash
# Vérifier qu'il n'y a pas de régression
./test/gwd_test.sh full
```

### 3. Si des différences sont intentionnelles
```bash
# Mettre à jour les golden masters
./test/gwd_test.sh record all
```

### 4. Avant de commiter
```bash
# Vérification finale
./test/gwd_test.sh full
git add test/golden/gwd/
git commit -m "Update: description du changement"
```

## ⚙️ Configuration avancée

### Utiliser une autre base de données
```bash
GWD_TEST_BASE=autre_base ./test/gwd_test.sh quick
```

### Utiliser une autre distribution
```bash
GWD_TEST_DIST=/path/to/distribution ./test/gwd_test.sh quick
```

### Utiliser directement le script Python
```bash
# Plus de contrôle et d'options
python3 test/gwd_golden.py --help

# Exemples
python3 test/gwd_golden.py record --base galichet --scenarios basic trees
python3 test/gwd_golden.py verify --base galichet --scenarios all
```

## 🆘 En cas de problème

### Erreur "gwd non trouvé"
```bash
make distrib
```

### Erreur "Base ... n'existe pas"
```bash
# Vérifier les bases disponibles
ls distribution/bases/

# Créer une base de test si nécessaire
distribution/gw/gwc -f -bd distribution/bases -o galichet test/galichet.gw
```

### Des différences sont détectées sans raison
1. Vérifiez que la base n'a pas été modifiée
2. Vérifiez les logs dans `/tmp/gwd_golden_*.log`
3. Consultez `test/README_gwd_golden.md` pour plus de détails

## 📁 Fichiers importants

```
test/
├── gwd_golden.py              ← Script Python principal
├── gwd_test.sh                ← Script de facilitation (à utiliser!)
├── README_gwd_golden.md       ← Documentation complète
├── GOLDEN_MASTER_SUMMARY.md   ← Résumé du projet
├── QUICKSTART_gwd_golden.md   ← Ce fichier!
└── golden/gwd/                ← Golden masters (à commiter!)
    └── galichet/
        ├── homepage.html
        ├── search.html
        └── ... (22 fichiers)
```

## 💡 Conseils

✅ **À faire:**
- Exécuter `./test/gwd_test.sh quick` régulièrement pendant le développement
- Exécuter `./test/gwd_test.sh full` avant chaque commit important
- Commiter les golden masters avec vos changements de code
- Ajouter de nouveaux scénarios pour les nouvelles fonctionnalités

❌ **À éviter:**
- Modifier manuellement les fichiers golden masters
- Ignorer les différences sans les comprendre
- Oublier de mettre à jour les golden masters après des changements intentionnels

## 🎓 Pour en savoir plus

- **Documentation complète** : `test/README_gwd_golden.md`
- **Résumé du projet** : `test/GOLDEN_MASTER_SUMMARY.md`
- **Code source** : `test/gwd_golden.py`
- **Aide en ligne** : `./test/gwd_test.sh help`

---

**C'est tout! Vous êtes prêt à utiliser le système de golden master testing pour gwd. 🎉**

