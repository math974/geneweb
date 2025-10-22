"""Factory pour les stratégies d'auth - 20 lignes max"""
from typing import Dict, Type
from .auth_strategies import AuthStrategy, BasicAuthStrategy, DigestAuthStrategy

class AuthStrategyFactory:
    """Factory pour les stratégies d'auth - 20 lignes max"""
    
    def __init__(self, wizard_password: str, friend_password: str):
        self.strategies: Dict[str, AuthStrategy] = {
            "basic": BasicAuthStrategy(wizard_password, friend_password),
            "digest": DigestAuthStrategy(wizard_password, friend_password)
        }
    
    def get_strategy(self, auth_type: str) -> AuthStrategy:
        return self.strategies.get(auth_type, self.strategies["basic"])
    
    def authenticate(self, auth_type: str, credentials: str):
        strategy = self.get_strategy(auth_type)
        return strategy.authenticate(credentials)
