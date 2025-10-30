"""Template Strategy Pattern - 20 lignes max"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from fastapi.templating import Jinja2Templates

class TemplateStrategy(ABC):
    """Stratégie de template - 20 lignes max"""

    @abstractmethod
    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        pass

class PersonTemplateStrategy(TemplateStrategy):
    """Stratégie template personne - 20 lignes max"""

    def __init__(self, templates: Jinja2Templates):
        self.templates = templates

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        template = self.templates.get_template(template_name)
        return template.render(context)

    def render_person_page(self, person, base_name: str, mode: str = "") -> str:
        context = {
            'person': person,
            'base_name': base_name,
            'mode': mode,
            'lang': 'en'
        }
        template_name = self._get_template_name(mode)
        return self.render(template_name, context)

    def _get_template_name(self, mode: str) -> str:
        template_map = {
            "A": "anctree.html",
            "D": "deslist.html",
            "F": "family.html"
        }
        return template_map.get(mode, "perso.html")

class BaseTemplateStrategy(TemplateStrategy):
    """Stratégie template base - 20 lignes max"""

    def __init__(self, templates: Jinja2Templates):
        self.templates = templates

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        template = self.templates.get_template(template_name)
        return template.render(context)

    def render_base_home(self, base_name: str, persons_count: int, families_count: int) -> str:
        context = {
            'base_name': base_name,
            'persons_count': persons_count,
            'families_count': families_count,
            'lang': 'en'
        }
        return self.render("base_home.html", context)
