"""Observer Pattern pour la Protection Robots - 20 lignes max"""
from typing import Dict, List, Optional
from collections import defaultdict
import time
from fastapi import Request
from fastapi.responses import Response
from .middleware_chain import MiddlewareHandler

class RobotDetector:
    """Détecteur de robots - 20 lignes max"""

    def __init__(self, max_requests: int = 60):
        self.max_requests = max_requests
        self.access_times: Dict[str, List[float]] = defaultdict(list)
        self.blocked_ips: set = set()

    def is_robot_activity(self, client_ip: str) -> bool:
        current_time = time.time()
        self._cleanup_old_entries(client_ip, current_time)
        self._record_access(client_ip, current_time)
        return self._exceeds_limit(client_ip)

    def _cleanup_old_entries(self, client_ip: str, current_time: float):
        self.access_times[client_ip] = [
            t for t in self.access_times[client_ip]
            if current_time - t < 60
        ]

    def _record_access(self, client_ip: str, current_time: float):
        self.access_times[client_ip].append(current_time)

    def _exceeds_limit(self, client_ip: str) -> bool:
        return len(self.access_times[client_ip]) > self.max_requests

    def block_ip(self, client_ip: str):
        self.blocked_ips.add(client_ip)

    def is_blocked(self, client_ip: str) -> bool:
        return client_ip in self.blocked_ips

class RobotMiddlewareHandler(MiddlewareHandler):
    """Handler protection robots - 20 lignes max"""

    def __init__(self, detector: RobotDetector):
        super().__init__()
        self.detector = detector

    def handle(self, request: Request) -> Optional[Response]:
        client_ip = self._get_client_ip(request)

        if self.detector.is_blocked(client_ip):
            return self._create_blocked_response()

        if self.detector.is_robot_activity(client_ip):
            self.detector.block_ip(client_ip)
            return self._create_robot_response()

        return self._pass_to_next(request)

    def _get_client_ip(self, request: Request) -> str:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _create_blocked_response(self) -> Response:
        from fastapi.responses import Response
        return Response(content="IP blocked", status_code=403)

    def _create_robot_response(self) -> Response:
        from fastapi.responses import Response
        return Response(content="Robot detected", status_code=403)
