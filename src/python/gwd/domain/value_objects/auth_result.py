"""Value Object pour les résultats d'authentification - 20 lignes max"""
from dataclasses import dataclass
from typing import Optional
from enum import Enum

class AuthStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    REQUIRED = "required"

@dataclass
class AuthResult:
    """Résultat d'authentification - 20 lignes max"""
    status: AuthStatus
    user: str
    is_wizard: bool = False
    is_friend: bool = False
    scheme: str = "basic"
    
    @property
    def is_authenticated(self) -> bool:
        return self.status == AuthStatus.SUCCESS
    
    @property
    def success(self) -> bool:
        """Alias pour compatibilité des tests"""
        return self.is_authenticated
    
    @property
    def has_privileges(self) -> bool:
        return self.is_wizard or self.is_friend
    
    @classmethod
    def success(cls, user: str, is_wizard: bool = False, is_friend: bool = False) -> 'AuthResult':
        return cls(AuthStatus.SUCCESS, user, is_wizard, is_friend)
    
    @classmethod
    def failed(cls, user: str = "", _error: str = "") -> 'AuthResult':
        return cls(AuthStatus.FAILED, user)
    
    @classmethod
    def required(cls) -> 'AuthResult':
        return cls(AuthStatus.REQUIRED, "")
