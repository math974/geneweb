# 📚 Index - Documentation Golden Master Testing pour gwd

Bienvenue dans la documentation du système de golden master testing pour `gwd`!

## 🎯 Par où commencer?

### Vous êtes nouveau? Commencez ici! 👇
1. **[QUICKSTART_gwd_golden.md](QUICKSTART_gwd_golden.md)** - Guide de démarrage rapide (5 min)
   - Commandes essentielles
   - Premiers tests
   - Workflow de base

### Vous voulez comprendre le système? 👇
2. **[GOLDEN_MASTER_SUMMARY.md](GOLDEN_MASTER_SUMMARY.md)** - Résumé complet du projet
   - Vue d'ensemble
   - Architecture technique
   - Statistiques
   - Comparaison avec l'existant

### Vous avez besoin de détails techniques? 👇
3. **[README_gwd_golden.md](README_gwd_golden.md)** - Documentation détaillée
   - Guide d'utilisation complet
   - Tous les scénarios disponibles
   - Configuration avancée
   - Dépannage

## 📂 Fichiers du système

### Scripts exécutables
- **[gwd_golden.py](gwd_golden.py)** - Script Python principal (880 lignes)
- **[gwd_test.sh](gwd_test.sh)** - Script shell de facilitation (130 lignes)

### Golden masters
- **[golden/gwd/galichet/](golden/gwd/galichet/)** - 22 fichiers HTML de référence

### Configuration
- **[golden/gwd/.gitignore](golden/gwd/.gitignore)** - Configuration Git

## 🚀 Commandes rapides

```bash
# Test rapide (8 scénarios de base)
./test/gwd_test.sh quick

# Test complet (tous les scénarios)
./test/gwd_test.sh full

# Enregistrer de nouveaux golden masters
./test/gwd_test.sh record all

# Aide
./test/gwd_test.sh help
```

## 📊 Scénarios disponibles

| Set | Scénarios | Description |
|-----|-----------|-------------|
| `basic` | 8 | Homepage, search, statistics, listes |
| `trees` | 6 | Arbres généalogiques (ancêtres, descendants) |
| `person` | 4 | Pages de personnes (détails, relations, chrono, famille) |
| `lists` | 4 | Listes (naissances, décès, mariages, âgés) |
| `admin` | 3 | Pages d'administration (définis, non testés) |
| `all` | 25 | Tous les scénarios ci-dessus |

## 🎓 Cas d'usage

### Développement quotidien
- Avant de modifier du code: `./test/gwd_test.sh quick`
- Après modification: `./test/gwd_test.sh full`

### Avant un commit important
- Vérification complète: `./test/gwd_test.sh full`
- Si changements intentionnels: `./test/gwd_test.sh record all`

### Ajout de nouvelles fonctionnalités
1. Ajouter le scénario dans `gwd_golden.py`
2. Enregistrer: `./test/gwd_test.sh record mon_nouveau_set`
3. Vérifier: `./test/gwd_test.sh verify mon_nouveau_set`

## 🔧 Dépannage rapide

| Problème | Solution |
|----------|----------|
| "gwd non trouvé" | `make distrib` |
| "Base ... n'existe pas" | Vérifier avec `ls distribution/bases/` |
| Différences non attendues | Voir logs dans `/tmp/gwd_golden_*.log` |

## 📞 Besoin d'aide?

1. Consultez le [QUICKSTART](QUICKSTART_gwd_golden.md)
2. Lisez le [README complet](README_gwd_golden.md)
3. Examinez le [SUMMARY](GOLDEN_MASTER_SUMMARY.md)
4. Lancez `./test/gwd_test.sh help`

## 🎉 Bon testing!

Le système de golden master testing pour gwd est prêt à l'emploi.
Commencez par `./test/gwd_test.sh quick` pour votre premier test!

---

**Dernière mise à jour**: Octobre 2024
**Version**: 1.0
**Auteur**: Généré automatiquement pour GeneWeb

