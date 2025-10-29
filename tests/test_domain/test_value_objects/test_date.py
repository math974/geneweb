"""Tests pour le value object DateRange - 20 lignes max par fonction"""
import pytest
import sys
from pathlib import Path
from datetime import date

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src" / "python"))

from gwd.domain.value_objects.date import DateRange

def test_date_range_creation():
    """Test création d'une plage de dates"""
    dr = DateRange(date(2000, 1, 1), date(2010, 1, 1))
    assert dr.start_date == date(2000, 1, 1)
    assert dr.end_date == date(2010, 1, 1)

def test_date_range_duration():
    """Test durée d'une plage"""
    dr = DateRange(date(2000, 1, 1), date(2010, 1, 1))
    assert dr.duration_days == 3653

def test_date_range_contains():
    """Test si une date est dans la plage"""
    dr = DateRange(date(2000, 1, 1), date(2010, 1, 1))
    assert dr.contains(date(2005, 6, 15))

def test_date_range_not_contains():
    """Test si une date n'est pas dans la plage"""
    dr = DateRange(date(2000, 1, 1), date(2010, 1, 1))
    assert not dr.contains(date(2015, 6, 15))

