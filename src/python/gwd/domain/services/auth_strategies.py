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
        token = credentials.strip()
        if token.startswith("Basic "):
            token = token[len("Basic "):]
        decoded = base64.b64decode(token).decode("utf-8")
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
        parsed = self._parse_digest(credentials)
        if not parsed:
            return AuthResult.failed("", "Invalid digest header")
        username = parsed.get("username", "")
        response = parsed.get("response", "")
        if response == self.wizard_password:
            return AuthResult.success(username, is_wizard=True)
        if response == self.friend_password:
            return AuthResult.success(username, is_friend=True)
        return AuthResult.failed(username)
    
    def _parse_digest(self, credentials: str) -> Optional[dict]:
        header = credentials.strip()
        if not header.startswith("Digest "):
            return None
        parts = header[len("Digest "):].split(",")
        kv = {}
        for part in parts:
            if "=" in part:
                k, v = part.strip().split("=", 1)
                kv[k] = v.strip().strip('"')
        return kv
