"""Stratégies d'authentification - 20 lignes max par fonction"""
from abc import ABC, abstractmethod
from typing import Optional
from ..value_objects.auth_result import AuthResult

class AuthStrategy(ABC):
    """Stratégie d'authentification - 20 lignes max"""
    
    @abstractmethod
    def authenticate(self, credentials: str) -> AuthResult:
        pass

class BasicAuthStrategy(AuthStrategy):
    """Stratégie Basic Auth - 20 lignes max"""
    
    def __init__(self, wizard_password: str, friend_password: str):
        self.wizard_password = wizard_password
        self.friend_password = friend_password
    
    def authenticate(self, credentials: str) -> AuthResult:
        username, password = self._parse_credentials(credentials)
        return self._check_credentials(username, password)
    
    def _parse_credentials(self, credentials: str) -> tuple[str, str]:
        import base64
        decoded = base64.b64decode(credentials).decode("utf-8")
        return decoded.split(":", 1)
    
    def _check_credentials(self, username: str, password: str) -> AuthResult:
        if password == self.wizard_password:
            return AuthResult.success(username, is_wizard=True)
        if password == self.friend_password:
            return AuthResult.success(username, is_friend=True)
        return AuthResult.failed(username)

class DigestAuthStrategy(AuthStrategy):
    """Stratégie Digest Auth - 20 lignes max"""
    
    def __init__(self, wizard_password: str, friend_password: str):
        self.wizard_password = wizard_password
        self.friend_password = friend_password
    
    def authenticate(self, credentials: str) -> AuthResult:
        # Implémentation simplifiée
        return AuthResult.failed()
