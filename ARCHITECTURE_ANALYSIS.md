# 🏗️ Analyse Architecture GWD & Proposition Python

**Objectif** : Réécrire `gwd` (GeneWeb Web Daemon) en Python avec une architecture clean et modulaire

**Stratégie** : Utiliser les 44 tests existants comme suite de validation

> ⚠️ **IMPORTANT** : On ne cherche PAS à porter le code OCaml ligne par ligne !
> On crée une **nouvelle implémentation Python moderne** qui produit le **même résultat**.
> Les tests garantissent que le comportement externe est identique.

## 🎯 Approche : Réécriture, Pas Portage

### ❌ Ce qu'on NE fait PAS

- ❌ Porter le code OCaml ligne par ligne
- ❌ Reproduire l'architecture monolithique
- ❌ Garder les refs mutables globales
- ❌ Copier la logique complexe d'OCaml

### ✅ Ce qu'on FAIT

- ✅ **Repenser l'architecture** : Clean Architecture moderne
- ✅ **Simplifier la logique** : Code Python idiomatique
- ✅ **Utiliser le meilleur de Python** : async, types, patterns modernes
- ✅ **Garantir le résultat** : Les 44 tests comme contrat

### 🧪 Les Tests = Contrat de Comportement

```
Input (HTTP Request)  →  [Boîte Noire]  →  Output (HTML/JSON)
                              ↓
                    L'implémentation interne
                    peut être TOTALEMENT différente
                    tant que Input→Output est identique
```

**Exemple concret** :

```python
# OCaml fait ça (compliqué avec refs)
let auth_file = ref ""
let check_auth () = 
  if !auth_file = "" then false
  else read_auth_file !auth_file

# Python peut faire ça (simple et clair)
@dataclass
class AuthService:
    auth_file: Optional[Path]
    
    def check_auth(self, credentials: str) -> bool:
        if not self.auth_file:
            return False
        return self._validate(credentials)
```

**Résultat identique, code meilleur !**

---

## 📊 Analyse de l'Architecture OCaml Existante

### Structure Actuelle (gwd.ml - 2511 lignes)

#### 1. **Core Components**

```ocaml
// Modules principaux
open Geneweb
open Config
open Def
open Util
open Gwd_lib
module Wserver = ...  // Serveur HTTP
module Driver = ...   // Base de données
```

#### 2. **Configuration Globale** (refs mutable)

```ocaml
let auth_file = ref ""
let cache_langs = ref []
let selected_port = ref 2317
let wizard_passwd = ref ""
let friend_passwd = ref ""
let redirected_addr = ref None
let robot_xcl = ref None
// ... ~40 refs de configuration
```

#### 3. **Flow Principal**

```
main()
  ↓
geneweb_server() ou geneweb_cgi()
  ↓
Wserver.start() // démarre serveur HTTP
  ↓
connection() // handle chaque connexion
  ↓
conf_and_connection() // routing et auth
  ↓
Handle request (perso, update, search, etc.)
```

#### 4. **Modules Fonctionnels**

| Module | Responsabilité |
|--------|---------------|
| `Wserver` | Serveur HTTP, workers, timeouts |
| `Config` | Configuration requête |
| `Auth` | Authentification (Basic, Digest) |
| `Robot` | Détection robots |
| `Perso` | Pages personne |
| `Search` | Recherche |
| `Update` | Modification données |
| `Stats` | Statistiques |
| `Image` | Gestion images |

### 🔍 Points clés identifiés

1. **Architecture monolithique** : Un seul fichier principal
2. **État global mutable** : Refs partout
3. **Pas de séparation claire** : Business logic mélangée avec HTTP
4. **Routing implicite** : Basé sur paramètres `m=XXX`
5. **Authentification custom** : Basic + Digest
6. **Workers** : Fork-based (Unix) ou threads
7. **Base de données** : Driver abstrait

---

## 🐍 Proposition Architecture Python Clean

### Principes

- ✅ **Separation of Concerns** : Couches bien définies
- ✅ **Dependency Injection** : Pas d'état global
- ✅ **Testabilité** : Chaque composant testable isolément
- ✅ **Type Safety** : Type hints partout
- ✅ **Async/Await** : Pour performance
- ✅ **Clean Architecture** : Domain → Use Cases → Adapters

### Architecture Proposée (Hexagonale/Clean)

```
geneweb-python/
├── domain/                    # ❶ Domaine métier (indépendant)
│   ├── entities/              # Entités métier
│   │   ├── person.py
│   │   ├── family.py
│   │   ├── event.py
│   │   └── base.py
│   ├── value_objects/         # Value objects
│   │   ├── date.py
│   │   ├── place.py
│   │   └── sosa.py
│   └── repositories/          # Interfaces repositories (abstraction)
│       ├── person_repository.py
│       └── family_repository.py
│
├── use_cases/                 # ❷ Cas d'usage (logique métier)
│   ├── person/
│   │   ├── get_person.py
│   │   ├── search_person.py
│   │   └── update_person.py
│   ├── family/
│   │   ├── get_family.py
│   │   └── get_ancestors.py
│   ├── auth/
│   │   ├── authenticate.py
│   │   └── check_permissions.py
│   └── stats/
│       └── get_statistics.py
│
├── adapters/                  # ❸ Adapters (infrastructure)
│   ├── web/                   # Adapter HTTP
│   │   ├── app.py            # FastAPI/Flask app
│   │   ├── routers/          # Routes HTTP
│   │   │   ├── person.py
│   │   │   ├── family.py
│   │   │   ├── search.py
│   │   │   └── admin.py
│   │   ├── middleware/       # Middlewares
│   │   │   ├── auth.py
│   │   │   ├── robot.py
│   │   │   └── logging.py
│   │   └── presenters/       # Formatage réponses
│   │       ├── html.py
│   │       └── json.py
│   │
│   ├── database/             # Adapter BDD
│   │   ├── gwdb_adapter.py  # Lire bases GeneWeb
│   │   ├── models.py        # ORM models
│   │   └── repositories/    # Implémentations
│   │       ├── person_repo_impl.py
│   │       └── family_repo_impl.py
│   │
│   ├── templates/            # Templates HTML
│   │   ├── base.html
│   │   ├── person.html
│   │   └── tree.html
│   │
│   └── config/               # Configuration
│       ├── settings.py
│       └── dependencies.py
│
├── application/               # ❹ Application (orchestration)
│   ├── dto/                  # Data Transfer Objects
│   │   ├── person_dto.py
│   │   └── family_dto.py
│   ├── services/             # Services applicatifs
│   │   ├── person_service.py
│   │   └── tree_service.py
│   └── exceptions/           # Exceptions custom
│       └── errors.py
│
├── infrastructure/            # ❺ Infrastructure
│   ├── server/               # Serveur HTTP
│   │   ├── fastapi_server.py
│   │   └── workers.py
│   ├── auth/                 # Authentification
│   │   ├── basic_auth.py
│   │   ├── digest_auth.py
│   │   └── passwords.py
│   ├── cache/                # Cache
│   │   └── redis_cache.py
│   └── logger/               # Logging
│       └── logger.py
│
├── cli/                       # ❻ CLI
│   └── main.py               # Point d'entrée
│
├── tests/                     # ❼ Tests (existants + nouveaux)
│   ├── golden/               # Tests existants
│   ├── integration/          # Tests intégration
│   └── unit/                 # Tests unitaires
│       ├── domain/
│       ├── use_cases/
│       └── adapters/
│
└── pyproject.toml            # Configuration projet
```

---

## 🔧 Stack Technique Proposée

### Core

| Technologie | Usage |
|-------------|-------|
| **FastAPI** | Framework web async moderne |
| **Pydantic** | Validation données + types |
| **SQLAlchemy** | ORM (si migration BDD) |
| **Jinja2** | Templates HTML |
| **structlog** | Logging structuré |

### Infrastructure

| Technologie | Usage |
|-------------|-------|
| **uvicorn** | Serveur ASGI |
| **gunicorn** | Process manager |
| **redis** | Cache (optionnel) |
| **pytest** | Tests |

### Qualité

| Technologie | Usage |
|-------------|-------|
| **mypy** | Type checking |
| **ruff** | Linting rapide |
| **black** | Formatting |
| **coverage** | Couverture tests |

---

## 📝 Implémentation Progressive

### Phase 1 : Infrastructure de base (1-2 semaines)

**Objectif** : Serveur HTTP fonctionnel avec routing

```python
# cli/main.py
from infrastructure.server import GwdServer
from adapters.config import Settings

def main():
    settings = Settings.from_args()
    server = GwdServer(settings)
    server.run()
```

```python
# adapters/web/app.py
from fastapi import FastAPI
from adapters.web.routers import person, family

app = FastAPI(title="GeneWeb")
app.include_router(person.router)
app.include_router(family.router)
```

**Tests validés** : Options serveur (`-p`, `-bd`, `-hd`)

### Phase 2 : Lecture base de données (2-3 semaines)

**Objectif** : Lire bases GeneWeb existantes

```python
# adapters/database/gwdb_adapter.py
class GwdbAdapter:
    """Adapter pour lire bases GeneWeb binaires"""
    
    def read_person(self, iper: int) -> Person:
        # Lire format binaire GeneWeb
        pass
    
    def read_family(self, ifam: int) -> Family:
        pass
```

**Tests validés** : Affichage personnes, familles

### Phase 3 : Authentification (1 semaine)

**Objectif** : Basic + Digest auth

```python
# infrastructure/auth/basic_auth.py
class BasicAuthProvider:
    def authenticate(self, credentials: str) -> User:
        pass
```

**Tests validés** : Tests auth (5 scénarios)

### Phase 4 : Pages principales (2-3 semaines)

**Objectif** : Pages personne, arbres, recherche

```python
# use_cases/person/get_person.py
class GetPersonUseCase:
    def __init__(self, person_repo: PersonRepository):
        self.person_repo = person_repo
    
    def execute(self, person_id: int) -> PersonDTO:
        person = self.person_repo.get(person_id)
        return PersonDTO.from_entity(person)
```

**Tests validés** : Golden masters (25 tests)

### Phase 5 : Options avancées (1-2 semaines)

**Objectif** : Plugins, redirection, etc.

**Tests validés** : Tests avancés (5 tests)

---

## 🎯 Exemple Concret : Route "Person"

### 1. Domain (indépendant de tout)

```python
# domain/entities/person.py
from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Person:
    """Entité Person (domain)"""
    id: int
    first_name: str
    surname: str
    birth_date: Optional[date]
    birth_place: Optional[str]
    
    def get_full_name(self) -> str:
        return f"{self.first_name} {self.surname}"
```

### 2. Use Case (logique métier)

```python
# use_cases/person/get_person.py
from domain.entities.person import Person
from domain.repositories.person_repository import PersonRepository
from application.dto.person_dto import PersonDTO

class GetPersonUseCase:
    def __init__(self, person_repo: PersonRepository):
        self._person_repo = person_repo
    
    def execute(self, person_id: int) -> PersonDTO:
        person = self._person_repo.get_by_id(person_id)
        if not person:
            raise PersonNotFound(person_id)
        return PersonDTO.from_entity(person)
```

### 3. Repository Implementation (adapter)

```python
# adapters/database/repositories/person_repo_impl.py
from domain.repositories.person_repository import PersonRepository
from domain.entities.person import Person
from adapters.database.gwdb_adapter import GwdbAdapter

class GwdbPersonRepository(PersonRepository):
    def __init__(self, gwdb: GwdbAdapter):
        self._gwdb = gwdb
    
    def get_by_id(self, person_id: int) -> Optional[Person]:
        # Lire depuis base GeneWeb binaire
        raw_data = self._gwdb.read_person(person_id)
        return self._to_entity(raw_data)
```

### 4. HTTP Router (adapter web)

```python
# adapters/web/routers/person.py
from fastapi import APIRouter, Depends, HTTPException
from use_cases.person.get_person import GetPersonUseCase
from adapters.web.presenters.html import render_person_html

router = APIRouter(prefix="/person")

@router.get("/{person_id}")
async def get_person(
    person_id: int,
    use_case: GetPersonUseCase = Depends()
):
    try:
        person_dto = use_case.execute(person_id)
        return render_person_html(person_dto)
    except PersonNotFound:
        raise HTTPException(404, "Person not found")
```

### 5. Dependency Injection

```python
# adapters/config/dependencies.py
from fastapi import Depends
from adapters.database.gwdb_adapter import GwdbAdapter
from adapters.database.repositories.person_repo_impl import GwdbPersonRepository
from use_cases.person.get_person import GetPersonUseCase

def get_gwdb_adapter() -> GwdbAdapter:
    return GwdbAdapter(base_path="/path/to/bases")

def get_person_repository(
    gwdb: GwdbAdapter = Depends(get_gwdb_adapter)
) -> GwdbPersonRepository:
    return GwdbPersonRepository(gwdb)

def get_person_use_case(
    repo: GwdbPersonRepository = Depends(get_person_repository)
) -> GetPersonUseCase:
    return GetPersonUseCase(repo)
```

---

## ✅ Avantages de cette Architecture

### 1. **Testabilité**
```python
# Tests isolés sans dépendances
def test_get_person_use_case():
    # Mock repository
    mock_repo = Mock(PersonRepository)
    mock_repo.get_by_id.return_value = Person(...)
    
    # Test use case isolé
    use_case = GetPersonUseCase(mock_repo)
    result = use_case.execute(123)
    
    assert result.id == 123
```

### 2. **Maintenabilité**
- Chaque couche a sa responsabilité
- Changement BDD → modifier seulement adapters
- Changement UI → modifier seulement presenters

### 3. **Évolutivité**
- Ajouter une nouvelle feature = nouveau use case
- Support multi-BDD = nouveaux adapters
- API REST + GraphQL = nouveaux routers

### 4. **Validation Progressive**
- Chaque phase validée par tests existants
- Golden masters garantissent compatibilité
- Tests intégration valident options

---

## 🚀 Prochaines Étapes

### Décision à prendre

1. **Framework web** : FastAPI (async) ou Flask (sync) ?
2. **BDD** : Lire format GeneWeb binaire ou migrer vers SQL ?
3. **Templates** : Réutiliser templates existants ou nouveaux ?
4. **Déploiement** : Docker, systemd, autre ?

### Planning suggéré

| Phase | Durée | Livrables |
|-------|-------|-----------|
| Phase 0 | 1 sem | Setup projet + CI/CD |
| Phase 1 | 2 sem | Serveur HTTP + routing |
| Phase 2 | 3 sem | Lecture BDD + personnes |
| Phase 3 | 1 sem | Authentification |
| Phase 4 | 3 sem | Pages principales |
| Phase 5 | 2 sem | Options avancées |
| **Total** | **12 sem** | **v1.0 production** |

### Success Criteria

✅ **Tous les 44 tests passent**  
✅ **Performance équivalente** (benchmarks)  
✅ **Compatible bases existantes**  
✅ **Documentation complète**

---

## 📊 Confiance : 95%

Je suis confiant à 95% sur cette architecture car :
- ✅ Architecture Clean éprouvée
- ✅ Tests existants comme filet de sécurité
- ✅ Analyse complète de l'existant
- ⚠️ 5% d'incertitude sur format binaire GeneWeb

**Recommandation** : Commencer par Phase 0 (setup) pour valider l'approche

---

**Prêt à passer en mode Act pour l'implémentation ?**
