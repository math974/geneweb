"""Serveur GeneWeb GWD - 20 lignes max"""
import uvicorn
from geneweb_gwd.adapters.web.fastapi_app import GeneWebFastAPIApp
from geneweb_gwd.infrastructure.config import GWDSettings

class GeneWebServer:
    """Serveur GeneWeb GWD - 20 lignes max"""
    
    def __init__(self, settings: GWDSettings):
        self.settings = settings
        self.app = GeneWebFastAPIApp(settings)
    
    def start(self):
        """Démarre le serveur - 20 lignes max"""
        uvicorn.run(
            self.app.app,
            host=self.settings.host,
            port=self.settings.port,
            workers=self.settings.workers if not self.settings.debug else 1,
            log_level="debug" if self.settings.debug else "info"
        )
    
    def stop(self):
        """Arrête le serveur - 20 lignes max"""
        # Implémentation simplifiée
        pass
