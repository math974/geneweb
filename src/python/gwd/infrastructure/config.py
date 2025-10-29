"""Configuration de l'application - MAX 20 LIGNES"""
from dataclasses import dataclass, asdict
import os
import json
from pathlib import Path
from typing import Dict, Any

@dataclass
class Config:
    """Configuration - MAX 20 LIGNES"""
    bases_dir: str
    port: int = 2317
    host: str = "localhost"
    auth_type: str = "basic"
    wizard_password: str = ""
    friend_password: str = ""
    templates_dir: str = "templates"
    static_dir: str = "static"
    debug: bool = False
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Charger depuis ENV - MAX 20 LIGNES"""
        return cls(
            bases_dir=os.getenv("BASES_DIR", "./bases"),
            port=int(os.getenv("PORT", "2317")),
            host=os.getenv("HOST", "localhost"),
            auth_type=os.getenv("AUTH_TYPE", "basic"),
            wizard_password=os.getenv("WIZARD_PASSWORD", ""),
            friend_password=os.getenv("FRIEND_PASSWORD", ""),
            templates_dir=os.getenv("TEMPLATES_DIR", "templates"),
            static_dir=os.getenv("STATIC_DIR", "static"),
            debug=os.getenv("DEBUG", "").lower() == "true"
        )
        
    @classmethod
    def from_file(cls, config_file: str) -> 'Config':
        """Charger depuis un fichier JSON - MAX 20 LIGNES"""
        path = Path(config_file)
        if not path.exists():
            raise FileNotFoundError(f"Fichier de configuration non trouvé: {config_file}")
        
        with open(path, "r") as f:
            config_data = json.load(f)
            
        return cls(**config_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire - MAX 20 LIGNES"""
        return asdict(self)
    
    def save_to_file(self, config_file: str) -> None:
        """Sauvegarder dans un fichier JSON - MAX 20 LIGNES"""
        path = Path(config_file)
        
        # Créer le répertoire parent si nécessaire
        if not path.parent.exists():
            path.parent.mkdir(parents=True)
            
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
