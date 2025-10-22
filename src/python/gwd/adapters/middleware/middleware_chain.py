"""Chain of Responsibility pour le Middleware - 20 lignes max"""
from abc import ABC, abstractmethod
from fastapi import Request
from fastapi.responses import Response
from typing import Optional

class MiddlewareHandler(ABC):
    """Handler de middleware - 20 lignes max"""
    
    def __init__(self):
        self._next_handler: Optional[MiddlewareHandler] = None
    
    def set_next(self, handler: 'MiddlewareHandler') -> 'MiddlewareHandler':
        self._next_handler = handler
        return handler
    
    @abstractmethod
    def handle(self, request: Request) -> Optional[Response]:
        pass
    
    def _pass_to_next(self, request: Request) -> Optional[Response]:
        if self._next_handler:
            return self._next_handler.handle(request)
        return None

class AuthMiddlewareHandler(MiddlewareHandler):
    """Handler d'authentification - 20 lignes max"""
    
    def __init__(self, auth_factory):
        super().__init__()
        self.auth_factory = auth_factory
    
    def handle(self, request: Request) -> Optional[Response]:
        if not self._is_auth_required(request):
            return self._pass_to_next(request)
        
        auth_result = self._check_authentication(request)
        return self._handle_auth_result(auth_result) or self._pass_to_next(request)
    
    def _is_auth_required(self, request: Request) -> bool:
        return not request.url.path.startswith("/static/")
    
    def _check_authentication(self, request: Request):
        auth_header = request.headers.get("Authorization", "")
        auth_type = self._extract_auth_type(auth_header)
        credentials = self._extract_credentials(auth_header)
        return self.auth_factory.authenticate(auth_type, credentials)
    
    def _extract_auth_type(self, auth_header: str) -> str:
        return auth_header.split(" ")[0].lower() if auth_header else "basic"
    
    def _extract_credentials(self, auth_header: str) -> str:
        return auth_header.split(" ")[1] if " " in auth_header else ""
    
    def _handle_auth_result(self, auth_result):
        return None if auth_result.is_authenticated else self._create_auth_response()
    
    def _create_auth_response(self) -> Response:
        from fastapi.responses import Response
        return Response(
            content="Authentication required",
            status_code=401,
            headers={"WWW-Authenticate": "Basic realm=\"GeneWeb\""}
        )
