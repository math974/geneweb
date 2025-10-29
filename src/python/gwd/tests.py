#!/usr/bin/env python3
"""Tests unitaires GeneWeb GWD"""

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

class TestRobotProtection(unittest.TestCase):
    """Tests protection robots"""
    
    def test_robot_detector(self):
        """Test détecteur robots"""
        from adapters.middleware.robot_observer import RobotDetector
        
        detector = RobotDetector(max_requests=3)
        
        # Test normal
        self.assertFalse(detector.is_robot_activity("192.168.1.1"))
        self.assertFalse(detector.is_robot_activity("192.168.1.1"))
        self.assertFalse(detector.is_robot_activity("192.168.1.1"))
        
        # Test robot
        self.assertTrue(detector.is_robot_activity("192.168.1.1"))
    
    def test_robot_blocking(self):
        """Test blocage robots"""
        from adapters.middleware.robot_observer import RobotDetector
        
        detector = RobotDetector(max_requests=2)
        
        # Simuler activité robot
        detector.is_robot_activity("192.168.1.100")
        detector.is_robot_activity("192.168.1.100")
        detector.is_robot_activity("192.168.1.100")  # Déclenche blocage
        
        # Vérifier blocage
        self.assertTrue(detector.is_blocked("192.168.1.100"))

def run_tests():
    """Lance tous les tests"""
    print("🧪 Tests unitaires GeneWeb GWD")
    print("=" * 40)
    
    # Créer la suite de tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Ajouter les tests
    suite.addTests(loader.loadTestsFromTestCase(TestEntities))
    suite.addTests(loader.loadTestsFromTestCase(TestAuth))
    suite.addTests(loader.loadTestsFromTestCase(TestCommands))
    suite.addTests(loader.loadTestsFromTestCase(TestRobotProtection))
    
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
