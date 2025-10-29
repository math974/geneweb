"""Configuration settings for GeneWeb server."""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerSettings(BaseSettings):
    """Server configuration matching gwd options."""
    
    # Basic server options
    port: int = Field(default=2317, description="Server port (-p)")
    base_dir: Path = Field(default=Path("bases"), description="Bases directory (-bd)")
    html_dir: Path = Field(default=Path("gw"), description="HTML/templates directory (-hd)")
    
    # Network options
    bind_address: Optional[str] = Field(default=None, description="Bind address (-a)")
    only_address: Optional[str] = Field(default=None, description="Only accept from address (-only)")
    no_host_address: bool = Field(default=False, description="No reverse DNS (-no_host_address)")
    
    # Authentication options
    auth_file: Optional[Path] = Field(default=None, description="Authorization file (-auth)")
    friend_password: Optional[str] = Field(default=None, description="Friend password (-friend)")
    wizard_password: Optional[str] = Field(default=None, description="Wizard password (-wizard)")
    use_digest: bool = Field(default=False, description="Use Digest auth (-digest)")
    wizard_just_friend: bool = Field(default=False, description="Wizard just friend (-wjf)")
    
    # Timeout and limits
    conn_timeout: int = Field(default=120, description="Connection timeout (-conn_tmout)")
    login_timeout: int = Field(default=1800, description="Login timeout (-login_tmout)")
    max_clients: Optional[int] = Field(default=None, description="Max clients DEPRECATED (-max_clients)")
    
    # Language and internationalization
    default_lang: str = Field(default="fr", description="Default language (-lang)")
    browser_lang: bool = Field(default=False, description="Use browser language (-blang)")
    cache_langs: Optional[str] = Field(default=None, description="Cache languages (-cache_langs)")
    
    # Interface options
    setup_link: bool = Field(default=False, description="Display setup link (-setup_link)")
    images_url: Optional[str] = Field(default=None, description="Images URL (-images_url)")
    images_dir: Optional[str] = Field(default=None, description="Images directory (-images_dir)")
    allowed_tags_file: Optional[Path] = Field(default=None, description="Allowed tags file (-allowed_tags)")
    
    # Logging and debugging
    log_file: Optional[Path] = Field(default=None, description="Log file (-log)")
    log_level: int = Field(default=6, description="Log level (-log_level)")
    trace_failed_passwd: bool = Field(default=False, description="Trace failed passwords (-trace_failed_passwd)")
    debug: bool = Field(default=False, description="Debug mode (-debug)")
    
    # Advanced options
    redirect_addr: Optional[str] = Field(default=None, description="Redirect address (-redirect)")
    add_lexicon: Optional[Path] = Field(default=None, description="Add lexicon file (-add_lexicon)")
    plugin: Optional[Path] = Field(default=None, description="Plugin file (-plugin)")
    plugins_dir: Optional[Path] = Field(default=None, description="Plugins directory (-plugins)")
    
    # Mode options
    daemon: bool = Field(default=False, description="Daemon mode (-daemon)")
    cgi: bool = Field(default=False, description="CGI mode (-cgi)")
    predictable_mode: bool = Field(default=False, description="Predictable mode (-predictable_mode)")
    
    # Working directory and files
    working_dir: Optional[Path] = Field(default=None, description="Working directory (-wd)")
    no_lock: bool = Field(default=False, description="No file locking (-nolock)")
    
    # Robot exclusion
    robot_exclude: Optional[str] = Field(default=None, description="Robot exclusion (-robot_xcl)")
    min_disp_req: int = Field(default=6, description="Min display requests (-min_disp_req)")
    
    model_config = SettingsConfigDict(
        env_prefix="GWD_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        # Convert relative paths to absolute
        if self.base_dir and not self.base_dir.is_absolute():
            self.base_dir = self.base_dir.resolve()
        if self.html_dir and not self.html_dir.is_absolute():
            self.html_dir = self.html_dir.resolve()
