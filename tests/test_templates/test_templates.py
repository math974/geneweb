"""Tests pour les templates HTML - MAX 20 LIGNES par fonction"""
import sys
import pytest
from pathlib import Path
import os

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "python"))

try:
    from jinja2 import Environment, FileSystemLoader
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False


@pytest.fixture
def jinja_env():
    """Fixture: Environment Jinja2 pour les tests"""
    if not JINJA2_AVAILABLE:
        pytest.skip("Jinja2 n'est pas disponible")
    
    templates_dir = str(Path(__file__).parent.parent.parent / "src" / "python" / "gwd" / "templates")
    if not os.path.exists(templates_dir):
        pytest.skip(f"Répertoire de templates non trouvé: {templates_dir}")
        
    return Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=True
    )


@pytest.fixture
def mock_person():
    """Fixture: Personne mock pour les tests"""
    return {
        'id': 1,
        'display_name': 'Jean Dupont',
        'first_name': 'Jean',
        'surname': 'Dupont',
        'birth': '1980-01-01',
        'birth_place': 'Paris',
        'death': '2050-12-31',
        'death_place': 'Lyon',
        'notes': 'Notes de test',
        'occ': 0
    }


@pytest.fixture
def mock_base():
    """Fixture: Base mock pour les tests"""
    return {
        'name': 'Base Test',
        'title': 'Base de Test',
        'description': 'Description de la base de test',
        'persons_count': 10,
        'families_count': 5
    }


@pytest.mark.skipif(not JINJA2_AVAILABLE, reason="Jinja2 n'est pas disponible")
def test_base_template(jinja_env):
    """Test template de base"""
    template = jinja_env.get_template('base.html')
    result = template.render(title="Test Title")
    
    assert "<title>Test Title</title>" in result
    assert "<div class=\"container\">" in result
    assert "<header>" in result
    assert "<main>" in result
    assert "<footer>" in result


@pytest.mark.skipif(not JINJA2_AVAILABLE, reason="Jinja2 n'est pas disponible")
def test_base_home_template(jinja_env, mock_base):
    """Test template de page d'accueil"""
    template = jinja_env.get_template('base_home.html')
    result = template.render(
        base_name=mock_base['name'],
        persons_count=mock_base['persons_count'],
        families_count=mock_base['families_count']
    )
    
    assert mock_base['name'] in result
    assert "Personnes" in result
    assert str(mock_base['persons_count']) in result
    assert "Familles" in result
    assert str(mock_base['families_count']) in result
    assert "Rechercher" in result


@pytest.mark.skipif(not JINJA2_AVAILABLE, reason="Jinja2 n'est pas disponible")
def test_person_template(jinja_env, mock_person):
    """Test template de page personne"""
    template = jinja_env.get_template('person.html')
    result = template.render(
        person=mock_person,
        base_name="base_test"
    )
    
    assert mock_person['display_name'] in result
    assert mock_person['birth'] in result
    assert mock_person['birth_place'] in result
    assert mock_person['death'] in result
    assert mock_person['death_place'] in result
    assert "Ascendance" in result
    assert "Descendance" in result


@pytest.mark.skipif(not JINJA2_AVAILABLE, reason="Jinja2 n'est pas disponible")
def test_search_results_template(jinja_env, mock_person):
    """Test template de résultats de recherche"""
    template = jinja_env.get_template('search_results.html')
    results = [mock_person]
    
    result = template.render(
        query="Dupont",
        results=results,
        count=len(results),
        base_name="base_test"
    )
    
    assert "Recherche: Dupont" in result
    assert mock_person['display_name'] in result
    assert "Résultats (1)" in result
    assert mock_person['birth'] in result
    assert mock_person['death'] in result


@pytest.mark.skipif(not JINJA2_AVAILABLE, reason="Jinja2 n'est pas disponible")
def test_search_results_no_results(jinja_env):
    """Test template de résultats de recherche sans résultats"""
    template = jinja_env.get_template('search_results.html')
    
    result = template.render(
        query="InexistantNom",
        results=[],
        count=0,
        base_name="base_test"
    )
    
    assert "Recherche: InexistantNom" in result
    assert "Résultats (0)" in result
    assert "Aucun résultat trouvé" in result


@pytest.mark.skipif(not JINJA2_AVAILABLE, reason="Jinja2 n'est pas disponible")
def test_not_found_template(jinja_env):
    """Test template de page non trouvée"""
    template = jinja_env.get_template('not_found.html')
    
    result = template.render(base_name="base_test")
    
    assert "Page non trouvée" in result
    assert "404" in result
    assert "base_test" in result
