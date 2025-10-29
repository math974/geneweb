# 🚀 Guide de Développement - GeneWeb GWD Python

## 📋 Vue d'ensemble

Ce guide détaille **exactement ce qu'il faut faire** pour chaque issue, dans l'ordre des phases.

## ✅ Contraintes à respecter

- ✅ **20 lignes max** par fonction
- ✅ **Code modulaire** sans forêt de IF  
- ✅ **Patterns de conception** (Strategy, Command, Repository, etc.)
- ✅ **Tests unitaires** pour chaque fonctionnalité
- ✅ **Documentation** à jour

---

## 🏗️ PHASE 1 : FONDATIONS

### Issue #40 : Domain Entities (Priorité 🔴 HIGH)

**Branche :** `feature/domain-entities`  
**Statut :** In Progress  
**Fichiers concernés :**
- `src/python/gwd/domain/entities/person.py`
- `src/python/gwd/domain/entities/family.py`
- `src/python/gwd/domain/entities/base.py`

#### 📝 Tâches à accomplir :

1. **Compléter l'entité Person** (déjà commencé) ✅
   - Vérifier que toutes les propriétés sont implémentées
   - Ajouter des méthodes d'aide si nécessaire
   - Tester l'entité avec des données réelles

2. **Implémenter l'entité Family** (à faire)
   ```python
   # domain/entities/family.py
   @dataclass
   class Family:
       id: int
       husband_id: Optional[int]
       wife_id: Optional[int]
       children_ids: List[int]
       events: List[str]
       
       # Méthodes à implémenter (max 20 lignes chacune)
       # - add_child()
       # - get_children()
       # - is_complete()
   ```

3. **Implémenter l'entité GenealogyBase** (à faire)
   ```python
   # domain/entities/base.py
   @dataclass
   class GenealogyBase:
       name: str
       persons: Dict[int, Person]
       families: Dict[int, Family]
       title: str = ""
       wizard_password: str = ""
       friend_password: str = ""
       
       # Méthodes à implémenter (max 20 lignes chacune)
       # - get_person()
       # - add_person()
       # - search_persons()
   ```

4. **Tests unitaires** (à créer)
   - Tests pour Person (création, propriétés, méthodes)
   - Tests pour Family (relations, événements)
   - Tests pour GenealogyBase (gestion personnes/familles)

#### 🎯 Critères de succès :
- ✅ Toutes les entités sont implémentées
- ✅ Pas de forêt de IF
- ✅ Chaque fonction fait max 20 lignes
- ✅ Tests unitaires à 100% de couverture

---

### Issue #41 : Authentication System (Priorité 🔴 HIGH)

**Branche :** `feature/authentication-system`  
**Statut :** In Progress  
**Fichiers concernés :**
- `src/python/gwd/domain/services/auth_strategies.py`
- `src/python/gwd/domain/services/auth_factory.py`
- `src/python/gwd/domain/value_objects/auth_result.py`

#### 📝 Tâches à accomplir :

1. **Compléter BasicAuthStrategy** (déjà commencé) ✅
   - Implémentation du décodage Base64
   - Validation des mots de passe wizard/friend
   - Retour des AuthResult appropriés

2. **Implémenter DigestAuthStrategy** (à compléter)
   ```python
   # domain/services/auth_strategies.py
   class DigestAuthStrategy(AuthStrategy):
       """Stratégie Digest Auth - 20 lignes max"""
       
       def authenticate(self, credentials: str) -> AuthResult:
           # Décoder les credentials digest
           # Vérifier nonce, realm, response
           # Retourner AuthResult approprié
           pass
   ```

3. **Créer AuthStrategyFactory** (à créer)
   ```python
   # domain/services/auth_factory.py
   class AuthStrategyFactory:
       """Factory pour créer des stratégies d'auth"""
       
       @staticmethod
       def create(auth_type: str, wizard_pwd: str, friend_pwd: str):
           # Créer Basic ou Digest selon le type
           pass
   ```

4. **Améliorer AuthResult** (à compléter)
   ```python
   # domain/value_objects/auth_result.py
   @dataclass
   class AuthResult:
       success: bool
       username: str
       is_wizard: bool = False
       is_friend: bool = False
       error: str = ""
       
       @staticmethod
       def success(username: str, is_wizard: bool = False, is_friend: bool = False):
           # Créer AuthResult de succès
           pass
       
       @staticmethod
       def failed(username: str, error: str = "Invalid credentials"):
           # Créer AuthResult d'échec
           pass
   ```

5. **Tests unitaires** (à créer)
   - Tests BasicAuth (valid/invalid credentials)
   - Tests DigestAuth (si implémenté)
   - Tests Factory (création de stratégies)
   - Tests AuthResult (success/failure)

#### 🎯 Critères de succès :
- ✅ Basic Auth fonctionnel à 100%
- ✅ Digest Auth implémenté (bonus)
- ✅ Factory pattern opérationnel
- ✅ Tests avec différents scénarios

---

### Issue #43 : Database Adapter (Priorité 🔴 HIGH)

**Branche :** `feature/database-adapter`  
**Statut :** In Progress  
**Fichiers concernés :**
- `src/python/gwd/adapters/database/base_repository.py`
- `src/python/gwd/adapters/database/__init__.py`

#### 📝 Tâches à accomplir :

1. **Implémenter le chargement MessagePack** (à compléter)
   ```python
   # adapters/database/base_repository.py
   def _load_from_disk(self, base_name: str) -> Optional[GenealogyBase]:
       """Charge une base depuis le disque en format .msgpack"""
       import msgpack
       
       # 1. Vérifier si le fichier existe
       # 2. Lire le fichier .msgpack
       # 3. Désérialiser les données
       # 4. Créer l'objet GenealogyBase
       # 5. Retourner la base
   ```

2. **Implémenter la recherche de personnes** (à compléter)
   ```python
   def search_persons(self, base_name: str, query: str) -> List[Person]:
       """Recherche des personnes par nom"""
       # 1. Charger la base
       # 2. Parcourir les personnes
       # 3. Filtrer par query (nom, prénom)
       # 4. Retourner la liste
   ```

3. **Implémenter le cache** (déjà commencé) ✅
   - Vérifier que le cache fonctionne
   - Ajouter invalidation du cache si nécessaire
   - Tester les performances

4. **Ajouter gestion des erreurs** (à faire)
   - Gestion de fichiers manquants
   - Gestion de fichiers corrompus
   - Gestion de formats invalides

5. **Tests unitaires** (à créer)
   - Tests de chargement de base
   - Tests de recherche
   - Tests de cache
   - Tests de gestion d'erreurs

#### 🎯 Critères de succès :
- ✅ Chargement .msgpack opérationnel
- ✅ Recherche de personnes fonctionnelle
- ✅ Cache efficace
- ✅ Gestion d'erreurs robuste

---

## 🔄 PHASE 2 : LOGIQUE MÉTIER

### Issue #42 : Use Cases Commands (Priorité 🟡 MEDIUM)

**Branche :** `feature/use-cases-commands`  
**Statut :** Todo  
**Fichiers concernés :**
- `src/python/gwd/use_cases/commands.py`

#### 📝 Tâches à accomplir :

1. **Implémenter GetPersonCommand**
   ```python
   class GetPersonCommand:
       """Commande pour obtenir une personne"""
       
       def __init__(self, repository: BaseRepository):
           self.repository = repository
       
       def execute(self, base_name: str, person_id: int) -> Optional[Person]:
           # Utiliser le repository pour charger la personne
           # Retourner la personne ou None
           pass
   ```

2. **Implémenter SearchPersonsCommand**
   ```python
   class SearchPersonsCommand:
       """Commande pour rechercher des personnes"""
       
       def __init__(self, repository: BaseRepository):
           self.repository = repository
       
       def execute(self, base_name: str, query: str) -> List[Person]:
           # Utiliser le repository pour rechercher
           # Retourner la liste des résultats
           pass
   ```

3. **Implémenter RenderPageCommand**
   ```python
   class RenderPageCommand:
       """Commande pour rendre une page"""
       
       def __init__(self, template_strategy):
           self.template_strategy = template_strategy
       
       def execute(self, context: dict) -> str:
           # Utiliser la stratégie de template
           # Rendre la page HTML
           # Retourner le HTML
           pass
   ```

4. **Tests unitaires** (à créer)
   - Tests GetPersonCommand (personne existante/inexistante)
   - Tests SearchPersonsCommand (recherches diverses)
   - Tests RenderPageCommand (rendu pages)

#### 🎯 Critères de succès :
- ✅ Command Pattern implémenté
- ✅ Toutes les commandes fonctionnelles
- ✅ Injection de dépendances
- ✅ Tests à 100%

---

### Issue #44 : Web Adapter (Priorité 🟡 MEDIUM)

**Branche :** `feature/web-adapter`  
**Statut :** Todo  
**Fichiers concernés :**
- `src/python/gwd/adapters/web/fastapi_app.py`
- `src/python/gwd/adapters/web/template_strategies.py`

#### 📝 Tâches à accomplir :

1. **Créer les routes FastAPI** (à compléter)
   ```python
   # adapters/web/fastapi_app.py
   @app.get("/{base_name}")
   async def home(base_name: str):
       """Page d'accueil d'une base"""
       # 1. Charger la base
       # 2. Rendre la page d'accueil
       # 3. Retourner HTML
       pass
   
   @app.get("/{base_name}/person/{person_id}")
   async def person(base_name: str, person_id: int):
       """Page d'une personne"""
       # 1. Charger la personne
       # 2. Rendre la page personne
       # 3. Retourner HTML
       pass
   
   @app.get("/{base_name}/search")
   async def search(base_name: str, q: str):
       """Recherche de personnes"""
       # 1. Rechercher les personnes
       # 2. Rendre les résultats
       # 3. Retourner HTML
       pass
   ```

2. **Implémenter les Template Strategies** (à compléter)
   ```python
   # adapters/web/template_strategies.py
   class PersonTemplateStrategy:
       """Stratégie de template pour une personne"""
       
       def render(self, person: Person, context: dict) -> str:
           # Rendre le template person.html
           # Injecter les données
           # Retourner HTML
           pass
   
   class BaseTemplateStrategy:
       """Stratégie de template pour la base"""
       
       def render(self, base: GenealogyBase, context: dict) -> str:
           # Rendre le template base_home.html
           # Injecter les données
           # Retourner HTML
           pass
   ```

3. **Ajouter middleware d'authentification** (à faire)
   ```python
   @app.middleware("http")
   async def auth_middleware(request: Request, call_next):
       """Middleware d'authentification"""
       # Vérifier les credentials
       # Ajouter l'utilisateur au contexte
       # Continuer la requête
       pass
   ```

4. **Tests d'intégration** (à créer)
   - Tests des routes (GET)
   - Tests des templates
   - Tests d'authentification

#### 🎯 Critères de succès :
- ✅ Routes FastAPI opérationnelles
- ✅ Templates Jinja2 fonctionnels
- ✅ Authentification opérationnelle
- ✅ Tests d'intégration complets

---

### Issue #45 : Robot Protection (Priorité 🟡 MEDIUM)

**Branche :** `feature/robot-protection`  
**Statut :** Todo  
**Fichiers concernés :**
- `src/python/gwd/adapters/middleware/robot_observer.py`
- `src/python/gwd/adapters/middleware/middleware_chain.py`

#### 📝 Tâches à accomplir :

1. **Implémenter RobotDetector** (à compléter)
   ```python
   # adapters/middleware/robot_observer.py
   class RobotDetector:
       """Détecteur de robots - Observer Pattern"""
       
       def __init__(self):
           self.suspicious_ips: Set[str] = set()
           self.request_counts: Dict[str, int] = {}
       
       def observe(self, ip: str, path: str):
           """Observer une requête"""
           # Compter les requêtes par IP
           # Détecter les patterns suspects
           # Bloquer si nécessaire
           pass
       
       def is_blocked(self, ip: str) -> bool:
           """Vérifier si une IP est bloquée"""
           return ip in self.suspicious_ips
   ```

2. **Créer la chaîne de middleware** (à compléter)
   ```python
   # adapters/middleware/middleware_chain.py
   class MiddlewareChain:
       """Chaîne de middleware - Chain of Responsibility"""
       
       def __init__(self):
           self.chain: List[MiddlewareHandler] = []
       
       def add_handler(self, handler: MiddlewareHandler):
           """Ajouter un handler à la chaîne"""
           self.chain.append(handler)
       
       async def process(self, request: Request):
           """Traiter la requête à travers la chaîne"""
           for handler in self.chain:
               if not await handler.handle(request):
                   return False
           return True
   ```

3. **Implémenter les handlers** (à créer)
   ```python
   class AuthMiddlewareHandler:
       """Handler d'authentification"""
       async def handle(self, request: Request) -> bool:
           # Vérifier l'authentification
           pass
   
   class RobotMiddlewareHandler:
       """Handler de protection anti-robot"""
       async def handle(self, request: Request) -> bool:
           # Vérifier les robots
           pass
   ```

4. **Tests unitaires** (à créer)
   - Tests de détection (IPs suspectes)
   - Tests de blocage
   - Tests de chaîne de middleware

#### 🎯 Critères de succès :
- ✅ Détection de robots opérationnelle
- ✅ Chaîne de middleware fonctionnelle
- ✅ Patterns Observer et Chain implémentés
- ✅ Tests complets

---

## 🛠️ PHASE 3 : INFRASTRUCTURE

### Issue #46 : Infrastructure (Priorité 🟡 MEDIUM)

**Branche :** `feature/infrastructure`  
**Statut :** Todo  
**Fichiers concernés :**
- `src/python/gwd/infrastructure/config.py`
- `src/python/gwd/infrastructure/server.py`

#### 📝 Tâches à accomplir :

1. **Créer la configuration** (à faire)
   ```python
   # infrastructure/config.py
   @dataclass
   class Config:
       """Configuration de l'application"""
       bases_dir: str
       port: int = 2317
       host: str = "localhost"
       auth_type: str = "basic"
       wizard_password: str = ""
       friend_password: str = ""
   
   @classmethod
   def from_env(cls):
       """Charger la config depuis les variables d'environnement"""
       pass
   
   @classmethod
   def from_file(cls, path: str):
       """Charger la config depuis un fichier"""
       pass
   ```

2. **Créer le serveur** (à compléter)
   ```python
   # infrastructure/server.py
   class Server:
       """Serveur GeneWeb GWD"""
       
       def __init__(self, config: Config):
           self.config = config
           self.app = create_app(config)
       
       def start(self):
           """Démarrer le serveur"""
           uvicorn.run(
               self.app,
               host=self.config.host,
               port=self.config.port
           )
       
       def stop(self):
           """Arrêter le serveur"""
           pass
   ```

3. **Ajouter logging** (à faire)
   - Logs de démarrage/arrêt
   - Logs de requêtes
   - Logs d'erreurs

4. **Tests** (à créer)
   - Tests de configuration
   - Tests de démarrage
   - Tests de logging

#### 🎯 Critères de succès :
- ✅ Configuration flexible
- ✅ Serveur opérationnel
- ✅ Logging complet
- ✅ Tests fonctionnels

---

### Issue #49 : Testing Documentation (Priorité 🟡 MEDIUM)

**Branche :** `feature/testing-documentation`  
**Statut :** Todo  
**Fichiers concernés :**
- `src/python/gwd/TESTING_GUIDE.md`

#### 📝 Tâches à accomplir :

1. **Compléter TESTING_GUIDE.md** (déjà commencé) ✅
   - Ajouter guide de tests unitaires
   - Ajouter guide de tests d'intégration
   - Ajouter guide de tests de performance

2. **Créer des exemples de tests** (à faire)
   ```python
   # Exemples à créer :
   # - test_domain_entities.py
   # - test_auth_strategies.py
   # - test_repository.py
   # - test_commands.py
   # - test_routes.py
   ```

3. **Créer la documentation de test** (à compléter)
   - Comment écrire des tests
   - Structure des tests
   - Bonnes pratiques

4. **Ajouter CI/CD** (bonus)
   - Configuration GitHub Actions
   - Tests automatiques
   - Coverage reports

#### 🎯 Critères de succès :
- ✅ Documentation complète
- ✅ Exemples de tests clairs
- ✅ CI/CD opérationnel (si ajouté)

---

## 🎨 PHASE 4 : INTERFACE UTILISATEUR

### Issue #47 : CLI Interface (Priorité 🟢 LOW)

**Branche :** `feature/cli-interface`  
**Statut :** Todo  
**Fichiers concernés :**
- `src/python/gwd/cli/main.py`

#### 📝 Tâches à accomplir :

1. **Créer l'interface CLI** (à compléter)
   ```python
   # cli/main.py
   @click.command()
   @click.option("--port", default=2317, help="Port du serveur")
   @click.option("--bases-dir", required=True, help="Répertoire des bases")
   @click.option("--host", default="localhost", help="Host du serveur")
   def main(port, bases_dir, host):
       """GeneWeb GWD - Serveur de généalogie"""
       config = Config(bases_dir=bases_dir, port=port, host=host)
       server = Server(config)
       server.start()
   ```

2. **Ajouter commandes CLI** (à faire)
   - `gwd serve` - Démarrer le serveur
   - `gwd list` - Lister les bases
   - `gwd info <base>` - Info sur une base

3. **Gestion d'erreurs CLI** (à faire)
   - Erreurs utilisateur claires
   - Aide contextuelle

4. **Tests CLI** (à créer)
   - Tests des commandes
   - Tests d'arguments
   - Tests d'erreurs

#### 🎯 Critères de succès :
- ✅ CLI fonctionnel
- ✅ Commandes complètes
- ✅ Gestion d'erreurs

---

### Issue #48 : Templates Assets (Priorité 🟢 LOW)

**Branche :** `feature/templates-assets`  
**Statut :** Todo  
**Fichiers concernés :**
- `src/python/gwd/templates/`
- `src/python/gwd/static/`

#### 📝 Tâches à accomplir :

1. **Créer les templates HTML** (à faire)
   ```html
   <!-- templates/base_home.html -->
   <html>
     <head>
       <title>{{ base.title }}</title>
       <link rel="stylesheet" href="/static/css/style.css">
     </head>
     <body>
       <h1>{{ base.title }}</h1>
       <p>{{ base.description }}</p>
     </body>
   </html>
   
   <!-- templates/person.html -->
   <html>
     <head>
       <title>{{ person.display_name }}</title>
       <link rel="stylesheet" href="/static/css/style.css">
     </head>
     <body>
       <h1>{{ person.display_name }}</h1>
       <p>{{ person.birth }} - {{ person.death }}</p>
     </body>
   </html>
   ```

2. **Créer les assets CSS** (à faire)
   ```css
   /* static/css/style.css */
   body {
     font-family: Arial, sans-serif;
     margin: 0;
     padding: 20px;
   }
   
   h1 {
     color: #333;
   }
   ```

3. **Tests de rendu** (à créer)
   - Tests de templates
   - Tests de CSS
   - Tests d'intégration

#### 🎯 Critères de succès :
- ✅ Templates complets
- ✅ CSS moderne
- ✅ Tests de rendu

---

## 🎯 Checklist globale

Pour chaque phase :

- [ ] Vérifier les branches existantes
- [ ] Implémenter les fonctionnalités
- [ ] Ajouter les tests
- [ ] Respecter 20 lignes max
- [ ] Utiliser les patterns
- [ ] Documenter le code
- [ ] Commiter et pousser

## 🚀 Commandes pour démarrer

```bash
# Phase 1 - Fondations
git checkout feature/domain-entities
# Développer Issue #40
# ... travail ...
git add . && git commit -m "feat: complete domain entities"
git push

# Continuer avec #41, #43...

# Phase 2 - Logique métier
git checkout feature/use-cases-commands
# Développer Issue #42
# ...

# Phase 3 - Infrastructure
git checkout feature/infrastructure
# Développer Issue #46
# ...

# Phase 4 - Interface
git checkout feature/cli-interface
# Développer Issue #47
# ...
```

---

**Bon développement ! 🎉**

