"""Value Objects - 20 lignes max par fonction"""
from .auth_result import AuthResult
from .name import Name
from .date import DateRange
from .place import Place

__all__ = ['AuthResult', 'Name', 'DateRange', 'Place']
