# 🔄 PHASES 2, 3 & 4 : Tâches détaillées

## 🔄 PHASE 2 : LOGIQUE MÉTIER

### Issue #42 : Use Cases Commands

**Fichier :** `src/python/gwd/use_cases/commands.py`  
**Pattern :** Command Pattern

### 📝 À FAIRE

```python
# use_cases/commands.py

from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.person import Person
from adapters.database.base_repository import BaseRepository

class Command(ABC):
    """Interface pour les commandes - 20 lignes max"""
    
    @abstractmethod
    def execute(self, *args, **kwargs):
        pass

class GetPersonCommand(Command):
    """Commande pour obtenir une personne - MAX 20 LIGNES"""
    
    def __init__(self, repository: BaseRepository):
        self.repository = repository
    
    def execute(self, base_name: str, person_id: int) -> Optional[Person]:
        return self.repository.get_person_by_id(base_name, person_id)

class SearchPersonsCommand(Command):
    """Commande pour rechercher des personnes - MAX 20 LIGNES"""
    
    def __init__(self, repository: BaseRepository):
        self.repository = repository
    
    def execute(self, base_name: str, query: str) -> List[Person]:
        return self.repository.search_persons(base_name, query)

class RenderPageCommand(Command):
    """Commande pour rendre une page - MAX 20 LIGNES"""
    
    def __init__(self, template_strategy):
        self.template_strategy = template_strategy
    
    def execute(self, context: dict) -> str:
        template_name = context.get('template', 'base')
        return self.template_strategy.render(template_name, context)
```

### 🧪 Tests à créer

```python
# tests/test_commands.py
def test_get_person_command():
    """Test GetPersonCommand"""
    repository = MockRepository()
    command = GetPersonCommand(repository)
    person = command.execute("base1", 1)
    assert person is not None

def test_search_persons_command():
    """Test SearchPersonsCommand"""
    repository = MockRepository()
    command = SearchPersonsCommand(repository)
    results = command.execute("base1", "Dupont")
    assert len(results) > 0
```

---

### Issue #44 : Web Adapter

**Fichier :** `src/python/gwd/adapters/web/fastapi_app.py`  
**Fichier :** `src/python/gwd/adapters/web/template_strategies.py`  
**Technologies :** FastAPI, Jinja2

### 📝 À FAIRE

#### 1. Routes FastAPI

```python
# adapters/web/fastapi_app.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from use_cases.commands import GetPersonCommand, SearchPersonsCommand

def create_app(config):
    """Créer l'application FastAPI - MAX 20 LIGNES"""
    app = FastAPI(title="GeneWeb GWD")
    
    # Middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Process-Time"] = str(time.time())
        return response
    
    return app

app = create_app(None)

@app.get("/{base_name}", response_class=HTMLResponse)
async def home(base_name: str, request: Request):
    """Page d'accueil - MAX 20 LIGNES"""
    # 1. Vérifier l'authentification
    # 2. Charger la base
    # 3. Rendre la page d'accueil
    return "Home page HTML"

@app.get("/{base_name}/person/{person_id}", response_class=HTMLResponse)
async def person_page(base_name: str, person_id: int, request: Request):
    """Page personne - MAX 20 LIGNES"""
    # 1. Obtenir la personne
    # 2. Rendre la page personne
    return "Person page HTML"

@app.get("/{base_name}/search", response_class=HTMLResponse)
async def search(base_name: str, q: str, request: Request):
    """Recherche - MAX 20 LIGNES"""
    # 1. Rechercher les personnes
    # 2. Rendre les résultats
    return "Search results HTML"
```

#### 2. Template Strategies

```python
# adapters/web/template_strategies.py
from abc import ABC, abstractmethod
from jinja2 import Environment, FileSystemLoader

class TemplateStrategy(ABC):
    """Stratégie de template - MAX 20 LIGNES"""
    
    @abstractmethod
    def render(self, template_name: str, context: dict) -> str:
        pass

class Jinja2TemplateStrategy(TemplateStrategy):
    """Stratégie Jinja2 - MAX 20 LIGNES"""
    
    def __init__(self, template_dir: str):
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )
    
    def render(self, template_name: str, context: dict) -> str:
        template = self.env.get_template(f"{template_name}.html")
        return template.render(**context)
```

### 🧪 Tests à créer

```python
# tests/test_web_adapter.py
def test_home_route():
    """Test route d'accueil"""
    response = client.get("/test_base")
    assert response.status_code == 200

def test_person_route():
    """Test route personne"""
    response = client.get("/test_base/person/123")
    assert response.status_code == 200

def test_search_route():
    """Test route recherche"""
    response = client.get("/test_base/search?q=Dupont")
    assert response.status_code == 200
```

---

### Issue #45 : Robot Protection

**Fichier :** `src/python/gwd/adapters/middleware/robot_observer.py`  
**Fichier :** `src/python/gwd/adapters/middleware/middleware_chain.py`  
**Pattern :** Observer, Chain of Responsibility

### 📝 À FAIRE

#### 1. Robot Detector (Observer Pattern)

```python
# adapters/middleware/robot_observer.py
from typing import Set, Dict
from datetime import datetime, timedelta

class RobotDetector:
    """Détecteur de robots - Observer Pattern - MAX 20 LIGNES"""
    
    def __init__(self):
        self.suspicious_ips: Set[str] = set()
        self.request_counts: Dict[str, int] = {}
        self.blocked_ips: Set[str] = set()
    
    def observe(self, ip: str, path: str, timestamp: datetime):
        """Observer une requête - MAX 20 LIGNES"""
        # Compter les requêtes par IP
        count = self.request_counts.get(ip, 0) + 1
        self.request_counts[ip] = count
        
        # Détecter les patterns suspects (>100 requêtes/min)
        if count > 100:
            self.blocked_ips.add(ip)
    
    def is_blocked(self, ip: str) -> bool:
        """Vérifier si bloqué - MAX 20 LIGNES"""
        return ip in self.blocked_ips
```

#### 2. Middleware Chain (Chain of Responsibility)

```python
# adapters/middleware/middleware_chain.py
from abc import ABC, abstractmethod
from typing import List
from fastapi import Request

class MiddlewareHandler(ABC):
    """Handler de middleware - MAX 20 LIGNES"""
    
    @abstractmethod
    async def handle(self, request: Request) -> bool:
        pass

class MiddlewareChain:
    """Chaîne de middleware - MAX 20 LIGNES"""
    
    def __init__(self):
        self.handlers: List[MiddlewareHandler] = []
    
    def add_handler(self, handler: MiddlewareHandler):
        """Ajouter un handler - MAX 20 LIGNES"""
        self.handlers.append(handler)
    
    async def process(self, request: Request) -> bool:
        """Traiter la requête - MAX 20 LIGNES"""
        for handler in self.handlers:
            if not await handler.handle(request):
                return False
        return True

class AuthMiddlewareHandler(MiddlewareHandler):
    """Handler d'authentification - MAX 20 LIGNES"""
    
    async def handle(self, request: Request) -> bool:
        # Vérifier l'authentification
        return True

class RobotMiddlewareHandler(MiddlewareHandler):
    """Handler anti-robot - MAX 20 LIGNES"""
    
    def __init__(self, detector: RobotDetector):
        self.detector = detector
    
    async def handle(self, request: Request) -> bool:
        ip = request.client.host
        return not self.detector.is_blocked(ip)
```

### 🧪 Tests à créer

```python
# tests/test_robot_protection.py
def test_robot_detection():
    """Test détection de robot"""
    detector = RobotDetector()
    for i in range(101):
        detector.observe("192.168.1.1", "/", datetime.now())
    assert detector.is_blocked("192.168.1.1")

def test_middleware_chain():
    """Test chaîne de middleware"""
    chain = MiddlewareChain()
    chain.add_handler(AuthMiddlewareHandler())
    chain.add_handler(RobotMiddlewareHandler())
    # Tester le traitement
```

---

## 🛠️ PHASE 3 : INFRASTRUCTURE

### Issue #46 : Infrastructure

**Fichier :** `src/python/gwd/infrastructure/config.py`  
**Fichier :** `src/python/gwd/infrastructure/server.py`

### 📝 À FAIRE

#### 1. Configuration

```python
# infrastructure/config.py
from dataclasses import dataclass
import os

@dataclass
class Config:
    """Configuration - MAX 20 LIGNES"""
    bases_dir: str
    port: int = 2317
    host: str = "localhost"
    auth_type: str = "basic"
    wizard_password: str = ""
    friend_password: str = ""
    debug: bool = False
    
    @classmethod
    def from_env(cls):
        """Charger depuis ENV - MAX 20 LIGNES"""
        return cls(
            bases_dir=os.getenv("BASES_DIR", "./bases"),
            port=int(os.getenv("PORT", "2317")),
            host=os.getenv("HOST", "localhost"),
            auth_type=os.getenv("AUTH_TYPE", "basic"),
            wizard_password=os.getenv("WIZARD_PASSWORD", ""),
            friend_password=os.getenv("FRIEND_PASSWORD", "")
        )
```

#### 2. Serveur

```python
# infrastructure/server.py
import uvicorn
import logging
from .config import Config
from adapters.web.fastapi_app import create_app

class Server:
    """Serveur GeneWeb - MAX 20 LIGNES"""
    
    def __init__(self, config: Config):
        self.config = config
        self.app = create_app(config)
        self._setup_logging()
    
    def _setup_logging(self):
        """Configurer le logging - MAX 20 LIGNES"""
        logging.basicConfig(
            level=logging.DEBUG if self.config.debug else logging.INFO
        )
    
    def start(self):
        """Démarrer le serveur - MAX 20 LIGNES"""
        uvicorn.run(
            self.app,
            host=self.config.host,
            port=self.config.port,
            log_level="info"
        )
```

### 🧪 Tests à créer

```python
# tests/test_infrastructure.py
def test_config_from_env():
    """Test chargement config depuis ENV"""
    config = Config.from_env()
    assert config.port == 2317

def test_server_start():
    """Test démarrage serveur"""
    config = Config(bases_dir="/tmp/bases")
    server = Server(config)
    # Test démarrage
```

---

### Issue #49 : Testing Documentation

**Fichier :** `src/python/gwd/TESTING_GUIDE.md`  
**Fichier :** `tests/` (divers)

### 📝 À FAIRE

#### 1. Compléter TESTING_GUIDE.md

```markdown
# Guide de Tests - GeneWeb GWD Python

## Structure des tests

```
tests/
├── test_domain/
│   ├── test_person.py
│   ├── test_family.py
│   └── test_base.py
├── test_services/
│   └── test_auth.py
├── test_adapters/
│   ├── test_repository.py
│   ├── test_web.py
│   └── test_middleware.py
└── test_integration/
    └── test_app.py
```

## Exécution des tests

```bash
# Tests unitaires
pytest tests/test_domain/
pytest tests/test_services/

# Tests d'intégration
pytest tests/test_integration/

# Tous les tests
pytest

# Coverage
pytest --cov=src/python/gwd
```
```

#### 2. Créer des exemples de tests

Voir les exemples dans les sections précédentes.

---

## 🎨 PHASE 4 : INTERFACE UTILISATEUR

### Issue #47 : CLI Interface

**Fichier :** `src/python/gwd/cli/main.py`

### 📝 À FAIRE

```python
# cli/main.py
import click
from infrastructure.config import Config
from infrastructure.server import Server

@click.group()
def cli():
    """GeneWeb GWD - Serveur de généalogie"""
    pass

@cli.command()
@click.option("--port", default=2317, help="Port du serveur")
@click.option("--bases-dir", required=True, help="Répertoire des bases")
@click.option("--host", default="localhost", help="Host du serveur")
def serve(port, bases_dir, host):
    """Démarrer le serveur - MAX 20 LIGNES"""
    config = Config(
        bases_dir=bases_dir,
        port=port,
        host=host
    )
    server = Server(config)
    server.start()

@cli.command()
@click.argument("bases-dir")
def list_bases(bases_dir):
    """Lister les bases - MAX 20 LIGNES"""
    import os
    for file in os.listdir(bases_dir):
        if file.endswith('.msgpack'):
            click.echo(file)

@cli.command()
@click.argument("base_name")
@click.argument("bases-dir")
def info(base_name, bases_dir):
    """Info sur une base - MAX 20 LIGNES"""
    config = Config(bases_dir=bases_dir)
    repository = MessagePackBaseRepository(bases_dir)
    base = repository.load_base(base_name)
    
    if base:
        click.echo(f"Base: {base.title}")
        click.echo(f"Personnes: {len(base.persons)}")
    else:
        click.echo("Base non trouvée")

if __name__ == "__main__":
    cli()
```

### 🧪 Tests à créer

```python
# tests/test_cli.py
from click.testing import CliRunner

def test_cli_serve():
    """Test commande serve"""
    runner = CliRunner()
    result = runner.invoke(serve, ['--bases-dir=/tmp/bases'])
    assert result.exit_code == 0

def test_cli_list():
    """Test commande list"""
    runner = CliRunner()
    result = runner.invoke(list_bases, ['/tmp/bases'])
    assert result.exit_code == 0
```

---

### Issue #48 : Templates Assets

**Fichier :** `src/python/gwd/templates/`  
**Fichier :** `src/python/gwd/static/`

### 📝 À FAIRE

#### 1. Templates HTML

```html
<!-- templates/base_home.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{{ base.title }}</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <header>
        <h1>{{ base.title }}</h1>
    </header>
    <main>
        <p>Bienvenue sur {{ base.title }}</p>
        <p>{{ base.description }}</p>
    </main>
</body>
</html>

<!-- templates/person.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{{ person.display_name }}</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <header>
        <h1>{{ person.display_name }}</h1>
    </header>
    <main>
        <p>Naissance : {{ person.birth }}</p>
        <p>Décès : {{ person.death }}</p>
        <p>{{ person.notes }}</p>
    </main>
</body>
</html>
```

#### 2. CSS

```css
/* static/css/style.css */
body {
    font-family: 'Arial', sans-serif;
    margin: 0;
    padding: 20px;
    background-color: #f5f5f5;
}

header h1 {
    color: #333;
    border-bottom: 2px solid #007bff;
}

main {
    margin-top: 20px;
}
```

### 🧪 Tests à créer

```python
# tests/test_templates.py
def test_base_home_template():
    """Test template base home"""
    template = env.get_template("base_home.html")
    html = template.render(base=test_base)
    assert "Bienvenue" in html

def test_person_template():
    """Test template person"""
    template = env.get_template("person.html")
    html = template.render(person=test_person)
    assert test_person.display_name in html
```

---

## ✅ Checklist Phases 2, 3 & 4

### Phase 2
- [ ] Issue #42 : Implémenter Command Pattern
- [ ] Issue #44 : Créer routes FastAPI
- [ ] Issue #44 : Implémenter Template Strategies
- [ ] Issue #45 : Implémenter Robot Protection
- [ ] Issue #45 : Créer Middleware Chain

### Phase 3
- [ ] Issue #46 : Créer configuration
- [ ] Issue #46 : Créer serveur
- [ ] Issue #49 : Compléter documentation tests

### Phase 4
- [ ] Issue #47 : Implémenter CLI
- [ ] Issue #48 : Créer templates HTML
- [ ] Issue #48 : Créer CSS

## 🚀 Commandes

```bash
# Phase 2
git checkout feature/use-cases-commands
# ... travail sur Issue #42 ...
git add . && git commit -m "feat: implement command pattern"
git push

git checkout feature/web-adapter
# ... travail sur Issue #44 ...
git add . && git commit -m "feat: implement web adapter"
git push

git checkout feature/robot-protection
# ... travail sur Issue #45 ...
git add . && git commit -m "feat: implement robot protection"
git push

# Phase 3
git checkout feature/infrastructure
# ... travail sur Issue #46 ...

git checkout feature/testing-documentation
# ... travail sur Issue #49 ...

# Phase 4
git checkout feature/cli-interface
# ... travail sur Issue #47 ...

git checkout feature/templates-assets
# ... travail sur Issue #48 ...
```

