"""Tests pour les stratégies de templates - 20 lignes max par fonction"""
import sys
import os
from pathlib import Path
import tempfile

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "src" / "python"))

from gwd.adapters.web.template_strategies import TemplateStrategy, Jinja2TemplateStrategy, FileTemplateStrategy


def test_file_template_strategy():
    """Test FileTemplateStrategy"""
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Créer un template de test
        template_path = Path(tmpdirname) / "test.html"
        template_path.write_text("""<h1>{{title}}</h1><p>{{content}}</p>""")
        
        # Créer la stratégie
        strategy = FileTemplateStrategy(tmpdirname)
        
        # Rendre le template
        context = {"title": "Mon titre", "content": "Mon contenu"}
        result = strategy.render("test", context)
        
        assert "<h1>Mon titre</h1>" in result
        assert "<p>Mon contenu</p>" in result


def test_file_template_strategy_not_found():
    """Test FileTemplateStrategy avec template non trouvé"""
    with tempfile.TemporaryDirectory() as tmpdirname:
        strategy = FileTemplateStrategy(tmpdirname)
        result = strategy.render("nonexistent", {})
        assert "not found" in result
