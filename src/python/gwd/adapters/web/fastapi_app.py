"""Application FastAPI modulaire - 20 lignes max par fonction"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from geneweb_gwd.adapters.middleware.middleware_chain import MiddlewareHandler, AuthMiddlewareHandler
from geneweb_gwd.adapters.middleware.robot_observer import RobotDetector, RobotMiddlewareHandler
from geneweb_gwd.domain.services.auth_factory import AuthStrategyFactory
from geneweb_gwd.adapters.database.base_repository import MessagePackBaseRepository
from geneweb_gwd.adapters.web.template_strategies import PersonTemplateStrategy, BaseTemplateStrategy
from geneweb_gwd.use_cases.commands import GetPersonCommand, SearchPersonsCommand, RenderPageCommand

class GeneWebFastAPIApp:
    """Application FastAPI modulaire - 20 lignes max par fonction"""
    
    def __init__(self, settings):
        self.settings = settings
        self.app = self._create_app()
        self._setup_components()
        self._setup_middleware_chain()
        self._setup_routes()
    
    def _create_app(self) -> FastAPI:
        """Crée l'application - 20 lignes max"""
        return FastAPI(
            title="GeneWeb Python GWD",
            version="1.0.0",
            description="Serveur GeneWeb modulaire en Python"
        )
    
    def _setup_components(self):
        """Configure les composants - 20 lignes max"""
        self.auth_factory = AuthStrategyFactory(
            self.settings.wizard_password or "",
            self.settings.friend_password or ""
        )
        self.repository = MessagePackBaseRepository(self.settings.bases_dir)
        self.templates = Jinja2Templates(directory=self.settings.templates_dir)
        self.person_template_strategy = PersonTemplateStrategy(self.templates)
        self.base_template_strategy = BaseTemplateStrategy(self.templates)
    
    def _setup_middleware_chain(self):
        """Configure la chaîne de middleware - 20 lignes max"""
        auth_handler = AuthMiddlewareHandler(self.auth_factory)
        robot_detector = RobotDetector(self.settings.max_requests_per_minute)
        robot_handler = RobotMiddlewareHandler(robot_detector)
        
        # Chaîne: Auth -> Robot -> Pass
        auth_handler.set_next(robot_handler)
        self.middleware_chain = auth_handler
    
    def _setup_routes(self):
        """Configure les routes - 20 lignes max"""
        self.app.mount("/static", StaticFiles(directory=self.settings.static_dir), name="static")
        
        @self.app.get("/{base_name}", response_class=HTMLResponse)
        async def get_base_home(base_name: str, request: Request):
            return await self._handle_base_home(base_name, request)
        
        @self.app.get("/{base_name}/person/{person_id}", response_class=HTMLResponse)
        async def get_person_page(base_name: str, person_id: int, request: Request, m: str = ""):
            return await self._handle_person_page(base_name, person_id, request, m)
    
    async def _handle_base_home(self, base_name: str, request: Request) -> HTMLResponse:
        """Gère la page d'accueil - 20 lignes max"""
        base = self.repository.load_base(base_name)
        if not base:
            raise HTTPException(status_code=404, detail="Base introuvable")
        
        command = RenderPageCommand(
            "base_home.html",
            {
                'base_name': base_name,
                'persons_count': len(base.persons),
                'families_count': len(base.families),
                'lang': 'fr'
            },
            self.base_template_strategy
        )
        
        html = command.execute()
        return HTMLResponse(content=html)
    
    async def _handle_person_page(self, base_name: str, person_id: int, 
                                 request: Request, mode: str) -> HTMLResponse:
        """Gère la page personne - 20 lignes max"""
        command = GetPersonCommand(base_name, person_id, self.repository)
        person = command.execute()
        
        if not person:
            raise HTTPException(status_code=404, detail="Personne introuvable")
        
        html = self.person_template_strategy.render_person_page(person, base_name, mode)
        return HTMLResponse(content=html)
