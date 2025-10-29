"""Robot Observer Pattern - Détection des robots par IP - 20 lignes max par fonction"""
from typing import Set, Dict, List, Optional
from datetime import datetime, timedelta


class RobotDetector:
    """Détecteur de robots - Observer Pattern - MAX 20 LIGNES"""
    
    def __init__(self, max_requests_per_minute: int = 60):
        """Initialiser le détecteur avec un seuil de requêtes"""
        self.max_requests = max_requests_per_minute
        self.suspicious_ips: Set[str] = set()
        self.request_counts: Dict[str, int] = {}
        self.blocked_ips: Set[str] = set()
        self.timestamps: Dict[str, List[datetime]] = {}
    
    def observe(self, ip: str, path: str, timestamp: datetime = None):
        """Observer une requête - MAX 20 LIGNES"""
        if timestamp is None:
            timestamp = datetime.now()
            
        # Enregistrer la requête
        if ip not in self.timestamps:
            self.timestamps[ip] = []
        self.timestamps[ip].append(timestamp)
        
        # Compter les requêtes récentes (dernière minute)
        recent_requests = self._count_recent_requests(ip, timestamp)
        
        # Détecter les patterns suspects
        if recent_requests > self.max_requests:
            self.blocked_ips.add(ip)
            self.suspicious_ips.add(ip)
    
    def _count_recent_requests(self, ip: str, now: datetime) -> int:
        """Compte les requêtes récentes pour une IP - MAX 20 LIGNES"""
        if ip not in self.timestamps:
            return 0
            
        # Ne garder que les timestamps de la dernière minute
        cutoff = now - timedelta(minutes=1)
        recent = [ts for ts in self.timestamps[ip] if ts >= cutoff]
        
        # Mettre à jour la liste des timestamps
        self.timestamps[ip] = recent
        
        # Réinitialiser le blocage si plus aucune requête récente
        if not recent and ip in self.blocked_ips:
            self.blocked_ips.remove(ip)
        
        return len(recent)
    
    def is_blocked(self, ip: str) -> bool:
        """Vérifier si une IP est bloquée - MAX 20 LIGNES"""
        return ip in self.blocked_ips
    
    def is_suspicious(self, ip: str) -> bool:
        """Vérifier si une IP est suspecte - MAX 20 LIGNES"""
        return ip in self.suspicious_ips
    
    def clear_ip(self, ip: str) -> None:
        """Effacer les données d'une IP - MAX 20 LIGNES"""
        if ip in self.blocked_ips:
            self.blocked_ips.remove(ip)
        if ip in self.suspicious_ips:
            self.suspicious_ips.remove(ip)
        if ip in self.request_counts:
            del self.request_counts[ip]
        if ip in self.timestamps:
            del self.timestamps[ip]
