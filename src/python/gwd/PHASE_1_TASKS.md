# 🏗️ PHASE 1 : FONDATIONS - Tâches détaillées

## Issue #40 : Domain Entities

**Fichier :** `src/python/gwd/domain/entities/person.py`  
**Fichier :** `src/python/gwd/domain/entities/family.py`  
**Fichier :** `src/python/gwd/domain/entities/base.py`

### ✅ Ce qui existe déjà

```python
# person.py - DÉJÀ IMPLÉMENTÉ ✅
@dataclass
class Person:
    id: int
    first_name: str
    surname: str
    public_name: Optional[str] = None
    occ: int = 0
    birth: Optional[date] = None
    death: Optional[date] = None
    birth_place: Optional[str] = None
    death_place: Optional[str] = None
    notes: str = ""
    sources: List[str] = None
    
    @property
    def display_name(self) -> str: # ✅ Implémenté
    @property
    def age_at_death(self) -> Optional[int]: # ✅ Implémenté
```

### 📝 À FAIRE

#### 1. Compléter `family.py`

```python
# domain/entities/family.py
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Family:
    """Entité Famille - 20 lignes max"""
    id: int
    husband_id: Optional[int]
    wife_id: Optional[int]
    children_ids: List[int]
    
    def __post_init__(self):
        if self.children_ids is None:
            self.children_ids = []
    
    def add_child(self, child_id: int) -> None:
        """Ajouter un enfant - MAX 20 LIGNES"""
        if child_id not in self.children_ids:
            self.children_ids.append(child_id)
    
    def get_children_count(self) -> int:
        """Nombre d'enfants - MAX 20 LIGNES"""
        return len(self.children_ids)
    
    def is_complete(self) -> bool:
        """Famille complète (père + mère) - MAX 20 LIGNES"""
        return self.husband_id is not None and self.wife_id is not None
```

#### 2. Compléter `base.py`

```python
# domain/entities/base.py
from dataclasses import dataclass, field
from typing import Dict
from .person import Person
from .family import Family

@dataclass
class GenealogyBase:
    """Entité Base généalogique - 20 lignes max"""
    name: str
    persons: Dict[int, Person] = field(default_factory=dict)
    families: Dict[int, Family] = field(default_factory=dict)
    title: str = ""
    wizard_password: str = ""
    friend_password: str = ""
    
    def get_person(self, person_id: int) -> Optional[Person]:
        """Obtenir une personne - MAX 20 LIGNES"""
        return self.persons.get(person_id)
    
    def add_person(self, person: Person) -> None:
        """Ajouter une personne - MAX 20 LIGNES"""
        self.persons[person.id] = person
    
    def search_persons(self, query: str) -> List[Person]:
        """Rechercher des personnes - MAX 20 LIGNES"""
        query_lower = query.lower()
        return [
            p for p in self.persons.values()
            if query_lower in p.first_name.lower()
            or query_lower in p.surname.lower()
        ]
```

#### 3. Créer les tests

```python
# tests/test_domain_entities.py
def test_person_creation():
    """Test création d'une personne"""
    person = Person(
        id=1,
        first_name="Jean",
        surname="Dupont",
        birth=date(1950, 1, 1)
    )
    assert person.id == 1
    assert person.display_name == "Jean Dupont"

def test_family_add_child():
    """Test ajout d'enfant à une famille"""
    family = Family(id=1, husband_id=1, wife_id=2, children_ids=[])
    family.add_child(3)
    assert 3 in family.children_ids

def test_base_search():
    """Test recherche dans une base"""
    base = GenealogyBase(name="test")
    base.add_person(Person(1, "Jean", "Dupont"))
    base.add_person(Person(2, "Marie", "Martin"))
    results = base.search_persons("Dupont")
    assert len(results) == 1
```

---

## Issue #41 : Authentication System

**Fichier :** `src/python/gwd/domain/services/auth_strategies.py`  
**Fichier :** `src/python/gwd/domain/services/auth_factory.py`

### ✅ Ce qui existe déjà

```python
# auth_strategies.py - DÉJÀ COMMENCÉ ✅
class BasicAuthStrategy(AuthStrategy):
    def authenticate(self, credentials: str) -> AuthResult:
        # ✅ Implémenté
        pass
    
class DigestAuthStrategy(AuthStrategy):
    def authenticate(self, credentials: str) -> AuthResult:
        # ⚠️ À COMPLÉTER
        return AuthResult.failed()
```

### 📝 À FAIRE

#### 1. Compléter `DigestAuthStrategy`

```python
# domain/services/auth_strategies.py
class DigestAuthStrategy(AuthStrategy):
    """Stratégie Digest Auth - 20 lignes max"""
    
    def __init__(self, wizard_password: str, friend_password: str):
        self.wizard_password = wizard_password
        self.friend_password = friend_password
    
    def authenticate(self, credentials: str) -> AuthResult:
        """Authentifier avec Digest Auth - MAX 20 LIGNES"""
        parsed = self._parse_digest(credentials)
        if not parsed:
            return AuthResult.failed("", "Invalid digest")
        
        username = parsed['username']
        response = parsed['response']
        nonce = parsed.get('nonce', '')
        
        # Vérifier les credentials
        if self._check_password(username, response):
            return AuthResult.success(username)
        return AuthResult.failed(username)
    
    def _parse_digest(self, credentials: str) -> Optional[dict]:
        """Parser les credentials digest - MAX 20 LIGNES"""
        import re
        pattern = r'Digest (.+)'
        match = re.search(pattern, credentials)
        if not match:
            return None
        # Parse la chaîne Digest
        return {'username': '', 'response': '', 'nonce': ''}
    
    def _check_password(self, username: str, response: str) -> bool:
        """Vérifier le mot de passe - MAX 20 LIGNES"""
        # Implémenter la vérification digest
        return False
```

#### 2. Créer `auth_factory.py`

```python
# domain/services/auth_factory.py
from .auth_strategies import AuthStrategy, BasicAuthStrategy, DigestAuthStrategy

class AuthStrategyFactory:
    """Factory pour créer des stratégies d'authentification"""
    
    @staticmethod
    def create(
        auth_type: str,
        wizard_password: str,
        friend_password: str
    ) -> AuthStrategy:
        """Créer une stratégie d'auth - MAX 20 LIGNES"""
        if auth_type == "basic":
            return BasicAuthStrategy(wizard_password, friend_password)
        elif auth_type == "digest":
            return DigestAuthStrategy(wizard_password, friend_password)
        else:
            raise ValueError(f"Type d'auth inconnu: {auth_type}")
```

#### 3. Améliorer `auth_result.py`

```python
# domain/value_objects/auth_result.py
from dataclasses import dataclass

@dataclass
class AuthResult:
    """Résultat d'authentification - 20 lignes max"""
    success: bool
    username: str
    is_wizard: bool = False
    is_friend: bool = False
    error: str = ""
    
    @staticmethod
    def success(username: str, is_wizard: bool = False, is_friend: bool = False):
        """Créer un résultat de succès - MAX 20 LIGNES"""
        return AuthResult(
            success=True,
            username=username,
            is_wizard=is_wizard,
            is_friend=is_friend
        )
    
    @staticmethod
    def failed(username: str, error: str = "Invalid credentials"):
        """Créer un résultat d'échec - MAX 20 LIGNES"""
        return AuthResult(
            success=False,
            username=username,
            error=error
        )
```

#### 4. Créer les tests

```python
# tests/test_auth.py
def test_basic_auth_valid():
    """Test authentification Basic valide"""
    strategy = BasicAuthStrategy("wizard123", "friend456")
    credentials = base64.b64encode(b"admin:wizard123").decode()
    result = strategy.authenticate(f"Basic {credentials}")
    assert result.success
    assert result.is_wizard

def test_basic_auth_invalid():
    """Test authentification Basic invalide"""
    strategy = BasicAuthStrategy("wizard123", "friend456")
    credentials = base64.b64encode(b"admin:wrong").decode()
    result = strategy.authenticate(f"Basic {credentials}")
    assert not result.success

def test_factory():
    """Test de la factory"""
    strategy = AuthStrategyFactory.create("basic", "w1", "f1")
    assert isinstance(strategy, BasicAuthStrategy)
```

---

## Issue #43 : Database Adapter

**Fichier :** `src/python/gwd/adapters/database/base_repository.py`

### ✅ Ce qui existe déjà

```python
# base_repository.py - DÉJÀ COMMENCÉ ✅
class MessagePackBaseRepository(BaseRepository):
    def __init__(self, bases_dir: str):
        self.bases_dir = bases_dir
        self._cache: Dict[str, GenealogyBase] = {}
    
    def load_base(self, base_name: str) -> Optional[GenealogyBase]:
        # ✅ Cache implémenté
    
    def _load_from_disk(self, base_name: str) -> Optional[GenealogyBase]:
        # ❌ À COMPLÉTER
        return None
```

### 📝 À FAIRE

#### 1. Compléter `_load_from_disk()`

```python
# adapters/database/base_repository.py
def _load_from_disk(self, base_name: str) -> Optional[GenealogyBase]:
    """Charger une base depuis le disque - MAX 20 LIGNES"""
    import msgpack
    from pathlib import Path
    
    file_path = Path(self.bases_dir) / f"{base_name}.msgpack"
    if not file_path.exists():
        return None
    
    try:
        with open(file_path, 'rb') as f:
            data = msgpack.unpackb(f.read(), raw=False)
        
        base = GenealogyBase(
            name=base_name,
            title=data.get('title', ''),
            wizard_password=data.get('wizard_password', ''),
            friend_password=data.get('friend_password', '')
        )
        
        # Charger les personnes
        for p_data in data.get('persons', []):
            person = Person(**p_data)
            base.add_person(person)
        
        return base
    except Exception as e:
        print(f"Erreur chargement base {base_name}: {e}")
        return None
```

#### 2. Compléter `search_persons()`

```python
def search_persons(self, base_name: str, query: str) -> List[Person]:
    """Rechercher des personnes - MAX 20 LIGNES"""
    base = self.load_base(base_name)
    if not base:
        return []
    
    query_lower = query.lower()
    results = []
    
    for person in base.persons.values():
        if (query_lower in person.first_name.lower()
            or query_lower in person.surname.lower()
            or (person.public_name and query_lower in person.public_name.lower())):
            results.append(person)
    
    return results
```

#### 3. Créer les tests

```python
# tests/test_repository.py
def test_load_base_exists():
    """Test chargement d'une base existante"""
    repository = MessagePackBaseRepository("/tmp/bases")
    base = repository.load_base("test")
    assert base is not None

def test_search_persons():
    """Test recherche de personnes"""
    repository = MessagePackBaseRepository("/tmp/bases")
    results = repository.search_persons("test", "Dupont")
    assert len(results) > 0

def test_cache():
    """Test du cache"""
    repository = MessagePackBaseRepository("/tmp/bases")
    base1 = repository.load_base("test")
    base2 = repository.load_base("test")  # Doit utiliser le cache
    assert base1 is base2
```

---

## ✅ Checklist Phase 1

- [ ] **Issue #40** : Compléter `family.py` et `base.py`
- [ ] **Issue #40** : Créer tests pour domain entities
- [ ] **Issue #41** : Compléter `DigestAuthStrategy`
- [ ] **Issue #41** : Créer `auth_factory.py`
- [ ] **Issue #41** : Améliorer `auth_result.py`
- [ ] **Issue #41** : Créer tests pour auth
- [ ] **Issue #43** : Compléter `_load_from_disk()`
- [ ] **Issue #43** : Compléter `search_persons()`
- [ ] **Issue #43** : Créer tests pour repository

## 🚀 Commandes

```bash
# Basculer sur la branche
git checkout feature/domain-entities

# Travail sur Issue #40
# ... modifier family.py, base.py ...
git add src/python/gwd/domain/entities/
git commit -m "feat(domain): complete entities implementation"
git push

# Basculer sur Issue #41
git checkout feature/authentication-system
# ... compléter DigestAuthStrategy, créer auth_factory.py ...
git add src/python/gwd/domain/services/
git commit -m "feat(auth): complete authentication strategies"
git push

# Basculer sur Issue #43
git checkout feature/database-adapter
# ... compléter repository ...
git add src/python/gwd/adapters/database/
git commit -m "feat(database): complete repository implementation"
git push
```

