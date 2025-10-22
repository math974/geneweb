# 📊 Rapport Option A - Parser gwu

**Date**: 8 octobre 2025  
**Option choisie**: A - Parser gwu  
**Statut**: ⏸️ Partiellement implémenté - Bloqué sur complexité du format

---

## 🎯 Ce qui a été tenté

### 1. Analyse du format gwu ✅
- Exporté la base galichet avec `gwu`
- Analysé la structure du format
- Identifié les blocs principaux (`fam`, `pevt`, `beg/end`)

### 2. Parser gwu implémenté ⚠️ 
**Fichier**: `geneweb-python/src/geneweb/adapters/database/gwu_parser.py`

**Ce qui fonctionne** :
- ✅ Classe `GwuParser` créée
- ✅ Parsing des dates (DD/MM/YYYY)
- ✅ Parsing des événements (`pevt`)
- ✅ Parsing des familles (`fam`)
- ✅ Parsing des enfants (`beg/end`)

**Ce qui NE fonctionne PAS** :
- ❌ Liaison personnes ↔ événements
- ❌ Clés de personnes mal gérées
- ❌ Pas de personnes retournées (count = 0)
- ❌ Relations familiales incomplètes

### 3. Repository mis à jour ✅
**Fichier**: `geneweb-python/src/geneweb/adapters/database/gwdb_repository.py`

- ✅ Intégration `GwuCache`
- ✅ Méthodes `get_by_id`, `get_all`, `search`
- ✅ Cache pour éviter re-parsing

---

## ❌ Problème rencontré

### Le format gwu est PLUS complexe que prévu

**Complexité** :
1. **Structure imbriquée complexe**
   - Personnes définies dans plusieurs endroits
   - Événements séparés des définitions
   - Clés de liaison ambiguës

2. **Exemple de complexité** :
```
fam Galichet Jean_Pierre + Loche Marie_Elisabeth
...
beg
- h Jean_Charles 1813
- f Thérèse_Eugénie 7/9/1830
end

pevt Galichet Jean_Charles
#birt 1813
end pevt
```

**Problèmes** :
- `Jean_Charles` dans `beg` ≠ `Galichet Jean_Charles` dans `pevt`
- Clés format variable (`Surname FirstName` vs `FirstName SURNAME`)
- Occurrences (`.0`, `.1`) parfois présentes

3. **Parser actuel trop simpliste**
   - Ne gère pas toutes les variations
   - Liaison clés incorrecte
   - Personnes perdues entre blocs

---

## 📊 Temps investi vs Temps nécessaire

### Temps déjà investi
| Tâche | Temps |
|-------|-------|
| Analyse format gwu | 30 min |
| Implémentation parser | 1h |
| Intégration repository | 30 min |
| Debug | 30 min |
| **Total** | **2h30** |

### Temps encore nécessaire
| Tâche | Temps estimé |
|-------|--------------|
| Finir parser gwu correctement | 3-4h |
| Tester et corriger | 2h |
| Créer templates HTML | 3-4h |
| Faire passer tests golden master | 4-6h |
| **Total** | **12-16h** (~2 jours) |

---

## 💡 Réalité de l'Option A

### Estimation initiale
> "Option A : 1-2 jours" ⚠️ **SOUS-ESTIMÉ**

### Estimation réaliste
> "Option A : 2-3 jours" (avec parser gwu complet)

**Raisons** :
1. Format gwu plus complexe que prévu
2. Parsing manuel laborieux
3. Beaucoup de cas particuliers
4. Tests golden master exigeants

---

## 🔄 Options maintenant

### Option A.1 : Continuer parser gwu ⏱️ 2-3 jours
**Pour** :
- Déjà commencé
- Pas de dépendances OCaml
- Fonctionnera éventuellement

**Contre** :
- Encore 12-16h de travail
- Format gwu incomplet (pas toutes les infos)
- Maintenance difficile

### Option B : FFI OCaml (recommandé maintenant) ⏱️ 1-2 jours
**Pour** :
- Réutilise code OCaml existant
- Fiable et complet
- Moins de code à écrire

**Contre** :
- Nécessite OCaml installé
- Binding C/Python complexe

**Approche** :
```python
# Utiliser ctypes ou cffi
import ctypes
gwdb = ctypes.CDLL("libgwdb.so")
# Wrapper functions OCaml
```

### Option C : Abandonner parsing, utiliser API HTTP ⏱️ 1 jour
**Pour** :
- Très rapide
- Pas de parsing
- Réutilise gwd OCaml

**Contre** :
- Dépendance au serveur OCaml
- Pas vraiment une réécriture

**Approche** :
```python
# Lancer gwd OCaml en arrière-plan
# Faire des requêtes HTTP
# Récupérer HTML et le resservir
```

---

## 📝 Leçons apprises

### 1. Format de données ≠ Format d'export
- gwu est pour EXPORT, pas lecture efficace
- Conçu pour humains, pas machines
- Parsing manuel très laborieux

### 2. Estimation temps
- "1-2 jours" trop optimiste
- Format plus complexe que prévu
- Debugging prend du temps

### 3. Alternative mieux
- FFI OCaml probablement meilleur choix
- Ou migration SQL directe
- Parser gwu = solution de dernier recours

---

## 🎯 Recommandation finale

### ❌ Ne PAS continuer Option A (parser gwu)
**Raisons** :
1. Trop complexe pour bénéfice limité
2. Encore 12-16h de travail
3. Résultat incomplet (gwu ne contient pas tout)

### ✅ CHOISIR Option B (FFI OCaml)
**Raisons** :
1. Plus rapide finalement (1-2 jours)
2. Complet et fiable
3. Réutilise code OCaml existant et testé

**Plan B** :
1. Créer bindings Python → OCaml avec ctypes/cffi
2. Wrapper fonctions gwdb OCaml
3. Utiliser directement depuis Python
4. Faire passer les 44 tests

---

## 📂 Code créé (Option A)

### Fichiers modifiés
- ✅ `gwu_parser.py` (~250 lignes) - Parser incomplet mais base solide
- ✅ `gwdb_repository.py` (~130 lignes) - Repository avec intégration gwu

### Réutilisable ?
- ⚠️ Parser gwu : base OK mais nécessite refonte
- ✅ Repository : structure OK, juste changer source données

---

## 🚀 Prochaine étape suggérée

### Passer à Option B : FFI OCaml

**Étape 1** : Identifier fonctions OCaml à wrapper
```bash
# Dans lib/gwdb.ml ou gwdb-driver/
- person_of_key : string -> person
- person_get : base -> int -> person  
- family_get : base -> int -> family
```

**Étape 2** : Créer bindings Python
```python
# src/geneweb/adapters/database/ocaml_bindings.py
import ctypes
gwdb = ctypes.CDLL("path/to/gwdb.so")
```

**Étape 3** : Adapter repository
```python
# Remplacer gwu_parser par ocaml_bindings
```

**Temps estimé** : 1-2 jours (vs 2-3 pour finir gwu parser)

---

## 💭 Conclusion

**Option A tentée** : Parser gwu  
**Résultat** : Partiellement implémenté mais trop complexe  
**Temps investi** : 2h30  
**Temps encore nécessaire** : 12-16h

**Recommandation** : **Abandonner Option A**, **passer à Option B (FFI OCaml)**

**Nouvelle estimation Option B** : 1-2 jours (plus rapide que finir Option A !)

---

**Question** : Voulez-vous que je passe à **Option B (FFI OCaml)** ?

Tapez :
- **"B"** pour Option B (FFI OCaml) - Recommandé ✅
- **"A2"** pour continuer Option A (parser gwu) - Non recommandé
- **"C"** pour Option C (API HTTP) - Pragmatique mais pas une vraie réécriture
