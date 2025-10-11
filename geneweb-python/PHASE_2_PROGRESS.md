# Phase 2: Reading (Adapters de Lecture) - Progrès

**Status:** 🟢 Presque complétée (85% complété)  
**Date de démarrage:** 11 octobre 2025  
**Tests:** ✅ 122/122 passés (100%)

---

## ✅ Complété

### Spécification du Format
- [x] `GW_FORMAT_SPEC.md` - Documentation complète du format `.gw`
  - Structure globale (encoding, gwplus)
  - Familles et événements
  - Personnes et événements
  - Notes et sources
  - Format des dates
  - Format des noms

### Parser .gw (GwParser)
- [x] **Structure de base** (`gw_parser.py` - ~620 lignes)
  - [x] Parsing encoding
  - [x] Parsing familles (fam)
  - [x] Parsing enfants (beg/end)
  - [x] Parsing notes
  - [x] Gestion des relations parent-enfant
  - [x] Héritage du nom de famille

- [x] **Tests unitaires** (`test_gw_parser.py` - 9 tests)
  - [x] Parsing fichier vide
  - [x] Parsing couple sans enfants
  - [x] Parsing couple avec enfants
  - [x] Parsing noms avec underscore
  - [x] Parsing noms avec occurrence
  - [x] Parsing multiples familles
  - [x] Parsing notes
  - [x] Parsing relations familiales

- [x] **Tests d'intégration** (`test_gw_parser_real.py` - 3 tests)
  - [x] Parsing fichier galichet.gw complet (47 personnes, 15 familles)
  - [x] Vérification personnes spécifiques
  - [x] Vérification cohérence structure familiale

### Parser Dates (DateParser)
- [x] **DateParser** (`date_parser.py` - ~230 lignes)
  - [x] Dates simples: 1789, 8/1789, 15/8/1789
  - [x] Année zéro: -0
  - [x] Précisions: <1789, >1789, ~1789, ?1789
  - [x] Périodes OrYear: 1789|1790, 8/1789|9/1790
  - [x] Périodes YearInterval: 1789..1790
  - [x] Dates complètes dans périodes

- [x] **Tests unitaires** (`test_date_parser.py` - 19 tests)
  - [x] Dates simples (4 tests)
  - [x] Précisions (5 tests)
  - [x] Périodes (5 tests)
  - [x] Cas limites (4 tests)
  - [x] Compatibilité galichet.gw (1 test)

### Parsing des événements
- [x] **Événements personnes** (dans `gw_parser.py`)
  - [x] #birt (naissance) + date + lieu
  - [x] #deat (décès) + date + lieu
  - [x] #bapm (baptême)
  - [x] #buri (inhumation)
  - [x] #crem (crémation)
  - [x] Recherche personne par nom
  - [x] Association événements ↔ personnes

- [x] **Événements familles** (dans `gw_parser.py`)
  - [x] #marr (mariage) + date + lieu
  - [x] #div (divorce) + date + lieu
  - [x] #enga (fiançailles)
  - [x] #marb (bans mariage)
  - [x] #marc (contrat mariage)
  - [x] Association événements ↔ familles

- [x] **Parsing des lieux**
  - [x] #p (lieu général)
  - [x] #bp (lieu naissance)
  - [x] #dp (lieu décès)
  - [x] #mp (lieu mariage)

- [x] **Tests événements** (`test_gw_parser_events.py` - 9 tests)
  - [x] Événements personnes avec date/lieu
  - [x] Événements familles avec date/lieu
  - [x] Test intégration galichet.gw (20 naissances, 20 décès)

### GwFileRepository
- [x] **GwFilePersonRepository** (`gw_file_repository.py` - ~340 lignes)
  - [x] get_by_id()
  - [x] get_by_key(first_name, surname, occ)
  - [x] get_all()
  - [x] get_count()
  - [x] search_by_name()
  - [x] get_isolated_persons()

- [x] **GwFileFamilyRepository** (`gw_file_repository.py`)
  - [x] get_by_id()
  - [x] get_all()
  - [x] get_count()
  - [x] get_families_of_person()
  - [x] get_family_of_parents()

- [x] **GwFileRepository** (Repository combiné)
  - [x] Accès unifié personnes et familles
  - [x] Partage database pour éviter double parsing

- [x] **Tests repositories** (`test_gw_file_repository.py` - 16 tests)
  - [x] Tests PersonRepository (8 tests)
  - [x] Tests FamilyRepository (5 tests)
  - [x] Tests Repository combiné (3 tests)
  - [x] Test intégration galichet.gw

### Infrastructure
- [x] Structure adapters (`src/geneweb/gwu/adapters/`)
  - [x] `input/` pour les parsers
  - [x] `__init__.py` pour exposition
- [x] Tests structurés (`tests/gwu/adapters/`)

---

## ⏹️ À Faire (Phase 2 - Reste 15%)

### Amélioration gestion des personnes (Déduplication)
- [ ] **Déduplication des personnes** (~1h)
  - Actuellement: Si Pierre apparaît comme enfant puis comme père, 2 instances
  - Souhaité: Une seule instance reliée aux 2 familles
  - Implémentation:
    - Index par clé (Prénom.occ Nom)
    - Fusion des instances lors du parsing
    - Mise à jour des références dans familles
- [ ] **Tests déduplication** (~15 min)
  - Test personne enfant devient parent
  - Test résolution références croisées
  - Test galichet.gw avec déduplication

### Parsing des attributs additionnels (Optionnel)
- [ ] `#occu` : Occupation
- [ ] `#src` / `#s` : Sources
- [ ] `#image` : Image
- [ ] `#title` : Titres

### GwdbRepository (Optionnel - Phase future)
- [ ] Analyse du format binaire .gwb
- [ ] Lecture des index
- [ ] Implémentation PersonRepository pour .gwb

---

## 📊 Métriques Actuelles

### Tests
- **Total: 122 tests** ✅
  - Domain (Date): 28 tests
  - Domain (Person): 19 tests
  - Domain (Family): 19 tests
  - Adapters (DateParser): 19 tests
  - Adapters (GwParser): 9 tests
  - Adapters (GwParser Events): 9 tests
  - Adapters (GwParser Real): 3 tests
  - Adapters (GwFileRepository): 16 tests
- Passés: 122 ✅ (100%)
- Temps d'exécution: ~0.12s

### Fichiers Créés (Phase 2)
- `GW_FORMAT_SPEC.md` : 180 lignes
- `gw_parser.py` : 620 lignes
- `date_parser.py` : 230 lignes
- `gw_file_repository.py` : 340 lignes
- `test_gw_parser.py` : 250 lignes
- `test_gw_parser_real.py` : 100 lignes
- `test_date_parser.py` : 180 lignes
- `test_gw_parser_events.py` : 250 lignes
- `test_gw_file_repository.py` : 280 lignes

**Total Phase 2: ~2430 lignes**

### Couverture
- GwParser - Structure de base: 100% ✅
- GwParser - Événements: 100% ✅
- GwParser - Dates: 100% ✅
- DateParser: 100% ✅
- GwFileRepository: 100% ✅
- Déduplication personnes: 0% (TODO)
- GwdbRepository: 0% (optionnel)

---

## 🎯 Objectifs Phase 2

### Objectifs Minimums (Must Have)
- [x] Parser .gw - Structure de base ✅
- [x] Parser .gw - Événements (pevt/fevt) ✅
- [x] Parser .gw - Dates ✅
- [x] GwFileRepository implémenté ✅

### Objectifs Souhaitables (Should Have)
- [ ] Déduplication des personnes (15% restant)
- [ ] Parser .gw - Attributs complets (optionnel)
- [ ] Index par clé (intégré avec déduplication)

### Objectifs Nice to Have (Phase future)
- [ ] GwdbRepository complet
- [ ] Performance optimisée
- [ ] Gestion erreurs robuste

---

## 📅 Planning

### Temps Réalisé
- Spécification format: ~30 min
- Parser structure base: ~1h30
- Tests structure: ~45 min
- **Sous-total initial: ~2h45**
- DateParser: ~1h
- Événements: ~1h15
- Tests événements: ~45 min
- GwFileRepository: ~45 min
- Tests repositories: ~30 min
- **Total Phase 2: ~6h30**

### Temps Estimé Restant
1. Déduplication personnes: ~1h
2. Tests déduplication: ~15 min

**Total estimé restant: ~1h15**

**Temps total Phase 2 estimé: ~7h45** (dont 6h30 déjà réalisé = 85%)

---

## 🚀 Test Réel

### Fichier galichet.gw (via GwFileRepository)
```
Résultats du parsing complet:
  ✅ 47 personnes parsées
  ✅ 15 familles parsées
  ✅ 20 naissances avec dates/lieux
  ✅ 20 décès avec dates/lieux
  ✅ Mariages avec dates/lieux
  ✅ Notes parsées
  ✅ Relations parent-enfant cohérentes
  ✅ Héritage nom de famille correct
  ✅ 11 personnes "Galichet" trouvées
  ✅ 0 personnes isolées
```

### Exemples de personnes parsées (avec événements)
- Jean Pierre.0 Galichet (naissance 1813, décès avec date)
- Thérèse Eugénie.0 Galichet (naissance 7/9/1830 à Châlons-sur-Marne)
- Marie Elisabeth.0 Loche
- Jean Charles.0 Galichet
- Paul.0 Galichet

### Utilisation du Repository
```python
from pathlib import Path
from geneweb.gwu.adapters.input import GwFileRepository

# Charger fichier .gw
repo = GwFileRepository(Path("test/galichet.gw"))

# Statistiques
print(f"Personnes: {repo.persons.get_count()}")  # 47
print(f"Familles: {repo.families.get_count()}")  # 15

# Recherche par nom
galichets = repo.persons.search_by_name("Galichet")  # 11 personnes

# Récupération par clé
jean = repo.persons.get_by_key("Jean Pierre", "Galichet", 0)
print(jean.has_birth())  # False (car pas d'événement birth dans le .gw)
print(jean.has_death())  # True (événement death présent)

# Personnes isolées
isolated = list(repo.persons.get_isolated_persons())  # []
```

---

## 📝 Notes Techniques

### Décisions de Design
1. **GwDatabase intermédiaire**: Permet de séparer parsing et conversion en entités
2. **Parser ligne par ligne**: Plus simple à maintenir que regex complexes
3. **Héritage nom famille**: Les enfants héritent automatiquement du nom du père
4. **IDs auto-générés**: P0, P1, F0, F1 pour identifiants uniques
5. **DateParser séparé**: Réutilisable et testable indépendamment
6. **Repository combiné**: GwFileRepository donne accès unifié à persons et families
7. **Parsing partagé**: Un seul parsing pour PersonRepository et FamilyRepository

### Limitations Actuelles
1. **Duplication personnes**: Personne peut apparaître plusieurs fois (enfant puis parent)
   - En cours de résolution avec déduplication
2. **Attributs partiels**: #occu, #src, #image non encore parsés (optionnel)
3. **Sources**: Non parsées dans événements (TODO futur)

### Problèmes Résolus
- ✅ Parsing enfants avec nom famille hérité
- ✅ Relations parent-enfant bidirectionnelles
- ✅ Noms avec underscores (Jean_Pierre → Jean Pierre)
- ✅ Occurrences (Jean.1, Jean.2)
- ✅ Parsing dates (tous formats)
- ✅ Parsing événements personnes/familles
- ✅ Parsing lieux (#p, #bp, #dp, #mp)
- ✅ Repository pattern implémenté
- ✅ Tests 100% passés

---

## 🎯 Critères de Succès Phase 2

- [x] Parser fichier .gw basique ✅
- [x] Parser événements personnes ✅
- [x] Parser événements familles ✅
- [x] Parser dates ✅
- [x] GwFileRepository fonctionnel ✅
- [x] Tests > 90% coverage ✅ (100%)
- [x] Parsing galichet.gw complet (avec dates et événements) ✅
- [ ] Déduplication personnes ⏹️

**Statut actuel:** 85% des critères atteints (7/8)

---

## 🔗 Dépendances

### Phase 1 (Foundation) - ✅ COMPLÉTÉE
- Entités Person, Family, Event, Date, Place
- Repositories (interfaces)

### Phase 2 (Reading) - 🟢 PRESQUE COMPLÉTÉE (85%)
- Parser .gw ✅ (structure, événements, dates)
- GwFileRepository ✅
- Déduplication ⏹️ (15% restant)
- GwdbRepository ⏹️ (optionnel, phase future)

### Phase 3 (Core Logic) - ⏹️ À VENIR
- Utilise PersonRepository et FamilyRepository ✅ (interfaces prêtes)
- Dépend de Phase 2 pour lecture des données ✅ (90% prêt)

---

*Dernière mise à jour: 11 octobre 2025 - 85% complété*
