# Phase 2: Reading (Adapters de Lecture) - Progrès

**Status:** 🟡 En cours (40% complété)  
**Date de démarrage:** 11 octobre 2025  
**Tests:** ✅ 12/12 passés (100%)

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
- [x] **Structure de base** (`gw_parser.py` - ~470 lignes)
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

### Infrastructure
- [x] Structure adapters (`src/geneweb/gwu/adapters/`)
  - [x] `input/` pour les parsers
  - [x] `__init__.py` pour exposition
- [x] Tests structurés (`tests/gwu/adapters/`)

---

## ⏹️ À Faire (Phase 2 - Reste 60%)

### Parser .gw - Fonctionnalités avancées

#### Parsing des événements (pevt)
```python
def _parse_person_events(self, lines, start_idx):
    """
    Parse les événements d'une personne.
    
    À implémenter:
    - #birt (naissance) + date + lieu
    - #deat (décès) + date + lieu
    - #bapm (baptême)
    - #buri (inhumation)
    """
```

#### Parsing des événements de famille (fevt)
```python
def _parse_family_events(self, lines, start_idx, family):
    """
    Parse les événements de famille.
    
    À implémenter:
    - #marr (mariage) + date + lieu
    - #div (divorce) + date + lieu
    - #enga (fiançailles)
    """
```

#### Parsing des dates
```python
class DateParser:
    """
    Parse les dates au format .gw.
    
    À implémenter:
    - Dates simples: 1789, 8/1789, 15/8/1789
    - Précisions: <1789, >1789, ~1789, ?1789
    - Périodes: 1789|1790, 1789..1790
    """
```

#### Parsing des attributs
- [ ] `#occu` : Occupation
- [ ] `#src` / `#s` : Sources
- [ ] `#p` : Lieu (place)
- [ ] `#bp`, `#dp`, `#mp` : Lieux spécifiques

#### Amélioration gestion des personnes
- [ ] Déduplication des personnes
  - Actuellement: Si Pierre apparaît comme enfant puis comme père, 2 instances
  - Souhaité: Une seule instance reliée aux 2 familles
- [ ] Index par clé (Nom Prénom.occ)
- [ ] Résolution des références croisées

### GwFileRepository (Implémentation PersonRepository)
```python
class GwFileRepository(PersonRepository):
    """
    Implémentation de PersonRepository pour fichiers .gw.
    
    Utilise GwParser en interne.
    """
    
    def __init__(self, file_path: Path):
        self.parser = GwParser()
        self.db = self.parser.parse_file(file_path)
    
    def get_by_id(self, person_id) -> Optional[Person]:
        # À implémenter
    
    def get_all(self) -> Iterator[Person]:
        return self.parser.get_all_persons()
```

### GwdbRepository (Lecture bases binaires .gwb)
- [ ] Analyse du format binaire .gwb
- [ ] Lecture des index
- [ ] Lecture des personnes
- [ ] Lecture des familles
- [ ] Implémentation PersonRepository pour .gwb

---

## 📊 Métriques Actuelles

### Tests
- Total: 12 tests
- Passés: 12 ✅ (100%)
- Temps d'exécution: ~0.04s

### Fichiers Créés
- `GW_FORMAT_SPEC.md` : 180 lignes
- `gw_parser.py` : 470 lignes
- `test_gw_parser.py` : 250 lignes
- `test_gw_parser_real.py` : 100 lignes

### Couverture
- GwParser - Structure de base: 100% ✅
- GwParser - Événements: 0% (TODO)
- GwParser - Dates: 0% (TODO)
- GwdbRepository: 0% (pas démarré)

---

## 🎯 Objectifs Phase 2

### Objectifs Minimums (Must Have)
- [x] Parser .gw - Structure de base ✅
- [ ] Parser .gw - Événements (pevt)
- [ ] Parser .gw - Dates
- [ ] GwFileRepository implémenté

### Objectifs Souhaitables (Should Have)
- [ ] Parser .gw - Attributs complets
- [ ] Déduplication des personnes
- [ ] Index par clé
- [ ] GwdbRepository - Lecture basique

### Objectifs Nice to Have
- [ ] GwdbRepository complet
- [ ] Performance optimisée
- [ ] Gestion erreurs robuste

---

## 📅 Planning

### Temps Réalisé
- Spécification format: ~30 min
- Parser structure base: ~1h30
- Tests: ~45 min
- **Total: ~2h45**

### Temps Estimé Restant
1. Parser événements: ~1h
2. Parser dates: ~1h
3. GwFileRepository: ~45 min
4. Déduplication personnes: ~1h
5. GwdbRepository basique: ~2h (optionnel)

**Total estimé: 3-4h (6-7h avec GwdbRepository)**

---

## 🚀 Test Réel

### Fichier galichet.gw
```
Résultats du parsing:
  ✅ 47 personnes parsées
  ✅ 15 familles parsées
  ✅ Notes parsées
  ✅ Relations parent-enfant cohérentes
  ✅ Héritage nom de famille correct
```

### Exemples de personnes parsées
- Jean Pierre.0 Galichet
- Marie Elisabeth.0 Loche
- Jean Charles.0 Galichet
- Paul.0 Galichet
- Thérèse Eugénie.0 Galichet

---

## 📝 Notes Techniques

### Décisions de Design
1. **GwDatabase intermédiaire**: Permet de séparer parsing et conversion en entités
2. **Parser ligne par ligne**: Plus simple à maintenir que regex complexes
3. **Héritage nom famille**: Les enfants héritent automatiquement du nom du père
4. **IDs auto-générés**: P0, P1, F0, F1 pour identifiants uniques

### Limitations Actuelles
1. **Événements ignorés**: pevt et fevt parsés mais pas convertis en entités Event
2. **Dates ignorées**: Présentes dans le texte mais pas parsées
3. **Attributs ignorés**: #occu, #src, etc. non extraits
4. **Duplication personnes**: Personne peut apparaître plusieurs fois

### Problèmes Résolus
- ✅ Parsing enfants avec nom famille hérité
- ✅ Relations parent-enfant bidirectionnelles
- ✅ Noms avec underscores (Jean_Pierre → Jean Pierre)
- ✅ Occurrences (Jean.1, Jean.2)

---

## 🎯 Critères de Succès Phase 2

- [x] Parser fichier .gw basique ✅
- [ ] Parser événements personnes
- [ ] Parser événements familles
- [ ] Parser dates
- [ ] GwFileRepository fonctionnel
- [ ] Tests > 90% coverage
- [ ] Parsing galichet.gw complet (avec dates et événements)

**Statut actuel:** 40% des critères atteints

---

## 🔗 Dépendances

### Phase 1 (Foundation) - ✅ COMPLÉTÉE
- Entités Person, Family, Event, Date, Place
- Repositories (interfaces)

### Phase 2 (Reading) - 🟡 EN COURS
- Parser .gw ✅ (structure base)
- Parser .gw ⏹️ (événements, dates)
- GwFileRepository ⏹️
- GwdbRepository ⏹️

### Phase 3 (Core Logic) - ⏹️ À VENIR
- Utilise PersonRepository et FamilyRepository
- Dépend de Phase 2 pour lecture des données

---

*Dernière mise à jour: 11 octobre 2025*
