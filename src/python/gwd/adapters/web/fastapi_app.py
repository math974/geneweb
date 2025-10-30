"""Application FastAPI modulaire - 20 lignes max par fonction"""
from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# Use relative imports when running from gwd directory
try:
    from adapters.middleware.middleware_chain import MiddlewareHandler, AuthMiddlewareHandler
    from adapters.middleware.robot_observer import RobotDetector, RobotMiddlewareHandler
    from domain.services.auth_factory import AuthStrategyFactory
    from adapters.database.base_repository import MessagePackBaseRepository
    from adapters.web.template_strategies import PersonTemplateStrategy, BaseTemplateStrategy
    from use_cases.commands import GetPersonCommand, SearchPersonsCommand, RenderPageCommand
except ImportError:
    # Fallback for absolute imports if module is installed
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
        import os
        static_dir = self.settings.static_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static")
        if os.path.exists(static_dir):
            self.app.mount("/static", StaticFiles(directory=static_dir), name="static")

        @self.app.get("/", response_class=HTMLResponse)
        async def get_root(request: Request):
            return await self._handle_root(request)

        @self.app.get("/{base_name}", response_class=HTMLResponse)
        async def get_base_home(base_name: str, request: Request):
            return await self._handle_base_home(base_name, request)

        @self.app.get("/{base_name}/person/{person_id}", response_class=HTMLResponse)
        async def get_person_page(base_name: str, person_id: int, request: Request, m: str = ""):
            return await self._handle_person_page(base_name, person_id, request, m)

        @self.app.get("/{base_name}/search", response_class=HTMLResponse)
        async def get_search_page(base_name: str, request: Request, q: str = ""):
            return await self._handle_search_page(base_name, request, q)

        @self.app.get("/{base_name}/stats", response_class=HTMLResponse)
        async def get_stats_page(base_name: str, request: Request):
            return await self._handle_stats_page(base_name, request)

        @self.app.post("/upload", response_class=HTMLResponse)
        async def upload_gedcom_new(request: Request,
                                   file: UploadFile = File(...),
                                   new_base_name: str = Form(...)):
            return await self._handle_upload_gedcom("", request, file, new_base_name)

        @self.app.post("/{base_name}/upload", response_class=HTMLResponse)
        async def upload_gedcom(base_name: str, request: Request,
                               file: UploadFile = File(...),
                               new_base_name: str = Form(None)):
            return await self._handle_upload_gedcom(base_name, request, file, new_base_name)

    async def _handle_root(self, request: Request) -> HTMLResponse:
        """Gère la page d'accueil principale - 20 lignes max"""
        bases = self.repository.list_bases()

        # Si une seule base, rediriger vers elle
        if len(bases) == 1:
            return RedirectResponse(url=f"/{bases[0]}", status_code=303)

        context = {
            'bases': bases,
            'lang': 'en',
            'request': request
        }

        html = self.base_template_strategy.render("index.html", context)
        return HTMLResponse(content=html)

    async def _handle_base_home(self, base_name: str, request: Request) -> HTMLResponse:
        """Gère la page d'accueil - 20 lignes max"""
        base = self.repository.load_base(base_name)
        if not base:
            raise HTTPException(status_code=404, detail="Base introuvable")

        success_param = request.query_params.get('success', '')

        command = RenderPageCommand(
            "base_home.html",
            {
                'base_name': base_name,
                'persons_count': len(base.persons),
                'families_count': len(base.families),
                'lang': 'en',
                'request': request
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

    async def _handle_search_page(self, base_name: str, request: Request, q: str) -> HTMLResponse:
        """Gère la page recherche - 20 lignes max"""
        base = self.repository.load_base(base_name)
        if not base:
            raise HTTPException(status_code=404, detail="Base introuvable")

        results = []
        if q:
            command = SearchPersonsCommand(base_name, q, self.repository)
            results = command.execute()

        context = {
            'base_name': base_name,
            'query': q,
            'results': results,
            'lang': 'en'
        }

        html = self.base_template_strategy.render("search.html", context)
        return HTMLResponse(content=html)

    async def _handle_stats_page(self, base_name: str, request: Request) -> HTMLResponse:
        """Gère la page statistiques - 20 lignes max"""
        base = self.repository.load_base(base_name)
        if not base:
            raise HTTPException(status_code=404, detail="Base introuvable")

        # Calculer quelques statistiques simples
        persons_with_birth = sum(1 for p in base.persons.values() if p.birth)
        persons_with_death = sum(1 for p in base.persons.values() if p.death)
        families_with_marriage = sum(1 for f in base.families.values() if f.marriage_date)

        context = {
            'base_name': base_name,
            'persons_count': len(base.persons),
            'families_count': len(base.families),
            'persons_with_birth': persons_with_birth,
            'persons_with_death': persons_with_death,
            'families_with_marriage': families_with_marriage,
            'lang': 'en'
        }

        html = self.base_template_strategy.render("stats.html", context)
        return HTMLResponse(content=html)

    async def _handle_upload_gedcom(self, base_name: str, request: Request,
                                    file: UploadFile, new_base_name: str) -> HTMLResponse:
        """Gère l'upload et la conversion de fichier GEDCOM - 20 lignes max"""
        import tempfile
        import subprocess
        import os

        if not file.filename.endswith(('.ged', '.GED')):
            raise HTTPException(status_code=400, detail="Le fichier doit être un .ged")

        target_base = new_base_name or base_name
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, file.filename)

        try:
            content = await file.read()
            with open(temp_file, 'wb') as f:
                f.write(content)

            # Use Python module directly for ged2gwb
            import sys
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            bases_dir = self.settings.bases_dir or "bases"
            python_bin = sys.executable

            result = subprocess.run(
                [python_bin, "-m", "ged2gwb", "-o", target_base, "-bd", bases_dir, temp_file],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=300,
                env={**os.environ, "PYTHONPATH": project_root}
            )

            os.remove(temp_file)
            os.rmdir(temp_dir)

            if result.returncode == 0:
                # Invalider le cache pour forcer le rechargement
                if target_base in self.repository._cache:
                    del self.repository._cache[target_base]
                return RedirectResponse(url=f"/{target_base}?success=upload", status_code=303)
            else:
                error_msg = result.stderr or result.stdout or "Unknown error"
                raise HTTPException(status_code=500, detail=f"Erreur conversion: {error_msg}")
        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=500, detail="Timeout lors de la conversion")
        except Exception as e:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
            raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
