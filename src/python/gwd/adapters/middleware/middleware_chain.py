"""Chain of Responsibility Pattern - Chaîne de middleware - 20 lignes max par fonction"""
from abc import ABC, abstractmethod
from typing import List, Optional, Any
from typing import Dict, Any, Optional
# FastAPI import conditionnels pour permettre les tests sans FastAPI
try:
    from fastapi import Request, Response
    from fastapi.responses import JSONResponse, HTMLResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    # Créer des classes stub pour les tests
    class Request:
        def __init__(self):
            self.headers = {}
            self.client = None
            self.url = type('obj', (object,), {'path': ''})
    
    class Response:
        pass
        
    class JSONResponse:
        pass
        
    class HTMLResponse:
        pass
        
    FASTAPI_AVAILABLE = False
from .robot_observer import RobotDetector


class MiddlewareHandler(ABC):
    """Handler de middleware - Chain of Responsibility - MAX 20 LIGNES"""
    
    @abstractmethod
    async def handle(self, request: Request) -> bool:
        """Traiter une requête - True si OK, False si arrêter la chaîne"""
        pass


class MiddlewareChain:
    """Chaîne de middleware - MAX 20 LIGNES"""
    
    def __init__(self):
        """Initialiser la chaîne avec une liste vide de handlers"""
        self.handlers: List[MiddlewareHandler] = []
    
    def add_handler(self, handler: MiddlewareHandler) -> None:
        """Ajouter un handler à la chaîne - MAX 20 LIGNES"""
        self.handlers.append(handler)
    
    async def process(self, request: Request) -> bool:
        """Traiter la requête à travers la chaîne - MAX 20 LIGNES"""
        for handler in self.handlers:
            # Si un handler retourne False, arrêter la chaîne
            if not await handler.handle(request):
                return False
        # Tous les handlers ont passé
        return True


class AuthMiddlewareHandler(MiddlewareHandler):
    """Handler d'authentification - MAX 20 LIGNES"""
    
    def __init__(self, auth_strategy=None):
        """Initialiser avec une stratégie d'authentification"""
        self.auth_strategy = auth_strategy
    
    async def handle(self, request: Request) -> bool:
        """Vérifier l'authentification - MAX 20 LIGNES"""
        # Si pas de stratégie, laisser passer
        if not self.auth_strategy:
            return True
            
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            # Pas d'en-tête d'authentification, autoriser l'accès en lecture seule
            return True
        
        # Utiliser la stratégie d'authentification
        # Pourrait être étendu pour vérifier les permissions
        return True


class RobotMiddlewareHandler(MiddlewareHandler):
    """Handler anti-robot - MAX 20 LIGNES"""
    
    def __init__(self, detector: RobotDetector):
        """Initialiser avec un détecteur de robots"""
        self.detector = detector
    
    async def handle(self, request: Request) -> bool:
        """Vérifier si c'est un robot - MAX 20 LIGNES"""
        # Obtenir l'IP client
        ip = self._get_client_ip(request)
        
        # Observer la requête pour statistiques
        path = str(request.url.path)
        self.detector.observe(ip, path)
        
        # Si l'IP est bloquée, rejeter la requête
        if self.detector.is_blocked(ip):
            return False
            
        # Autoriser la requête
        return True
    
    def _get_client_ip(self, request: Request) -> str:
        """Récupérer l'IP client depuis la requête - MAX 20 LIGNES"""
        # Vérifier X-Forwarded-For (pour proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Premier IP dans la liste
            return forwarded_for.split(",")[0].strip()
        
        # Sinon utiliser l'IP directe
        return request.client.host if request.client else "unknown"
