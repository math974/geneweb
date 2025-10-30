"""Serveur GeneWeb GWD - 20 lignes max"""
import uvicorn
import sys
import os

# Handle imports - try relative first, then absolute
try:
    from adapters.web.fastapi_app import GeneWebFastAPIApp
    from infrastructure.config import GWDSettings
except ImportError:
    # Try from gwd module
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from adapters.web.fastapi_app import GeneWebFastAPIApp
    from infrastructure.config import GWDSettings

class GeneWebServer:
    """Serveur GeneWeb GWD - 20 lignes max"""

    def __init__(self, settings: GWDSettings):
        self.settings = settings
        self.app = GeneWebFastAPIApp(settings)

    def start(self):
        """Démarre le serveur - 20 lignes max"""
        config = uvicorn.Config(
            self.app.app,
            host=self.settings.host,
            port=self.settings.port,
            log_level="debug" if self.settings.debug else "info",
            reload=self.settings.debug,
            workers=1 if self.settings.debug else self.settings.workers
        )
        server = uvicorn.Server(config)
        server.run()

    def stop(self):
        """Arrête le serveur - 20 lignes max"""
        # Implémentation simplifiée
        pass
