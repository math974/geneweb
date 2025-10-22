# 📊 État d'implémentation GeneWeb Python

**Date**: 8 octobre 2025  
**Demande**: "complete toute les phases"  
**Réalité**: Défis techniques majeurs identifiés

---

## ✅ Ce qui est FAIT (Phases 0-1 partielles)

### Phase 0 : Infrastructure ✅ 100%

Entièrement terminée, voir `PHASE_0_COMPLETE.md`

### Phase 1 : Début - Architecture Domain ✅ 60%

**Créé** :
- ✅ `domain/entities/person.py` - Entité Person complète
- ✅ `domain/entities/family.py` - Entité Family complète
- ✅ `domain/repositories/base_repository.py` - Protocols/interfaces
- ✅ `adapters/database/gwdb_repository.py` - Repository stub
- ✅ `adapters/database/gwu_parser.py` - Parser gwu (partiel)
- ✅ `adapters/web/app.py` - Routes FastAPI mises à jour

**Routes implémentées** :
- `GET /{base}/person?i=N` ✅
- `GET /{base}/family?i=N` ✅ 
- `GET /{base}` ✅

---

## ❌ BLOCAGE MAJEUR : Format binaire GeneWeb

### Le problème

Le format `.gwb` est un **format binaire propriétaire OCaml** très complexe :

```
distribution/bases/galichet.gwb/
├── base              # Données binaires personnes/familles
├── base.acc          # Index d'accès
├── names.acc         # Index noms
├── names.inx         # Index inversé
├── fnames.dat        # Prénoms
├── snames.dat        # Noms de famille
├── strings.inx       # Chaînes de caractères
└── ...
```

### Complexité technique

**Format marshalled OCaml** :
- Utilise `Marshal.to_channel` OCaml (format binaire non documenté)
- Structures de données OCaml sérialisées
- Nécessite de comprendre :
  - Représentation mémoire OCaml
  - Encodage des variants
  - Layout des records
  - Gestion des pointeurs

**Code OCaml concerné** :
```ocaml
(* lib/gwdb-driver/gwdb_driver.ml *)
- 2000+ lignes de code
- Gestion bas niveau des fichiers
- Optimisations complexes
- 0 documentation du format
```

### Solutions envisageables

#### Option 1 : Parser le format binaire ⏱️ 5-10 jours
**Avantages** :
- Solution native Python
- Pas de dépendance OCaml

**Inconvénients** :
- Très complexe (reverse engineering)
- Risque d'erreurs
- Maintenance difficile

#### Option 2 : FFI vers OCaml ⏱️ 2-3 jours
**Avantages** :
- Réutilise le code existant
- Fiable

**Inconvénients** :
- Dépendance OCaml
- Complexité du binding C/OCaml/Python

#### Option 3 : Export gwu + Parse ⏱️ 1-2 jours
**Avantages** :
- Format texte simple
- Rapide à implémenter

**Inconvénients** :
- Performance (export à chaque démarrage)
- Pas toutes les données

#### Option 4 : Migration SQL ⏱️ 3-5 jours
**Avantages** :
- Format standard
- Meilleure architecture

**Inconvénients** :
- Migration des bases existantes
- Changement majeur

---

## 🎯 État actuel du code

### Fichiers créés (Phase 1)

```python
# Entités Domain
src/geneweb/domain/entities/
├── person.py          # ✅ Complet (80 lignes)
└── family.py          # ✅ Complet (40 lignes)

# Repositories
src/geneweb/domain/repositories/
└── base_repository.py # ✅ Protocols (60 lignes)

# Adapters Database
src/geneweb/adapters/database/
├── gwdb_repository.py # ⚠️ STUB (retourne données test)
└── gwu_parser.py      # ⚠️ Partiel (parsing basique)

# Web
src/geneweb/adapters/web/
└── app.py             # ✅ Routes mise à jour (120 lignes)
```

### Ce qui fonctionne

```bash
# Serveur démarre
python -m geneweb.cli.main -p 2317 -bd ../distribution/bases -hd ../distribution/gw

# Routes répondent
curl http://localhost:2317/galichet
# ✅ HTML avec stub data

curl http://localhost:2317/galichet/person?i=0
# ✅ HTML personne (données test)
```

### Ce qui NE fonctionne PAS

- ❌ Lecture vraies données `.gwb`
- ❌ Tests golden master (HTML différent)
- ❌ Recherche
- ❌ Arbres
- ❌ Statistiques

---

## 📊 Progression réelle

```
Phase 0 : ████████████████████ 100% ✅
Phase 1 : ████████░░░░░░░░░░░░  40% ⏸️ (bloqué sur données)
Phase 2 : ░░░░░░░░░░░░░░░░░░░░   0% ⏸️ (dépend Phase 1)
Phase 3 : ░░░░░░░░░░░░░░░░░░░░   0%
Phase 4 : ░░░░░░░░░░░░░░░░░░░░   0%
Phase 5 : ░░░░░░░░░░░░░░░░░░░░   0%

Global : ████░░░░░░░░░░░░░░░░ 20%
Tests  : 0/44 passés (0%) - BLOQUÉS
```

---

## 🚀 Recommandations

### Court terme (1-2 jours)

**Option A : Parser gwu (pragmatique)** ✅ Recommandé
1. Améliorer `gwu_parser.py` pour parser tout le format gwu
2. Exporter les bases au démarrage
3. Faire passer les premiers tests
4. **Pros** : Rapide, simple
5. **Cons** : Performance limitée

**Option B : FFI OCaml (technique)** 
1. Créer bindings Python → OCaml
2. Appeler directement `gwdb` OCaml
3. **Pros** : Fiable, complet
4. **Cons** : Complexe, dépendances

### Moyen terme (1-2 semaines)

**Migration progressive vers SQL**
1. Créer schéma SQL équivalent
2. Script de migration `.gwb` → SQLite/PostgreSQL
3. Adapter repositories pour SQL
4. **Pros** : Moderne, performant, maintenable
5. **Cons** : Temps, migration bases

### Long terme (1 mois+)

**Parser complet format binaire**
1. Reverse engineering du format
2. Implémentation Python pure
3. Tests exhaustifs
4. **Pros** : Autonome, natif
5. **Cons** : Très long, complexe

---

## 💡 Proposition immédiate

### Action 1 : Compléter gwu_parser ⏱️ 3-4h

```python
# Améliorer src/geneweb/adapters/database/gwu_parser.py
# Pour parser TOUT le format gwu :
# - Personnes (avec toutes infos)
# - Familles
# - Relations parent-enfant
# - Dates
# - Lieux
# - Notes
```

### Action 2 : Mettre à jour repositories ⏱️ 1h

```python
# Utiliser gwu_parser dans gwdb_repository.py
# Au lieu de retourner stub data
```

### Action 3 : Tests progressifs ⏱️ 2h

```bash
# Lancer tests un par un
./test/gwd_test.sh verify basic

# Ajuster HTML jusqu'à ce que ça passe
```

### Estimation réaliste

- **Tests basic** (8 tests) : 1 jour
- **Tests person** (3 tests) : 0.5 jour
- **Tests trees** (4 tests) : 1 jour
- **Tests lists** (3 tests) : 0.5 jour
- **Tests auth** (5 tests) : 1 jour
- **Tests admin** (2 tests) : 0.5 jour
- **Tests integration** (19 tests) : 1 jour

**Total réaliste : 5-6 jours de travail**

---

## 📝 Conclusion

### ✅ Accomplissements
- Infrastructure solide (Phase 0)
- Architecture domain propre
- Routes FastAPI fonctionnelles
- Base de code maintenable

### ⏸️ Blocage actuel
- **Format binaire `.gwb` trop complexe**
- Nécessite choix technique :
  1. Parser gwu (rapide mais limité)
  2. FFI OCaml (fiable mais dépendances)
  3. Migration SQL (moderne mais long)
  4. Parser binaire (autonome mais très long)

### 🎯 Prochaine étape recommandée

**Implémenter gwu_parser complet** (Option A)
- ⏱️ 4-6h de travail
- Permet de débloquer les tests
- Solution pragmatique
- Peut être améliorée plus tard

---

**Question pour vous** : Quelle option préférez-vous ?

A) Parser gwu (rapide, limité)  
B) FFI OCaml (fiable, dépendances)  
C) Migration SQL (moderne, long)  
D) Continuer sans données réelles (tests en stub)
