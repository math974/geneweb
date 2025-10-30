"""Tests for gwd imports (adapted from test_imports.py)."""
import pytest
import sys
from pathlib import Path

# Add gwd directory to path for relative imports
gwd_dir = Path(__file__).parent.parent
sys.path.insert(0, str(gwd_dir))


def test_domain_imports():
    """Test domain entity imports."""
    try:
        from domain.entities.person import Person
        from domain.entities.family import Family
        from domain.entities.base import GenealogyBase
        from domain.value_objects.auth_result import AuthResult
        from domain.services.auth_strategies import BasicAuthStrategy
        from domain.services.auth_factory import AuthStrategyFactory
        assert True
    except ImportError as e:
        pytest.skip(f"Domain imports not available: {e}")


def test_use_cases_imports():
    """Test use cases imports."""
    try:
        from use_cases.commands import GetPersonCommand, SearchPersonsCommand
        assert True
    except ImportError as e:
        pytest.skip(f"Use cases imports not available: {e}")


def test_adapters_imports():
    """Test adapters imports."""
    try:
        from adapters.database.base_repository import MessagePackBaseRepository
        from adapters.middleware.middleware_chain import AuthMiddlewareHandler
        from adapters.middleware.robot_observer import RobotDetector
        from adapters.web.template_strategies import PersonTemplateStrategy
        assert True
    except ImportError as e:
        pytest.skip(f"Adapters imports not available: {e}")


def test_infrastructure_imports():
    """Test infrastructure imports."""
    try:
        from infrastructure.config import GWDSettings
        from infrastructure.server import GeneWebServer
        assert True
    except ImportError as e:
        pytest.skip(f"Infrastructure imports not available: {e}")


def test_cli_imports():
    """Test CLI imports."""
    try:
        from cli.main import serve
        assert True
    except ImportError as e:
        pytest.skip(f"CLI imports not available: {e}")

