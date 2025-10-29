#!/usr/bin/env python3
"""Test des imports GeneWeb GWD"""

def test_imports():
    """Test tous les imports"""
    try:
        from domain.entities.person import Person
        print("✅ Person import OK")
        
        from domain.entities.family import Family
        print("✅ Family import OK")
        
        from domain.entities.base import GenealogyBase
        print("✅ GenealogyBase import OK")
        
        from domain.value_objects.auth_result import AuthResult
        print("✅ AuthResult import OK")
        
        from domain.services.auth_strategies import BasicAuthStrategy
        print("✅ BasicAuthStrategy import OK")
        
        from domain.services.auth_factory import AuthStrategyFactory
        print("✅ AuthStrategyFactory import OK")
        
        from use_cases.commands import GetPersonCommand
        print("✅ GetPersonCommand import OK")
        
        from adapters.database.base_repository import MessagePackBaseRepository
        print("✅ MessagePackBaseRepository import OK")
        
        from adapters.middleware.middleware_chain import AuthMiddlewareHandler
        print("✅ AuthMiddlewareHandler import OK")
        
        from adapters.middleware.robot_observer import RobotDetector
        print("✅ RobotDetector import OK")
        
        from adapters.web.template_strategies import PersonTemplateStrategy
        print("✅ PersonTemplateStrategy import OK")
        
        from adapters.web.fastapi_app import GeneWebFastAPIApp
        print("✅ GeneWebFastAPIApp import OK")
        
        from infrastructure.config import GWDSettings
        print("✅ GWDSettings import OK")
        
        from infrastructure.server import GeneWebServer
        print("✅ GeneWebServer import OK")
        
        from cli.main import serve
        print("✅ CLI serve import OK")
        
        print("\n🎉 Tous les imports sont OK !")
        return True
        
    except ImportError as e:
        print(f"❌ Erreur import: {e}")
        return False

if __name__ == "__main__":
    test_imports()
