# Guide de Tests - GeneWeb GWD Python

Ce document décrit comment exécuter et écrire des tests pour le projet GeneWeb GWD Python.

## Structure des tests

Les tests sont organisés dans une structure qui reflète l'architecture Clean du projet :

```
tests/
├── test_domain/
│   ├── test_entities/
│   │   ├── test_person.py
│   │   ├── test_family.py
│   │   └── test_base.py
│   ├── test_value_objects/
│   │   ├── test_name.py
│   │   ├── test_date.py
│   │   └── test_place.py
│   └── test_services/
│       └── test_auth.py
├── test_use_cases/
│   └── test_commands.py
├── test_adapters/
│   ├── test_database/
│   │   └── test_repository.py
│   ├── test_web/
│   │   ├── test_template_strategies.py
│   │   └── test_fastapi_app.py
│   └── test_middleware/
│       ├── test_robot_observer.py
│       └── test_middleware_chain.py
├── test_infrastructure/
│   ├── test_config.py
│   └── test_server.py
└── test_integration/
    └── test_app.py
```

## Exécution des tests

Pour exécuter les tests, utilisez les commandes suivantes :

```bash
# Tous les tests
python -m pytest

# Tests spécifiques par couche
python -m pytest tests/test_domain/  # Tests du domaine
python -m pytest tests/test_use_cases/  # Tests des cas d'utilisation
python -m pytest tests/test_adapters/  # Tests des adaptateurs
python -m pytest tests/test_infrastructure/  # Tests de l'infrastructure
python -m pytest tests/test_integration/  # Tests d'intégration

# Exécution avec rapport de couverture
python -m pytest --cov=src/python/gwd

# Exécution verbeuse
python -m pytest -v

# Exécution d'un fichier spécifique
python -m pytest tests/test_domain/test_entities/test_person.py
```

## Règles pour écrire des tests

1. **Nommage** : Les fonctions de test doivent commencer par `test_` et avoir un nom clair qui décrit le comportement testé.

2. **Assertions** : Utilisez les assertions standards de pytest (`assert`).

3. **Fixtures** : Utilisez les fixtures pour créer des objets réutilisables.

4. **Mocks** : Utilisez `unittest.mock` pour simuler les dépendances externes.

5. **Tests isolés** : Chaque test doit être indépendant et ne pas dépendre d'autres tests.

## Exemples de tests

### Test d'entité

```python
# tests/test_domain/test_entities/test_person.py
def test_person_display_name():
    # Arrange
    person = Person(id=1, first_name="John", surname="Doe")
    
    # Act
    display_name = person.display_name
    
    # Assert
    assert display_name == "John Doe"
```

### Test avec Mock

```python
# tests/test_use_cases/test_commands.py
@mock.patch('gwd.adapters.database.base_repository.BaseRepository')
def test_get_person_command(mock_repository):
    # Arrange
    mock_repository.get_person_by_id.return_value = Person(id=1, first_name="John", surname="Doe")
    command = GetPersonCommand(mock_repository)
    
    # Act
    result = command.execute("test_base", 1)
    
    # Assert
    assert result.id == 1
    assert result.first_name == "John"
    mock_repository.get_person_by_id.assert_called_once_with("test_base", 1)
```

## Gestion des dépendances dans les tests

Pour gérer les dépendances externes dans les tests, deux approches sont utilisées :

1. **Imports conditionnels** : Permet de tester le code même si certaines dépendances ne sont pas installées.

```python
try:
    import uvicorn
    UVICORN_AVAILABLE = True
except ImportError:
    UVICORN_AVAILABLE = False
```

2. **Mocks systématiques** : Simule les modules externes pour les tests.

```python
sys.modules['uvicorn'] = mock.MagicMock()
```

## Couverture de code

L'objectif est d'atteindre une couverture de code de 90% minimum.
Pour vérifier la couverture de code :

```bash
python -m pytest --cov=src/python/gwd --cov-report=html
```

Cela générera un rapport HTML dans le dossier `htmlcov/` que vous pouvez ouvrir dans un navigateur.
