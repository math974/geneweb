# GeneWeb GWD Python

Serveur généalogique GeneWeb en Python avec bases .msgpack.

## 🚀 Installation

```bash
pip install -e .
```

## 🎯 Utilisation

```bash
# Démarrage du serveur
geneweb-gwd --port 2317 --bases-dir /path/to/bases

# Accès web
http://localhost:2317/ma_base
http://localhost:2317/ma_base/person/123
```

## 🏗️ Architecture

- **Domain** : Entités et value objects
- **Use Cases** : Command pattern
- **Adapters** : Web, Database, Middleware
- **Infrastructure** : Configuration et serveur

## ✅ Fonctionnalités

- ✅ Authentification (Basic/Digest Auth)
- ✅ Protection anti-robots
- ✅ Gestion bases .msgpack
- ✅ Recherche de personnes
- ✅ Affichage des pages
- ✅ Templates Jinja2
- ✅ Architecture modulaire

## 🔧 Configuration

Variables d'environnement :
- `GWD_HOST` : Adresse du serveur
- `GWD_PORT` : Port du serveur
- `GWD_BASES_DIR` : Répertoire des bases
- `GWD_WIZARD_PASSWORD` : Mot de passe wizard
- `GWD_FRIEND_PASSWORD` : Mot de passe friend
