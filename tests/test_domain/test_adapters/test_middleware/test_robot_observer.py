"""Tests pour le détecteur de robots - 20 lignes max par fonction"""
import sys
from pathlib import Path
import unittest
from datetime import datetime, timedelta

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "src" / "python"))

from gwd.adapters.middleware.robot_observer import RobotDetector


def test_robot_detection():
    """Test détection de robot par seuil"""
    detector = RobotDetector(max_requests_per_minute=10)
    now = datetime.now()
    
    # Simuler 11 requêtes (plus que le seuil)
    for i in range(11):
        detector.observe("192.168.1.1", "/", now)
    
    # Vérifier blocage
    assert detector.is_blocked("192.168.1.1")
    assert detector.is_suspicious("192.168.1.1")


def test_no_robot_detection():
    """Test pas de détection sous le seuil"""
    detector = RobotDetector(max_requests_per_minute=10)
    now = datetime.now()
    
    # Simuler 5 requêtes (moins que le seuil)
    for i in range(5):
        detector.observe("192.168.1.2", "/", now)
    
    # Vérifier pas de blocage
    assert not detector.is_blocked("192.168.1.2")
    assert not detector.is_suspicious("192.168.1.2")


def test_request_counting():
    """Test comptage des requêtes"""
    detector = RobotDetector(max_requests_per_minute=10)
    now = datetime.now()
    
    # Ajouter 5 requêtes (en-dessous du seuil)
    for i in range(5):
        detector.observe("192.168.1.3", "/test", now)
    
    # Vérifier pas de blocage
    assert not detector.is_blocked("192.168.1.3")
    
    # Ajouter 6 requêtes de plus (total > seuil)
    for i in range(6):
        detector.observe("192.168.1.3", "/test", now)
    
    # Vérifier blocage
    assert detector.is_blocked("192.168.1.3")


def test_clear_ip():
    """Test effacement des données d'une IP"""
    detector = RobotDetector(max_requests_per_minute=10)
    now = datetime.now()
    
    # Simuler 15 requêtes (plus que le seuil)
    for i in range(15):
        detector.observe("192.168.1.4", "/", now)
    
    # Vérifier blocage initial
    assert detector.is_blocked("192.168.1.4")
    
    # Effacer les données
    detector.clear_ip("192.168.1.4")
    
    # Vérifier déblocage
    assert not detector.is_blocked("192.168.1.4")
    assert not detector.is_suspicious("192.168.1.4")
