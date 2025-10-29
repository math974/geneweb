"""Application Web FastAPI pour GeneWeb GWD - 20 lignes max par fonction"""
import time
from typing import Optional
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from gwd.adapters.database.base_repository import BaseRepository
from gwd.use_cases.commands import GetPersonCommand, SearchPersonsCommand
from gwd.adapters.web.template_strategies import TemplateStrategy, Jinja2TemplateStrategy


def create_app(config, repository: Optional[BaseRepository] = None):
    """Créer l'application FastAPI - MAX 20 LIGNES"""
    app = FastAPI(title="GeneWeb GWD")
    
    # Configuration
    templates_dir = Path(config.templates_dir) if config else Path("src/python/gwd/templates")
    static_dir = Path(config.static_dir) if config else Path("src/python/gwd/static")
    
    # Template strategy
    template_strategy = Jinja2TemplateStrategy(str(templates_dir))
    
    # Servir les fichiers statiques
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # Middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    
    # Routes
    @app.get("/{base_name}", response_class=HTMLResponse)
    async def home(base_name: str, request: Request):
        """Page d'accueil - MAX 20 LIGNES"""
        if not repository:
            return "Base repository non configuré"
        
        base = repository.load_base(base_name)
        if not base:
            raise HTTPException(status_code=404, detail=f"Base {base_name} non trouvée")
        
        context = {
            'base': base,
            'base_name': base_name,
            'persons_count': base.persons_count,
            'families_count': base.families_count,
            'request': request
        }
        
        return template_strategy.render('base_home', context)
    
    @app.get("/{base_name}/person/{person_id}", response_class=HTMLResponse)
    async def person_page(base_name: str, person_id: int, request: Request):
        """Page personne - MAX 20 LIGNES"""
        if not repository:
            return "Base repository non configuré"
        
        cmd = GetPersonCommand(repository)
        person = cmd.execute(base_name, person_id)
        
        if not person:
            raise HTTPException(status_code=404, detail=f"Personne {person_id} non trouvée")
        
        context = {
            'person': person,
            'base_name': base_name,
            'request': request
        }
        
        return template_strategy.render('person', context)
    
    @app.get("/{base_name}/search", response_class=HTMLResponse)
    async def search(base_name: str, q: str, request: Request):
        """Recherche - MAX 20 LIGNES"""
        if not repository:
            return "Base repository non configuré"
        
        cmd = SearchPersonsCommand(repository)
        results = cmd.execute(base_name, q)
        
        context = {
            'query': q,
            'base_name': base_name,
            'results': results,
            'count': len(results),
            'request': request
        }
        
        return template_strategy.render('search_results', context)
    
    return app
