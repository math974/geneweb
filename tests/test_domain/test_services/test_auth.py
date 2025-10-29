"""Tests pour l'authentification - 20 lignes max par fonction"""
import base64
import sys
from pathlib import Path

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src" / "python"))

from gwd.domain.services.auth_strategies import BasicAuthStrategy, DigestAuthStrategy
from gwd.domain.services.auth_factory import AuthStrategyFactory


def encode_basic(user: str, password: str) -> str:
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    return f"Basic {token}"


def test_basic_auth_valid_wizard():
    strategy = BasicAuthStrategy("wizard123", "friend456")
    result = strategy.authenticate(encode_basic("admin", "wizard123"))
    assert result.success and result.is_wizard


def test_basic_auth_invalid():
    strategy = BasicAuthStrategy("wizard123", "friend456")
    result = strategy.authenticate(encode_basic("admin", "wrong"))
    assert not result.is_authenticated


def test_factory_returns_basic():
    factory = AuthStrategyFactory("wizard123", "friend456")
    result = factory.authenticate("basic", encode_basic("admin", "friend456"))
    assert result.success and result.is_friend


def test_digest_minimal_success_friend():
    strategy = DigestAuthStrategy("wizard123", "friend456")
    header = 'Digest username="john", response="friend456", nonce="abc"'
    result = strategy.authenticate(header)
    assert result.success and result.is_friend


def test_digest_minimal_fail():
    strategy = DigestAuthStrategy("wizard123", "friend456")
    header = 'Digest username="john", response="bad", nonce="abc"'
    result = strategy.authenticate(header)
    assert not result.is_authenticated
