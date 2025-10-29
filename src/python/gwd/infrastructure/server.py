"""Serveur de l'application - MAX 20 LIGNES"""
import logging
from pathlib import Path
from typing import Optional

# Import conditionnels pour permettre les tests sans dépendances
try:
    import uvicorn
    UVICORN_AVAILABLE = True
except ImportError:
    UVICORN_AVAILABLE = False

try:
    from gwd.adapters.web.fastapi_app import create_app
    from gwd.adapters.database.base_repository import MessagePackBaseRepository
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from .config import Config


class Server:
    """Serveur GeneWeb - MAX 20 LIGNES"""
    
    def __init__(self, config: Config):
        """Initialiser le serveur avec une configuration"""
        self.config = config
        self._setup_logging()
        
        if not FASTAPI_AVAILABLE:
            logging.warning("FastAPI n'est pas disponible - fonctionnalités limitées")
            self.app = None
            return
            
        # Initialiser le repository
        self.repository = self._setup_repository()
        
        # Initialiser l'application FastAPI
        self.app = create_app(config, self.repository)
    
    def _setup_logging(self) -> None:
        """Configurer le logging - MAX 20 LIGNES"""
        logging.basicConfig(
            level=logging.DEBUG if self.config.debug else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        if self.config.debug:
            logging.info("Mode DEBUG activé")
    
    def _setup_repository(self):
        """Configurer le repository - MAX 20 LIGNES"""
        from gwd.adapters.database.base_repository import MessagePackBaseRepository
        
        bases_dir = self.config.bases_dir
        if not Path(bases_dir).exists():
            logging.warning(f"Répertoire des bases non trouvé: {bases_dir}")
            Path(bases_dir).mkdir(parents=True, exist_ok=True)
            logging.info(f"Répertoire des bases créé: {bases_dir}")
        
        return MessagePackBaseRepository(bases_dir)
    
    def start(self) -> None:
        """Démarrer le serveur - MAX 20 LIGNES"""
        if not UVICORN_AVAILABLE:
            logging.error("Uvicorn n'est pas disponible - impossible de démarrer")
            return
            
        if not self.app:
            logging.error("Application non initialisée - impossible de démarrer")
            return
            
        logging.info(f"Démarrage du serveur sur {self.config.host}:{self.config.port}")
        logging.info(f"Bases directory: {self.config.bases_dir}")
        
        uvicorn.run(
            self.app,
            host=self.config.host,
            port=self.config.port,
            log_level="debug" if self.config.debug else "info"
        )
    
    def stop(self) -> None:
        """Arrêter le serveur - MAX 20 LIGNES"""
        logging.info("Arrêt du serveur GeneWeb GWD")
        # Uvicorn gère l'arrêt propre
