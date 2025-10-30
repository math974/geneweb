"""Configuration GeneWeb GWD - 20 lignes max"""
from pydantic_settings import BaseSettings
from typing import List, Optional

class GWDSettings(BaseSettings):
    """Configuration GeneWeb GWD - 20 lignes max"""

    # Serveur
    host: str = "localhost"
    port: int = 2317
    workers: int = 4
    debug: bool = False

    # Bases
    bases_dir: Optional[str] = "bases"
    cache_enabled: bool = True

    # Auth
    wizard_password: Optional[str] = None
    friend_password: Optional[str] = None
    use_digest_auth: bool = False

    # Sécurité
    robot_protection: bool = True
    max_requests_per_minute: int = 60

    # Templates - paths will be resolved relative to gwd module directory
    templates_dir: Optional[str] = None
    static_dir: Optional[str] = None

    def model_post_init(self, __context) -> None:
        """Set default paths relative to module location"""
        import os
        if not self.templates_dir or not os.path.isabs(self.templates_dir):
            module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if not self.templates_dir:
                self.templates_dir = os.path.join(module_dir, "templates")
            if not self.static_dir:
                self.static_dir = os.path.join(module_dir, "static")
            # Ensure absolute paths
            if not os.path.isabs(self.templates_dir):
                self.templates_dir = os.path.abspath(self.templates_dir)
            if not os.path.isabs(self.static_dir):
                self.static_dir = os.path.abspath(self.static_dir)

    class Config:
        env_file = ".env"
        env_prefix = "GWD_"
