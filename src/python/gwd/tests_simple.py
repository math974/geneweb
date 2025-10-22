#!/usr/bin/env python3
"""Tests unitaires GeneWeb GWD (sans FastAPI)"""

import unittest
from domain.entities.person import Person
from domain.entities.family import Family
from domain.entities.base import GenealogyBase
from domain.value_objects.auth_result import AuthResult, AuthStatus
from domain.services.auth_factory import AuthStrategyFactory
from use_cases.commands import GetPersonCommand, SearchPersonsCommand

class TestEntities(unittest.TestCase):
    """Tests des entités"""
    
    def test_person_creation(self):
        """Test création personne"""
        person = Person(id=1, first_name="Jean", surname="Dupont")
        self.assertEqual(person.id, 1)
        self.assertEqual(person.display_name, "Jean Dupont")
    
    def test_person_public_name(self):
        """Test nom public"""
        person = Person(id=1, first_name="Jean", surname="Dupont", public_name="Jean-Pierre")
        self.assertEqual(person.display_name, "Jean-Pierre Dupont")
    
    def test_family_creation(self):
        """Test création famille"""
        family = Family(id=1, husband_id=1, wife_id=2)
        self.assertEqual(family.id, 1)
        self.assertEqual(family.husband_id, 1)
        self.assertEqual(family.wife_id, 2)
    
    def test_base_creation(self):
        """Test création base"""
        person = Person(id=1, first_name="Jean", surname="Dupont")
        family = Family(id=1, husband_id=1, wife_id=2)
        base = GenealogyBase(
            name="Test Base",
            path="/test",
            persons={1: person},
            families={1: family},
            last_modified="2024-01-01"
        )
        self.assertEqual(base.name, "Test Base")
        self.assertEqual(base.persons_count, 1)
        self.assertEqual(base.families_count, 1)

class TestAuth(unittest.TestCase):
    """Tests d'authentification"""
    
    def test_auth_result_success(self):
        """Test résultat auth succès"""
        auth = AuthResult.success("user", is_wizard=True)
        self.assertTrue(auth.is_authenticated)
        self.assertTrue(auth.is_wizard)
        self.assertFalse(auth.is_friend)
    
    def test_auth_result_failed(self):
        """Test résultat auth échec"""
        auth = AuthResult.failed("user")
        self.assertFalse(auth.is_authenticated)
        self.assertFalse(auth.is_wizard)
        self.assertFalse(auth.is_friend)
    
    def test_auth_factory(self):
        """Test factory auth"""
        factory = AuthStrategyFactory("wizard123", "friend456")
        
        # Test wizard
        import base64
        credentials = base64.b64encode(b"admin:wizard123").decode()
        result = factory.authenticate("basic", credentials)
        self.assertTrue(result.is_authenticated)
        self.assertTrue(result.is_wizard)
        
        # Test friend
        credentials = base64.b64encode(b"user:friend456").decode()
        result = factory.authenticate("basic", credentials)
        self.assertTrue(result.is_authenticated)
        self.assertTrue(result.is_friend)
        
        # Test échec
        credentials = base64.b64encode(b"user:wrong").decode()
        result = factory.authenticate("basic", credentials)
        self.assertFalse(result.is_authenticated)

class TestCommands(unittest.TestCase):
    """Tests des commandes"""
    
    def test_get_person_command(self):
        """Test commande get person"""
        person = Person(id=1, first_name="Jean", surname="Dupont")
        
        class MockRepository:
            def get_person_by_id(self, base_name, person_id):
                return person if person_id == 1 else None
        
        repo = MockRepository()
        command = GetPersonCommand("test", 1, repo)
        result = command.execute()
        
        self.assertIsNotNone(result)
        self.assertEqual(result.display_name, "Jean Dupont")
    
    def test_search_persons_command(self):
        """Test commande search persons"""
        person = Person(id=1, first_name="Jean", surname="Dupont")
        
        class MockRepository:
            def search_persons(self, base_name, query):
                return [person] if "jean" in query.lower() else []
        
        repo = MockRepository()
        command = SearchPersonsCommand("test", "jean", repo)
        results = command.execute()
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].display_name, "Jean Dupont")

class TestRobotProtectionSimple(unittest.TestCase):
    """Tests protection robots (version simplifiée)"""
    
    def test_robot_detector_simple(self):
        """Test détecteur robots simplifié"""
        class SimpleRobotDetector:
            def __init__(self, max_requests=3):
                self.max_requests = max_requests
                self.access_times = {}
            
            def is_robot_activity(self, client_ip):
                import time
                current_time = time.time()
                
                if client_ip not in self.access_times:
                    self.access_times[client_ip] = []
                
                # Nettoyer les anciennes entrées
                self.access_times[client_ip] = [
                    t for t in self.access_times[client_ip] 
                    if current_time - t < 60
                ]
                
                # Ajouter l'accès actuel
                self.access_times[client_ip].append(current_time)
                
                return len(self.access_times[client_ip]) > self.max_requests
        
        detector = SimpleRobotDetector(max_requests=3)
        
        # Test normal
        self.assertFalse(detector.is_robot_activity("192.168.1.1"))
        self.assertFalse(detector.is_robot_activity("192.168.1.1"))
        self.assertFalse(detector.is_robot_activity("192.168.1.1"))
        
        # Test robot
        self.assertTrue(detector.is_robot_activity("192.168.1.1"))

class TestPatterns(unittest.TestCase):
    """Tests des patterns"""
    
    def test_strategy_pattern(self):
        """Test Strategy Pattern"""
        from domain.services.auth_strategies import BasicAuthStrategy, DigestAuthStrategy
        
        basic_strategy = BasicAuthStrategy("wizard", "friend")
        digest_strategy = DigestAuthStrategy("wizard", "friend")
        
        self.assertIsInstance(basic_strategy, BasicAuthStrategy)
        self.assertIsInstance(digest_strategy, DigestAuthStrategy)
    
    def test_command_pattern(self):
        """Test Command Pattern"""
        from use_cases.commands import RenderPageCommand
        
        class MockTemplateStrategy:
            def render(self, template_name, context):
                return f"<html><body><h1>{context.get('title', 'Page')}</h1></body></html>"
        
        template_strategy = MockTemplateStrategy()
        command = RenderPageCommand("test.html", {"title": "Test"}, template_strategy)
        result = command.execute()
        
        self.assertIn("Test", result)
        self.assertIn("<html>", result)

def run_tests():
    """Lance tous les tests"""
    print("🧪 Tests unitaires GeneWeb GWD (Simplifiés)")
    print("=" * 50)
    
    # Créer la suite de tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Ajouter les tests
    suite.addTests(loader.loadTestsFromTestCase(TestEntities))
    suite.addTests(loader.loadTestsFromTestCase(TestAuth))
    suite.addTests(loader.loadTestsFromTestCase(TestCommands))
    suite.addTests(loader.loadTestsFromTestCase(TestRobotProtectionSimple))
    suite.addTests(loader.loadTestsFromTestCase(TestPatterns))
    
    # Lancer les tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Résumé
    print(f"\n📊 Résumé des tests:")
    print(f"   ✅ Réussis: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   ❌ Échecs: {len(result.failures)}")
    print(f"   💥 Erreurs: {len(result.errors)}")
    print(f"   📈 Total: {result.testsRun}")
    
    if result.failures:
        print(f"\n❌ Échecs:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")
    
    if result.errors:
        print(f"\n💥 Erreurs:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    if success:
        print("\n🎉 Tous les tests sont passés !")
    else:
        print("\n❌ Certains tests ont échoué !")
