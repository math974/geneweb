"""FastAPI server implementation using uvicorn."""

import uvicorn

from geneweb.adapters.config.settings import ServerSettings
from geneweb.adapters.web.app import create_app


class GeneWebServer:
    """GeneWeb server wrapper for FastAPI/uvicorn."""
    
    def __init__(self, settings: ServerSettings):
        """Initialize server with settings."""
        self.settings = settings
        self.app = create_app(settings)
    
    def run(self) -> None:
        """Run the server with uvicorn."""
        uvicorn_config = {
            "app": self.app,
            "host": self.settings.bind_address or "0.0.0.0",
            "port": self.settings.port,
            "log_level": self._get_log_level(),
            "access_log": True,
        }
        
        # Add timeout configuration
        if self.settings.conn_timeout:
            uvicorn_config["timeout_keep_alive"] = self.settings.conn_timeout
        
        uvicorn.run(**uvicorn_config)
    
    def _get_log_level(self) -> str:
        """Convert numeric log level to uvicorn log level."""
        # Map syslog levels to uvicorn levels
        level_map = {
            0: "critical",
            1: "critical",
            2: "critical",
            3: "error",
            4: "warning",
            5: "warning",
            6: "info",
            7: "debug",
        }
        return level_map.get(self.settings.log_level, "info")
