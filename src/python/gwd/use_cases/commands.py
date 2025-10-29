"""Command Pattern pour les cas d'utilisation - 20 lignes max par fonction"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from gwd.domain.entities.person import Person
from gwd.adapters.database.base_repository import BaseRepository


class Command(ABC):
    """Interface pour les commandes - 20 lignes max"""
    
    @abstractmethod
    def execute(self, *args, **kwargs):
        """Exécuter la commande avec les arguments fournis"""
        pass


class GetPersonCommand(Command):
    """Commande pour obtenir une personne - MAX 20 LIGNES"""
    
    def __init__(self, repository: BaseRepository):
        self.repository = repository
    
    def execute(self, base_name: str, person_id: int) -> Optional[Person]:
        """Obtenir une personne par son ID"""
        return self.repository.get_person_by_id(base_name, person_id)


class SearchPersonsCommand(Command):
    """Commande pour rechercher des personnes - MAX 20 LIGNES"""
    
    def __init__(self, repository: BaseRepository):
        self.repository = repository
    
    def execute(self, base_name: str, query: str) -> List[Person]:
        """Rechercher des personnes par nom/prénom"""
        return self.repository.search_persons(base_name, query)


class RenderPageCommand(Command):
    """Commande pour rendre une page - MAX 20 LIGNES"""
    
    def __init__(self, template_strategy):
        self.template_strategy = template_strategy
    
    def execute(self, context: Dict[str, Any]) -> str:
        """Rendre une page avec un template et un contexte"""
        template_name = context.get('template', 'base')
        return self.template_strategy.render(template_name, context)
