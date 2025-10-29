"""Template strategies pour le rendu HTML - 20 lignes max par fonction"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


class TemplateStrategy(ABC):
    """Stratégie de template - MAX 20 LIGNES"""
    
    @abstractmethod
    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """Rendre un template avec un contexte"""
        pass


class Jinja2TemplateStrategy(TemplateStrategy):
    """Stratégie Jinja2 - MAX 20 LIGNES"""
    
    def __init__(self, template_dir: str):
        """Initialiser avec le répertoire des templates"""
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )
    
    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """Rendre un template avec un contexte - MAX 20 LIGNES"""
        template = self.env.get_template(f"{template_name}.html")
        return template.render(**context)


class FileTemplateStrategy(TemplateStrategy):
    """Stratégie de templates simples dans des fichiers - MAX 20 LIGNES"""
    
    def __init__(self, template_dir: str):
        """Initialiser avec le répertoire des templates"""
        self.template_dir = Path(template_dir)
    
    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """Rendre un template avec un contexte - MAX 20 LIGNES"""
        template_path = self.template_dir / f"{template_name}.html"
        if not template_path.exists():
            return f"Template {template_name}.html not found"
            
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Remplacement simple des variables {{var}}
        for key, value in context.items():
            content = content.replace(f"{{{{{key}}}}}", str(value))
            
        return content
