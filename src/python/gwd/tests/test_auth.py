"""Tests for gwd authentication (adapted from tests.py)."""
import pytest
import sys
import base64
from pathlib import Path

# Add gwd directory to path for relative imports
gwd_dir = Path(__file__).parent.parent
sys.path.insert(0, str(gwd_dir))

try:
    from domain.value_objects.auth_result import AuthResult, AuthStatus
    from domain.services.auth_factory import AuthStrategyFactory
except ImportError:
    pytest.skip("gwd auth modules not available")


class TestAuth:
    """Tests for authentication."""

    def test_auth_result_success(self):
        """Test successful auth result."""
        result = AuthResult.success(user="admin", is_wizard=True)
        assert result.is_authenticated is True
        assert result.is_wizard is True
        assert result.status == AuthStatus.SUCCESS

    def test_auth_result_failure(self):
        """Test failed auth result."""
        result = AuthResult.failed(user="user")
        assert result.is_authenticated is False
        assert result.status == AuthStatus.FAILED

    def test_basic_auth_wizard(self):
        """Test basic auth wizard."""
        factory = AuthStrategyFactory("wizard123", "friend456")
        wizard_creds = base64.b64encode(b"admin:wizard123").decode()
        result = factory.authenticate("basic", wizard_creds)
        assert result.is_authenticated is True
        assert result.is_wizard is True

    def test_basic_auth_friend(self):
        """Test basic auth friend."""
        factory = AuthStrategyFactory("wizard123", "friend456")
        friend_creds = base64.b64encode(b"user:friend456").decode()
        result = factory.authenticate("basic", friend_creds)
        assert result.is_authenticated is True
        assert result.is_wizard is False

    def test_basic_auth_failure(self):
        """Test basic auth failure."""
        factory = AuthStrategyFactory("wizard123", "friend456")
        wrong_creds = base64.b64encode(b"user:wrongpass").decode()
        result = factory.authenticate("basic", wrong_creds)
        assert result.is_authenticated is False

