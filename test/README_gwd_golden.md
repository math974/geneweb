# Golden Master Testing pour gwd

Ce document explique comment utiliser `gwd_golden.py` pour effectuer des tests de régression sur le serveur web GeneWeb (`gwd`).

## 📖 Qu'est-ce qu'un Golden Master Test?

Un golden master test (ou test de non-régression par snapshot) consiste à :
1. Capturer la sortie d'un programme (les "golden masters")
2. Comparer les sorties futures avec ces références
3. Détecter tout changement non intentionnel

Pour `gwd`, cela signifie capturer les pages HTML générées par le serveur et s'assurer qu'elles ne changent pas de manière inattendue.

## 🚀 Installation

Aucune installation supplémentaire n'est nécessaire. Le script utilise uniquement la bibliothèque standard Python 3.

## 📝 Utilisation

### 1. Enregistrer des Golden Masters

Pour capturer les réponses HTML actuelles de `gwd` et les sauvegarder comme référence :

```bash
# Scénarios de base (homepage, search, statistics, etc.)
./test/gwd_golden.py record --base galichet --scenarios basic

# Scénarios d'arbres généalogiques
./test/gwd_golden.py record --base galichet --scenarios trees

# Tous les scénarios disponibles
./test/gwd_golden.py record --base galichet --scenarios all

# Plusieurs sets de scénarios
./test/gwd_golden.py record --base galichet --scenarios basic trees person
```

Les golden masters sont sauvegardés dans `test/golden/gwd/{base}/`

### 2. Vérifier contre les Golden Masters

Pour vérifier que les réponses actuelles de `gwd` correspondent aux golden masters :

```bash
./test/gwd_golden.py verify --base galichet --scenarios basic
```

Si tout est conforme :
- Code de sortie : 0
- Message : "✓ Tous les scénarios sont conformes aux golden masters!"

Si des différences sont détectées :
- Code de sortie : 1
- Affichage des diffs pour chaque scénario non-conforme

### 3. Options avancées

```bash
# Utiliser une distribution différente
./test/gwd_golden.py record --base galichet --dist /path/to/distribution

# Ne pas ignorer les espaces de fin de ligne dans les diffs
./test/gwd_golden.py verify --base galichet --no-ignore-trailing-space
```

## 📚 Scénarios disponibles

Le script définit plusieurs sets de scénarios :

### `basic` (8 scénarios)
- Homepage de la base
- Recherche de personnes (existantes et inexistantes)
- Statistiques
- Listes de noms et prénoms

### `trees` (6 scénarios)
- Arbres des ancêtres (différents formats)
- Arbres des descendants (différents formats)

### `person` (4 scénarios)
- Fiche détaillée d'une personne
- Relations
- Chronologie
- Famille

### `lists` (4 scénarios)
- Listes de naissances récentes
- Listes de décès récents
- Listes de mariages récents
- Liste des plus âgés

### `admin` (3 scénarios)
- Page d'accueil wizard
- Formulaires d'ajout d'individu
- Formulaires d'ajout de famille

### `all`
Tous les scénarios ci-dessus

## 🔧 Fonctionnement interne

### Normalisation des réponses

Pour éviter les faux positifs, le script normalise automatiquement :
- Les timestamps (`<!-- generated at ... -->`)
- Les dates ISO (`2024-10-07T15:30:00`)
- Les chemins absoluts (`/Users/...`)
- Les session IDs

Cela garantit que seuls les véritables changements de contenu sont détectés.

### Gestion du serveur

Le script :
1. Démarre automatiquement `gwd` sur un port libre
2. Utilise le mode `-predictable_mode` pour la reproductibilité
3. Désactive les protections anti-robot
4. Arrête proprement le serveur à la fin

## 🎯 Utilisation dans CI/CD

Pour intégrer dans un pipeline CI/CD :

```bash
# Vérifier que tout est conforme
./test/gwd_golden.py verify --base galichet --scenarios all || exit 1
```

## 📁 Structure des fichiers

```
test/
├── gwd_golden.py              # Script principal
├── README_gwd_golden.md       # Cette documentation
└── golden/
    └── gwd/
        ├── galichet/
        │   ├── homepage.html
        │   ├── search.html
        │   ├── statistics.html
        │   └── ...
        └── autre_base/
            └── ...
```

## 🔍 Ajouter de nouveaux scénarios

Pour ajouter de nouveaux scénarios, éditez `gwd_golden.py` et ajoutez-les dans `SCENARIO_SETS` :

```python
SCENARIO_SETS = {
    "mon_nouveau_set": [
        {
            "name": "mon_scenario",
            "params": {"m": "X", "i": "123"},
            "description": "Description du scénario",
        },
        # ... autres scénarios
    ],
}
```

Puis enregistrez et vérifiez :

```bash
./test/gwd_golden.py record --base galichet --scenarios mon_nouveau_set
./test/gwd_golden.py verify --base galichet --scenarios mon_nouveau_set
```

## 🐛 Dépannage

### Erreur "gwd n'a pas démarré"

Vérifiez que la distribution est construite :
```bash
make distrib
```

### Erreur "La base ... n'existe pas"

Vérifiez que la base de données existe :
```bash
ls -l distribution/bases/galichet.gwb
```

Si elle n'existe pas, créez-la avec `gwc` :
```bash
distribution/gw/gwc -f -bd distribution/bases -o galichet test/galichet.gw
```

### Des différences sont détectées alors qu'il n'y a pas de changement

Cela peut arriver si :
1. Le mode `-predictable_mode` n'est pas utilisé
2. Des éléments non-normalisés varient (ajoutez des règles de normalisation)
3. La base de données a été modifiée

## 📊 Workflow recommandé

1. **Avant de modifier du code** : Enregistrez les golden masters actuels
   ```bash
   ./test/gwd_golden.py record --base galichet --scenarios all
   ```

2. **Après modification** : Vérifiez qu'il n'y a pas de régression
   ```bash
   ./test/gwd_golden.py verify --base galichet --scenarios all
   ```

3. **Si les changements sont intentionnels** : Mettez à jour les golden masters
   ```bash
   ./test/gwd_golden.py record --base galichet --scenarios all
   ```

4. **Committez** les golden masters mis à jour avec votre code

## 🔗 Voir aussi

- `gwu_golden.py` : Golden master testing pour l'outil d'export `gwu`
- `run_gw_test.sh` : Tests bash traditionnels pour `gwd`
- `tests/e2e/` : Tests end-to-end avec Selenium

## 📝 License

Même license que GeneWeb (voir LICENSE à la racine du projet)

