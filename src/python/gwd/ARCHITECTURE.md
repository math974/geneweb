# 🏗️ Architecture GeneWeb GWD Python

## 📋 Vue d'ensemble

Architecture modulaire **GeneWeb GWD** en Python avec bases `.msgpack`, respectant les contraintes :
- ✅ **20 lignes max** par fonction
- ✅ **Code modulaire** sans forêt de IF
- ✅ **Patterns** de conception
- ✅ **Fonctionnalités complètes** du GWD OCaml

## 🎯 Patterns utilisés

### **Strategy Pattern**
- **Authentification** : `BasicAuthStrategy`, `DigestAuthStrategy`
- **Templates** : `PersonTemplateStrategy`, `BaseTemplateStrategy`

### **Command Pattern**
- **Use Cases** : `GetPersonCommand`, `SearchPersonsCommand`, `RenderPageCommand`

### **Chain of Responsibility**
- **Middleware** : `AuthMiddlewareHandler` → `RobotMiddlewareHandler`

### **Observer Pattern**
- **Protection robots** : `RobotDetector`

### **Repository Pattern**
- **Accès données** : `MessagePackBaseRepository`

### **Factory Pattern**
- **Création stratégies** : `AuthStrategyFactory`

## 📁 Structure du projet

```
src/python/gwd/
├── domain/                    # 🎯 Cœur métier
│   ├── entities/
│   │   ├── person.py          # Entité Personne
│   │   ├── family.py          # Entité Famille
│   │   └── base.py            # Entité Base généalogique
│   ├── value_objects/
│   │   └── auth_result.py     # Résultat d'authentification
│   └── services/
│       ├── auth_strategies.py # Stratégies d'auth
│       └── auth_factory.py     # Factory d'auth
│
├── use_cases/                 # 🔄 Logique applicative
│   └── commands.py            # Commandes (Command Pattern)
│
├── adapters/                  # 🔌 Interfaces externes
│   ├── web/
│   │   ├── fastapi_app.py     # Application FastAPI
│   │   └── template_strategies.py # Stratégies templates
│   ├── database/
│   │   └── base_repository.py # Repository bases
│   └── middleware/
│       ├── middleware_chain.py # Chaîne middleware
│       └── robot_observer.py   # Protection robots
│
├── infrastructure/            # 🛠️ Services techniques
│   ├── config.py              # Configuration
│   └── server.py              # Serveur
│
├── cli/                       # 🖥️ Interface CLI
│   └── main.py                # CLI principal
│
├── templates/                 # 📄 Templates HTML
│   ├── base_home.html         # Page d'accueil base
│   └── perso.html             # Page personne
│
├── static/                    # 🎨 Assets statiques
│   └── css/
│       └── style.css          # Styles CSS
│
└── pyproject.toml             # Configuration Python
```

## 🔧 Fonctionnalités implémentées

### **✅ Authentification**
- Basic Auth et Digest Auth
- Gestion des wizards et amis
- Factory pattern pour les stratégies

### **✅ Protection robots**
- Détection d'activité suspecte
- Blocage des IPs malveillantes
- Observer pattern

### **✅ Gestion des bases**
- Repository pattern pour les bases .msgpack
- Cache des bases chargées
- Recherche de personnes

### **✅ Serveur web**
- FastAPI avec middleware
- Routes compatibles GeneWeb
- Templates Jinja2

### **✅ Architecture modulaire**
- Séparation des responsabilités
- Injection de dépendances
- Patterns de conception

## 🚀 Utilisation

### **Installation**
```bash
pip install fastapi uvicorn jinja2 msgpack pydantic click
```

### **Démarrage**
```bash
python cli/main.py --port 2317 --bases-dir /path/to/bases
```

### **Accès web**
- `http://localhost:2317/ma_base` - Page d'accueil
- `http://localhost:2317/ma_base/person/123` - Page personne
- `http://localhost:2317/ma_base/search?q=Dupont` - Recherche

## 🎯 Avantages de l'architecture

### **✅ Modulaire**
- Chaque composant a une responsabilité unique
- Facile à tester et maintenir
- Extensible avec de nouveaux patterns

### **✅ Sans forêt de IF**
- Utilisation de patterns au lieu de conditions
- Code plus lisible et maintenable
- Polymorphisme et délégation

### **✅ 20 lignes max**
- Fonctions courtes et focalisées
- Code facile à comprendre
- Maintenance simplifiée

### **✅ Fonctionnalités complètes**
- Toutes les fonctionnalités du GWD OCaml
- Format .msgpack plus moderne
- Performance améliorée

## 🔄 Comparaison avec GWD OCaml

| **Fonctionnalité** | **GWD OCaml** | **GWD Python** | **Statut** |
|-------------------|---------------|----------------|------------|
| Authentification | ✅ Basic/Digest | ✅ Basic/Digest | ✅ Équivalent |
| Protection robots | ✅ Anti-robot | ✅ Anti-robot | ✅ Équivalent |
| Gestion bases | ✅ .gwb | ✅ .msgpack | ✅ Amélioré |
| Serveur web | ✅ HTTP/CGI | ✅ FastAPI | ✅ Amélioré |
| Templates | ✅ OCaml | ✅ Jinja2 | ✅ Équivalent |
| Architecture | ❌ Monolithique | ✅ Modulaire | ✅ Amélioré |

## 🎉 Conclusion

L'architecture **GeneWeb GWD Python** offre :

- ✅ **Équivalence fonctionnelle** avec le GWD OCaml
- ✅ **Architecture moderne** et modulaire
- ✅ **Code maintenable** sans forêt de IF
- ✅ **Performance améliorée** avec FastAPI
- ✅ **Format moderne** avec .msgpack
- ✅ **Extensibilité** avec les patterns

**Architecture prête pour la production !** 🚀
