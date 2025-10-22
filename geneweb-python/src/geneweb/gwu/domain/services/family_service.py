"""Service pour la gestion des familles."""

from typing import List, Optional, Set, Iterator, Dict
from dataclasses import dataclass

from geneweb.common.types import PersonId, FamilyId
from geneweb.gwu.domain.entities import Person, Family
from geneweb.gwu.domain.repositories import PersonRepository, FamilyRepository


@dataclass
class AncestryResult:
    """Résultat de calcul d'ascendance."""
    
    ancestors: Set[PersonId]
    depth_reached: int
    total_found: int
    
    def __len__(self) -> int:
        """Retourne le nombre d'ancêtres."""
        return len(self.ancestors)


@dataclass
class DescendantsResult:
    """Résultat de calcul de descendance."""
    
    descendants: Set[PersonId]
    depth_reached: int
    total_found: int
    
    def __len__(self) -> int:
        """Retourne le nombre de descendants."""
        return len(self.descendants)


class FamilyService:
    """
    Service pour la gestion des familles.
    
    Fournit la logique métier pour :
    - Calcul des relations familiales
    - Ascendance et descendance
    - Gestion des événements familiaux
    """
    
    def __init__(
        self, 
        person_repository: PersonRepository,
        family_repository: FamilyRepository
    ):
        """
        Initialise le service.
        
        Args:
            person_repository: Repository pour accéder aux personnes
            family_repository: Repository pour accéder aux familles
        """
        self.person_repository = person_repository
        self.family_repository = family_repository
    
    def get_family_by_id(self, family_id: FamilyId) -> Optional[Family]:
        """
        Récupère une famille par son ID.
        
        Args:
            family_id: ID de la famille
        
        Returns:
            La famille ou None si non trouvée
        """
        return self.family_repository.get_by_id(family_id)
    
    def get_families_of_person(self, person_id: PersonId) -> List[Family]:
        """
        Récupère les familles où une personne est parent.
        
        Args:
            person_id: ID de la personne
        
        Returns:
            Liste des familles
        """
        return self.family_repository.get_families_of_person(person_id)
    
    def get_family_of_parents(
        self, father_id: PersonId, mother_id: PersonId
    ) -> Optional[Family]:
        """
        Récupère la famille formée par un père et une mère.
        
        Args:
            father_id: ID du père
            mother_id: ID de la mère
        
        Returns:
            La famille ou None si non trouvée
        """
        return self.family_repository.get_family_of_parents(father_id, mother_id)
    
    def get_all_families(self) -> Iterator[Family]:
        """
        Récupère toutes les familles.
        
        Returns:
            Itérateur sur les familles
        """
        return self.family_repository.get_all()
    
    def get_family_count(self) -> int:
        """
        Retourne le nombre total de familles.
        
        Returns:
            Nombre de familles
        """
        return self.family_repository.get_count()
    
    def get_ancestors(
        self, 
        person_id: PersonId, 
        max_depth: int
    ) -> AncestryResult:
        """
        Calcule les ancêtres d'une personne.
        
        Args:
            person_id: ID de la personne
            max_depth: Profondeur maximale (0 = parents, 1 = grands-parents, etc.)
        
        Returns:
            Résultat avec les ancêtres trouvés
        """
        ancestors = set()
        depth_reached = 0
        
        # Queue pour BFS: (person_id, current_depth)
        queue = [(person_id, 0)]
        visited = set()
        
        while queue and depth_reached < max_depth:
            current_person_id, current_depth = queue.pop(0)
            
            if current_person_id in visited:
                continue
            visited.add(current_person_id)
            
            person = self.person_repository.get_by_id(current_person_id)
            if not person or not person.parents:
                continue
            
            # Récupérer la famille des parents
            family = self.family_repository.get_by_id(person.parents)
            if not family:
                continue
            
            # Ajouter les parents
            if family.father_id and family.father_id not in ancestors:
                ancestors.add(family.father_id)
                if current_depth + 1 <= max_depth:
                    queue.append((family.father_id, current_depth + 1))
            
            if family.mother_id and family.mother_id not in ancestors:
                ancestors.add(family.mother_id)
                if current_depth + 1 <= max_depth:
                    queue.append((family.mother_id, current_depth + 1))
            
            depth_reached = max(depth_reached, current_depth + 1)
        
        return AncestryResult(
            ancestors=ancestors,
            depth_reached=depth_reached,
            total_found=len(ancestors)
        )
    
    def get_descendants(
        self, 
        person_id: PersonId, 
        max_depth: int
    ) -> DescendantsResult:
        """
        Calcule les descendants d'une personne.
        
        Args:
            person_id: ID de la personne
            max_depth: Profondeur maximale (0 = enfants, 1 = petits-enfants, etc.)
        
        Returns:
            Résultat avec les descendants trouvés
        """
        descendants = set()
        depth_reached = 0
        
        # Queue pour BFS: (person_id, current_depth)
        queue = [(person_id, 0)]
        visited = set()
        
        while queue and depth_reached < max_depth:
            current_person_id, current_depth = queue.pop(0)
            
            if current_person_id in visited:
                continue
            visited.add(current_person_id)
            
            # Récupérer les familles où cette personne est parent
            families = self.family_repository.get_families_of_person(current_person_id)
            
            for family in families:
                # Ajouter tous les enfants
                for child_id in family.children:
                    if child_id not in descendants:
                        descendants.add(child_id)
                        if current_depth + 1 <= max_depth:
                            queue.append((child_id, current_depth + 1))
                
                depth_reached = max(depth_reached, current_depth + 1)
        
        return DescendantsResult(
            descendants=descendants,
            depth_reached=depth_reached,
            total_found=len(descendants)
        )
    
    def get_ancestors_and_descendants(
        self, 
        person_id: PersonId, 
        asc_depth: int, 
        desc_depth: int
    ) -> Set[PersonId]:
        """
        Calcule les ancêtres et descendants d'une personne.
        
        Args:
            person_id: ID de la personne
            asc_depth: Profondeur d'ascendance
            desc_depth: Profondeur de descendance
        
        Returns:
            Set des IDs des ancêtres et descendants
        """
        result = set()
        
        # Ajouter la personne elle-même
        result.add(person_id)
        
        # Ajouter les ancêtres
        if asc_depth > 0:
            ancestors_result = self.get_ancestors(person_id, asc_depth)
            result.update(ancestors_result.ancestors)
        
        # Ajouter les descendants
        if desc_depth > 0:
            descendants_result = self.get_descendants(person_id, desc_depth)
            result.update(descendants_result.descendants)
        
        return result
    
    def get_related_persons(
        self, 
        person1_id: PersonId, 
        person2_id: PersonId
    ) -> Set[PersonId]:
        """
        Calcule les personnes impliquées dans le calcul de parenté.
        
        Args:
            person1_id: ID de la première personne
            person2_id: ID de la deuxième personne
        
        Returns:
            Set des IDs des personnes impliquées
        """
        # Pour l'instant, implémentation simple
        # TODO: Implémenter l'algorithme de calcul de parenté complet
        
        result = set()
        
        # Ajouter les deux personnes
        result.add(person1_id)
        result.add(person2_id)
        
        # Ajouter leurs ancêtres communs (jusqu'à une profondeur raisonnable)
        ancestors1 = self.get_ancestors(person1_id, 5)
        ancestors2 = self.get_ancestors(person2_id, 5)
        
        # Ancêtres communs
        common_ancestors = ancestors1.ancestors.intersection(ancestors2.ancestors)
        result.update(common_ancestors)
        
        # Descendants des ancêtres communs
        for ancestor_id in common_ancestors:
            descendants = self.get_descendants(ancestor_id, 5)
            result.update(descendants.descendants)
        
        return result
    
    def get_family_tree(self, person_id: PersonId, max_depth: int = 3) -> Dict:
        """
        Construit l'arbre généalogique d'une personne.
        
        Args:
            person_id: ID de la personne racine
            max_depth: Profondeur maximale de l'arbre
        
        Returns:
            Dictionnaire représentant l'arbre
        """
        person = self.person_repository.get_by_id(person_id)
        if not person:
            return {}
        
        def build_node(p_id: str, depth: int) -> Dict:
            if depth > max_depth:
                return {"id": p_id, "name": "..."}
            
            p = self.person_repository.get_by_id(p_id)
            if not p:
                return {"id": p_id, "name": "?"}
            
            node = {
                "id": p_id,
                "name": p.format_name(),
                "sex": p.sex.value,
                "parents": [],
                "children": []
            }
            
            # Ajouter les parents
            if p.parents and depth < max_depth:
                family = self.family_repository.get_by_id(p.parents)
                if family:
                    if family.father_id:
                        node["parents"].append(build_node(family.father_id, depth + 1))
                    if family.mother_id:
                        node["parents"].append(build_node(family.mother_id, depth + 1))
            
            # Ajouter les enfants
            if depth < max_depth:
                families = self.family_repository.get_families_of_person(p_id)
                for family in families:
                    for child_id in family.children:
                        node["children"].append(build_node(child_id, depth + 1))
            
            return node
        
        return build_node(person_id, 0)
    
    def validate_family(self, family: Family) -> List[str]:
        """
        Valide une famille et retourne les erreurs.
        
        Args:
            family: Famille à valider
        
        Returns:
            Liste des erreurs de validation
        """
        errors = []
        
        # Validation des champs obligatoires
        if not family.family_id or not family.family_id.strip():
            errors.append("L'ID de la famille est obligatoire")
        
        if not family.father_id or not family.father_id.strip():
            errors.append("L'ID du père est obligatoire")
        
        if not family.mother_id or not family.mother_id.strip():
            errors.append("L'ID de la mère est obligatoire")
        
        # Validation de l'existence des personnes
        if not self.person_repository.get_by_id(family.father_id):
            errors.append(f"Père non trouvé: {family.father_id}")
        
        if not self.person_repository.get_by_id(family.mother_id):
            errors.append(f"Mère non trouvée: {family.mother_id}")
        
        # Validation des enfants
        for child_id in family.children:
            if not self.person_repository.get_by_id(child_id):
                errors.append(f"Enfant non trouvé: {child_id}")
        
        return errors
