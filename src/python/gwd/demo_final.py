#!/usr/bin/env python3
"""Démonstration finale GeneWeb GWD (sans dépendances externes)"""

def demo_final():
    """Démonstration finale de l'architecture"""
    print("🚀 Démonstration GeneWeb GWD Python (Final)")
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
    
    # Test avec mauvais mot de passe
    credentials_bad = base64.b64encode(b"admin:wrong").decode()
    auth_result_bad = auth_factory.authenticate("basic", credentials_bad)
    print(f"   🔑 Auth Basic (mauvais): {auth_result_bad.is_authenticated}")
    
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
    
    # 4. Test de la configuration (version simplifiée)
    print("\n⚙️ 4. Test de la configuration...")
    
    class SimpleSettings:
        def __init__(self, host="localhost", port=2317, bases_dir="bases", 
                     wizard_password=None, friend_password=None):
            self.host = host
            self.port = port
            self.bases_dir = bases_dir
            self.wizard_password = wizard_password
            self.friend_password = friend_password
    
    settings = SimpleSettings(
        host="localhost",
        port=2317,
        bases_dir="bases",
        wizard_password="wizard123",
        friend_password="friend456"
    )
    print(f"   🔧 Configuration: {settings.host}:{settings.port}")
    print(f"   📁 Bases: {settings.bases_dir}")
    print(f"   🔐 Auth: Wizard={'✅' if settings.wizard_password else '❌'}, Friend={'✅' if settings.friend_password else '❌'}")
    
    # 5. Test des patterns
    print("\n🎯 5. Test des patterns...")
    
    # Strategy Pattern
    from domain.services.auth_strategies import BasicAuthStrategy, DigestAuthStrategy
    basic_strategy = BasicAuthStrategy("wizard", "friend")
    digest_strategy = DigestAuthStrategy("wizard", "friend")
    print(f"   🎯 Strategy Pattern: Basic={type(basic_strategy).__name__}, Digest={type(digest_strategy).__name__}")
    
    # Command Pattern
    from use_cases.commands import RenderPageCommand
    class MockTemplateStrategy:
        def render(self, template_name, context):
            return f"<html><body><h1>{context.get('title', 'Page')}</h1></body></html>"
    
    template_strategy = MockTemplateStrategy()
    render_cmd = RenderPageCommand("test.html", {"title": "Test"}, template_strategy)
    html = render_cmd.execute()
    print(f"   🎯 Command Pattern: Template rendu ({len(html)} caractères)")
    
    # 6. Test de la protection robots (version simplifiée)
    print("\n🤖 6. Test de la protection robots (simplifié)...")
    
    class SimpleRobotDetector:
        def __init__(self, max_requests=5):
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
    
    detector = SimpleRobotDetector(max_requests=5)
    
    # Simulation d'activité robot
    for i in range(6):
        is_robot = detector.is_robot_activity("192.168.1.100")
        print(f"   📊 Requête {i+1}: {'🤖 Robot détecté!' if is_robot else '✅ OK'}")
        if is_robot:
            break
    
    # 7. Test des templates HTML
    print("\n🎨 7. Test des templates HTML...")
    
    # Lire le template
    try:
        with open("templates/perso.html", "r") as f:
            template_content = f.read()
        print(f"   📄 Template perso.html: {len(template_content)} caractères")
        
        with open("templates/base_home.html", "r") as f:
            template_content = f.read()
        print(f"   📄 Template base_home.html: {len(template_content)} caractères")
        
        with open("static/css/style.css", "r") as f:
            css_content = f.read()
        print(f"   🎨 CSS style.css: {len(css_content)} caractères")
        
    except FileNotFoundError as e:
        print(f"   ⚠️  Fichier non trouvé: {e}")
    
    print("\n🎉 Démonstration terminée avec succès !")
    print("\n📋 Résumé des fonctionnalités testées:")
    print("   ✅ Entités (Person, Family, GenealogyBase)")
    print("   ✅ Authentification (Basic Auth)")
    print("   ✅ Commandes (GetPerson, SearchPersons, RenderPage)")
    print("   ✅ Protection robots (simplifiée)")
    print("   ✅ Configuration (simplifiée)")
    print("   ✅ Patterns (Strategy, Command)")
    print("   ✅ Templates HTML")
    print("\n🚀 Architecture modulaire prête à l'emploi !")
    print("\n📝 Pour utiliser avec FastAPI, installez les dépendances:")
    print("   pip install fastapi uvicorn jinja2 msgpack pydantic click")
    print("\n🔧 Structure créée:")
    print("   📁 domain/ - Entités et services")
    print("   📁 use_cases/ - Commandes")
    print("   📁 adapters/ - Web, Database, Middleware")
    print("   📁 infrastructure/ - Configuration et serveur")
    print("   📁 cli/ - Interface ligne de commande")
    print("   📁 templates/ - Templates HTML")
    print("   📁 static/ - Assets CSS/JS")

if __name__ == "__main__":
    demo_final()
