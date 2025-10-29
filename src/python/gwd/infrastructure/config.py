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
    bases_dir: str = "bases"
    cache_enabled: bool = True
    
    # Auth
    wizard_password: Optional[str] = None
    friend_password: Optional[str] = None
    use_digest_auth: bool = False
    
    # Sécurité
    robot_protection: bool = True
    max_requests_per_minute: int = 60
    
    # Templates
    templates_dir: str = "templates"
    static_dir: str = "static"
    
    class Config:
        env_file = ".env"
        env_prefix = "GWD_"
