#!/usr/bin/env python3
"""Test simple des imports GeneWeb GWD"""

def test_basic_imports():
    """Test des imports de base"""
    try:
        # Test des entités
        from domain.entities.person import Person
        person = Person(id=1, first_name="Jean", surname="Dupont")
        print(f"✅ Person créé: {person.display_name}")
        
        from domain.entities.family import Family
        family = Family(id=1, husband_id=1, wife_id=2)
        print(f"✅ Family créé: {family.id}")
        
        from domain.entities.base import GenealogyBase
        base = GenealogyBase(
            name="Test", 
            path="/test", 
            persons={1: person}, 
            families={1: family},
            last_modified="2024-01-01"
        )
        print(f"✅ GenealogyBase créé: {base.name}")
        
        # Test des value objects
        from domain.value_objects.auth_result import AuthResult, AuthStatus
        auth = AuthResult.success("user", is_wizard=True)
        print(f"✅ AuthResult créé: {auth.is_authenticated}")
        
        # Test des services
        from domain.services.auth_strategies import BasicAuthStrategy
        strategy = BasicAuthStrategy("wizard", "friend")
        print(f"✅ BasicAuthStrategy créé")
        
        from domain.services.auth_factory import AuthStrategyFactory
        factory = AuthStrategyFactory("wizard", "friend")
        print(f"✅ AuthStrategyFactory créé")
        
        # Test des use cases
        from use_cases.commands import GetPersonCommand
        command = GetPersonCommand("test", 1, None)
        print(f"✅ GetPersonCommand créé")
        
        print("\n🎉 Tous les tests de base sont OK !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    test_basic_imports()
