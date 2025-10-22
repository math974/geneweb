#!/usr/bin/env python3
"""Démonstration complète GeneWeb GWD"""

def demo_complete():
    """Démonstration complète de l'architecture"""
    print("🚀 Démonstration GeneWeb GWD Python")
    print("=" * 50)
    
    # 1. Test des entités
    print("\n📋 1. Test des entités...")
    from domain.entities.person import Person
    from domain.entities.family import Family
    from domain.entities.base import GenealogyBase
    
    person = Person(
        id=1, 
        first_name="Jean", 
        surname="Dupont",
        public_name="Jean-Pierre",
        occ=1
    )
    print(f"   👤 Personne: {person.display_name}")
    
    family = Family(
        id=1, 
        husband_id=1, 
        wife_id=2,
        marriage_date=None
    )
    print(f"   👨‍👩‍👧‍👦 Famille: {family.id}")
    
    base = GenealogyBase(
        name="Demo Base",
        path="/demo",
        persons={1: person},
        families={1: family},
        last_modified="2024-01-01"
    )
    print(f"   📁 Base: {base.name} ({base.persons_count} personnes, {base.families_count} familles)")
    
    # 2. Test de l'authentification
    print("\n🔐 2. Test de l'authentification...")
    from domain.services.auth_factory import AuthStrategyFactory
    
    auth_factory = AuthStrategyFactory("wizard123", "friend456")
    
    # Test Basic Auth
    import base64
    credentials = base64.b64encode(b"admin:wizard123").decode()
    auth_result = auth_factory.authenticate("basic", credentials)
    print(f"   🔑 Auth Basic: {auth_result.is_authenticated} (Wizard: {auth_result.is_wizard})")
    
    # 3. Test des commandes
    print("\n⚡ 3. Test des commandes...")
    from use_cases.commands import GetPersonCommand, SearchPersonsCommand
    
    # Simulation d'un repository
    class MockRepository:
        def get_person_by_id(self, base_name, person_id):
            return person if person_id == 1 else None
        
        def search_persons(self, base_name, query):
            return [person] if "jean" in query.lower() else []
    
    repo = MockRepository()
    
    get_cmd = GetPersonCommand("demo", 1, repo)
    found_person = get_cmd.execute()
    print(f"   🔍 Commande GetPerson: {found_person.display_name if found_person else 'Non trouvé'}")
    
    search_cmd = SearchPersonsCommand("demo", "jean", repo)
    results = search_cmd.execute()
    print(f"   🔍 Commande Search: {len(results)} résultats")
    
    # 4. Test de la protection robots
    print("\n🤖 4. Test de la protection robots...")
    from adapters.middleware.robot_observer import RobotDetector
    
    detector = RobotDetector(max_requests=5)
    
    # Simulation d'activité robot
    for i in range(6):
        is_robot = detector.is_robot_activity("192.168.1.100")
        print(f"   📊 Requête {i+1}: {'🤖 Robot détecté!' if is_robot else '✅ OK'}")
        if is_robot:
            break
    
    # 5. Test des templates
    print("\n🎨 5. Test des templates...")
    from adapters.web.template_strategies import PersonTemplateStrategy, BaseTemplateStrategy
    
    # Simulation d'un template engine
    class MockTemplates:
        def get_template(self, name):
            return MockTemplate()
    
    class MockTemplate:
        def render(self, context):
            return f"<html><body><h1>{context.get('person', {}).get('display_name', 'Unknown')}</h1></body></html>"
    
    templates = MockTemplates()
    person_strategy = PersonTemplateStrategy(templates)
    
    html = person_strategy.render_person_page(person, "demo", "")
    print(f"   📄 Template rendu: {len(html)} caractères")
    
    # 6. Test de la configuration
    print("\n⚙️ 6. Test de la configuration...")
    from infrastructure.config import GWDSettings
    
    settings = GWDSettings(
        host="localhost",
        port=2317,
        bases_dir="bases",
        wizard_password="wizard123",
        friend_password="friend456"
    )
    print(f"   🔧 Configuration: {settings.host}:{settings.port}")
    print(f"   📁 Bases: {settings.bases_dir}")
    print(f"   🔐 Auth: Wizard={'✅' if settings.wizard_password else '❌'}, Friend={'✅' if settings.friend_password else '❌'}")
    
    print("\n🎉 Démonstration terminée avec succès !")
    print("\n📋 Résumé des fonctionnalités testées:")
    print("   ✅ Entités (Person, Family, GenealogyBase)")
    print("   ✅ Authentification (Basic Auth)")
    print("   ✅ Commandes (GetPerson, SearchPersons)")
    print("   ✅ Protection robots")
    print("   ✅ Templates")
    print("   ✅ Configuration")
    print("\n🚀 Architecture modulaire prête à l'emploi !")

if __name__ == "__main__":
    demo_complete()
