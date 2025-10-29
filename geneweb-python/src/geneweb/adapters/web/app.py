"""FastAPI application for GeneWeb server."""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse

from geneweb.adapters.config.settings import ServerSettings
from geneweb.adapters.database.gwdb_repository import GwdbBaseRepository


def create_app(settings: ServerSettings) -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="GeneWeb",
        description="GeneWeb Web Daemon - Python Implementation",
        version="0.1.0",
        debug=settings.debug,
    )
    
    # Initialize repository
    base_repo = GwdbBaseRepository(settings.base_dir)
    
    @app.get("/health")
    async def health_check() -> dict:
        """Health check endpoint."""
        return {"status": "ok", "version": "0.1.0"}
    
    @app.get("/robots.txt", response_class=PlainTextResponse)
    async def robots_txt() -> str:
        """Serve robots.txt - blocks all robots by default."""
        return "User-agent: *\nDisallow: /\n"
    
    @app.get("/{base_name}/person", response_class=HTMLResponse)
    async def person_page(base_name: str, i: int = 0) -> str:
        """Person page."""
        if not base_repo.exists(base_name):
            raise HTTPException(status_code=404, detail=f"Base '{base_name}' not found")
        
        person_repo = base_repo.get_person_repository(base_name)
        person = person_repo.get_by_id(i)
        
        if not person:
            raise HTTPException(status_code=404, detail=f"Person {i} not found")
        
        # Simple HTML for now - will be replaced with templates
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>{person.display_name}</title>
</head>
<body>
    <h1>{person.display_name}</h1>
    <p>ID: {person.id}</p>
    <p>Sex: {person.sex.name}</p>
    {f'<p>Born: {person.birth_place}</p>' if person.birth_place else ''}
</body>
</html>"""
    
    @app.get("/{base_name}/family", response_class=HTMLResponse)
    async def family_page(base_name: str, i: int = 0) -> str:
        """Family page."""
        if not base_repo.exists(base_name):
            raise HTTPException(status_code=404, detail=f"Base '{base_name}' not found")
        
        family_repo = base_repo.get_family_repository(base_name)
        family = family_repo.get_by_id(i)
        
        if not family:
            return f"""<!DOCTYPE html>
<html><head><title>Family {i}</title></head>
<body><h1>Family {i}</h1><p>Not found (stub implementation)</p></body>
</html>"""
        
        return f"""<!DOCTYPE html>
<html><head><title>Family {i}</title></head>
<body><h1>Family {i}</h1></body>
</html>"""
    
    @app.get("/{base_name}", response_class=HTMLResponse)
    async def base_homepage(base_name: str, request: Request, m: str | None = None) -> str:
        """Homepage for a specific base."""
        if not base_repo.exists(base_name):
            raise HTTPException(status_code=404, detail=f"Base '{base_name}' not found")
        
        person_repo = base_repo.get_person_repository(base_name)
        count = person_repo.count()
        
        # Handle different modes
        if m == "NG":  # Welcome page
            title = f"Base {base_name}"
        else:
            title = f"Base {base_name}"
        
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
</head>
<body>
    <h1>{base_name}</h1>
    <p>Number of persons: {count}</p>
    <p><a href="/{base_name}/person?i=0">View person 0</a></p>
</body>
</html>"""
    
    return app
