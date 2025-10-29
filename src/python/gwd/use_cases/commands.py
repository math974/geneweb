"""Command Pattern pour les Use Cases - 20 lignes max"""
from abc import ABC, abstractmethod
from typing import Any, Dict
from dataclasses import dataclass

class Command(ABC):
    """Commande - 20 lignes max"""
    
    @abstractmethod
    def execute(self) -> Any:
        pass

@dataclass
class GetPersonCommand(Command):
    """Commande récupérer personne - 20 lignes max"""
    base_name: str
    person_id: int
    repository: Any
    
    def execute(self) -> Any:
        return self.repository.get_person_by_id(self.base_name, self.person_id)

@dataclass
class SearchPersonsCommand(Command):
    """Commande rechercher personnes - 20 lignes max"""
    base_name: str
    query: str
    repository: Any
    
    def execute(self) -> Any:
        return self.repository.search_persons(self.base_name, self.query)

@dataclass
class RenderPageCommand(Command):
    """Commande rendre page - 20 lignes max"""
    template_name: str
    context: Dict[str, Any]
    template_strategy: Any
    
    def execute(self) -> str:
        return self.template_strategy.render(self.template_name, self.context)
