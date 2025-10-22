# Stratégie de réécriture GWD → Python

**Objectif**: Recréer le binaire OCaml `gwd` en Python avec une architecture clean et modulaire.

**Approche**: Test-Driven Rewrite (TDR) - Les 44 tests existants valident chaque étape.

---

## 🎯 Principe directeur

> **"Même comportement, meilleure architecture"**

- ✅ Reproduire exactement la sortie de gwd OCaml
- ✅ Valider avec les 44 golden masters/integration tests
- ✅ Architecture moderne, testable, maintenable

---

## 📊 État actuel

### Tests disponibles (44 total)

| Type | Nombre | Description |
|------|--------|-------------|
| Golden Master | 25 | Comparaison HTML bit-à-bit |
| Integration | 19 | Tests comportementaux |

### Phases d'implémentation

| Phase | Objectif | Tests visés | Statut |
|-------|----------|-------------|--------|
| **0** | Infrastructure | 0 | ✅ Terminée |
| **1** | Routing HTTP | 5 | ⏳ En cours |
| **2** | Base de données | 10 | ⏳ À venir |
| **3** | Templates | 15 | ⏳ À venir |
| **4** | Authentification | 20 | ⏳ À venir |
| **5** | Features avancées | 44 | ⏳ À venir |

---

## 🔄 Méthodologie TDR (Test-Driven Rewrite)

### 1. Sélectionner un test
```bash
# Exemple: test basic homepage
./test/gwd_test.sh verify basic
```

### 2. Analyser le code OCaml correspondant
```bash
# Trouver la fonction dans le code source
grep -r "homepage" lib/
```

### 3. Implémenter en Python
```python
# Reproduire la logique avec architecture clean
@app.get("/{base}")
async def homepage(base: str):
    person_repo = get_person_repository(base)
    # ...
```

### 4. Vérifier le test
```bash
# Le test doit passer
./test/gwd_test.sh verify basic
```

### 5. Refactorer si besoin
```python
# Améliorer sans casser le test
```

### 6. Passer au test suivant

---

## 📝 Plan détaillé par phase

### Phase 0: Infrastructure ✅ (Terminée)

**Durée**: 1h  
**Tests**: 0/44

#### Livrables
- [x] Structure projet (hexagonal)
- [x] Configuration (Pydantic)
- [x] CLI (argparse → toutes options gwd)
- [x] Serveur FastAPI minimal
- [x] Package installable

#### Validation
```bash
pip install -e ".[dev]"
python -m geneweb.cli.main --help
```

---

### Phase 1: Routing HTTP ⏳ (En cours)

**Durée estimée**: 2-3h  
**Tests visés**: 5/44 (basic)

#### Objectifs
1. **Routes principales**
   ```python
   GET /{base}                    # Homepage
   GET /{base}/person?i=N         # Fiche personne
   GET /{base}/family?i=N         # Fiche famille
   GET /{base}/desc?i=N           # Descendance
   GET /{base}/anc?i=N            # Ascendance
   ```

2. **Middleware**
   - Logging (structlog)
   - Error handling
   - Request timing

3. **Tests à passer**
   - `basic_homepage` ✅
   - `basic_robots` ✅
   - `basic_person` ⏳
   - `basic_family` ⏳
   - `basic_desc` ⏳

#### Code OCaml à analyser
```
lib/gwd.ml                 # Main entry
lib/gwdLib.ml              # Core logic
lib/updateData.ml          # Update logic
lib/perso.ml               # Person display
```

---

### Phase 2: Base de données ⏳

**Durée estimée**: 4-5h  
**Tests visés**: 10/44

#### Objectifs
1. **Lecture format binaire GeneWeb**
   - Parser `.gwb` files
   - Index person/family
   - Relations (parents, enfants)

2. **Entities**
   ```python
   @dataclass
   class Person:
       id: int
       first_name: str
       surname: str
       # ...
   ```

3. **Repository Pattern**
   ```python
   class PersonRepository(Protocol):
       def get_by_id(self, id: int) -> Person: ...
       def search(self, name: str) -> list[Person]: ...
   ```

#### Fichiers OCaml à étudier
```
lib/gwdb.ml               # Database interface
lib/gwdb-driver/         # Binary format
lib/def.ml               # Type definitions
```

#### Tests à passer
- Tous les tests `basic_*`
- Tests `person_*` (fiche personne détaillée)

---

### Phase 3: Templates & Rendering ⏳

**Durée estimée**: 3-4h  
**Tests visés**: 15/44

#### Objectifs
1. **Templates Jinja2**
   - Convertir templates OCaml → Jinja2
   - Variables, filtres, macros
   - Layouts/includes

2. **Normalisation HTML**
   - Même structure que OCaml
   - Tests golden master passent

3. **Multi-langue**
   - Support `-lang`
   - Lexicons

#### Templates à convertir
```
hd/etc/*.txt              # Templates OCaml
→
templates/                # Templates Jinja2
  ├── base.html
  ├── person.html
  ├── family.html
  └── ...
```

#### Tests à passer
- Tests `trees_*`
- Tests `lists_*`

---

### Phase 4: Authentification ⏳

**Durée estimée**: 2-3h  
**Tests visés**: 20/44

#### Objectifs
1. **Basic Auth**
   ```python
   from fastapi.security import HTTPBasic
   
   @app.get("/{base}/admin")
   async def admin(credentials: HTTPBasicCredentials):
       # Validate against -auth file
   ```

2. **Digest Auth** (optionnel si `-digest`)
   ```python
   # MD5 challenge-response
   ```

3. **Friend/Wizard modes**
   ```python
   if settings.wizard_password:
       # Wizard access
   if settings.friend_password:
       # Friend access
   ```

#### Fichiers OCaml
```
lib/updateDataDisplay.ml  # Auth logic
lib/secure.ml             # Security
```

#### Tests à passer
- Tests `auth_*` (7 tests)
- Tests `admin_*`

---

### Phase 5: Features avancées ⏳

**Durée estimée**: 5-7h  
**Tests visés**: 44/44

#### Objectifs
1. **Recherche**
   - Par nom
   - Par lieu
   - Par date

2. **Arbres**
   - Ascendance
   - Descendance
   - Arbre complet

3. **Statistiques**
   - Par âge
   - Par lieu
   - Par profession

4. **Options avancées**
   - `-redirect`
   - `-plugin`/`-plugins`
   - `-cgi` mode
   - `-add_lexicon`

#### Tests à passer
- Tous les tests restants
- Tests integration (network, cache, etc.)

---

## 🧪 Validation continue

### À chaque commit

```bash
# Linter + types
ruff src/
mypy src/

# Tests unitaires
pytest tests/

# Golden masters
./test/gwd_test.sh verify all

# Integration tests
python test/gwd_integration_tests.py all
```

### Critère de succès

| Indicateur | Cible | Actuel |
|------------|-------|--------|
| Tests passés | 44/44 | 0/44 |
| Couverture code | >80% | TBD |
| Type safety | 100% | 100% |
| Performance | ~= OCaml | TBD |

---

## 📈 Progression

```
Phase 0: ████████████████████ 100% ✅
Phase 1: ░░░░░░░░░░░░░░░░░░░░   0% ⏳
Phase 2: ░░░░░░░░░░░░░░░░░░░░   0%
Phase 3: ░░░░░░░░░░░░░░░░░░░░   0%
Phase 4: ░░░░░░░░░░░░░░░░░░░░   0%
Phase 5: ░░░░░░░░░░░░░░░░░░░░   0%

Global: ███░░░░░░░░░░░░░░░░░ 16% (Phase 0 terminée)
```

---

## 🚀 Prochaines actions

### Immédiat (Phase 1)
1. Créer `PersonRepository` interface
2. Implémenter lecture `.gwb` (minimal)
3. Route `GET /{base}/person?i=N`
4. Passer `basic_person` test

### Court terme (Phase 1-2)
1. Tous les tests `basic_*`
2. Lecture complète base de données
3. Relations familiales

### Moyen terme (Phase 3-4)
1. Templates Jinja2
2. Multi-langue
3. Authentification

### Long terme (Phase 5)
1. Features avancées
2. Optimisations
3. 44/44 tests ✅

---

## 🎯 Success Criteria

### Fonctionnel
- ✅ 44/44 tests passent
- ✅ Même output HTML que OCaml
- ✅ Toutes les options CLI supportées

### Qualité
- ✅ Architecture clean/hexagonal
- ✅ 100% type hints
- ✅ >80% couverture tests
- ✅ Code formaté (black/ruff)

### Performance
- ✅ Temps réponse < 2x OCaml
- ✅ Mémoire < 2x OCaml
- ✅ Capable de gérer bases réelles

---

**Dernière mise à jour**: Phase 0 terminée (8 oct 2025)  
**Prochaine étape**: Phase 1 - Routing HTTP  
**Tests**: 0/44 ✅
