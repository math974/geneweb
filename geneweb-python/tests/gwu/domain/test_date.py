"""Tests unitaires pour l'entité Date."""

import pytest

from geneweb.common.types import DatePrecision
from geneweb.gwu.domain.entities.date import Date


class TestDateCreation:
    """Tests de création de dates."""
    
    def test_create_year_only(self):
        """Test création date avec année seule."""
        date = Date.from_year(1789)
        assert date.year == 1789
        assert date.month == 0
        assert date.day == 0
        assert date.precision == DatePrecision.SURE
    
    def test_create_month_year(self):
        """Test création date avec mois et année."""
        date = Date.from_month_year(8, 1789)
        assert date.year == 1789
        assert date.month == 8
        assert date.day == 0
    
    def test_create_full_date(self):
        """Test création date complète."""
        date = Date.from_full_date(15, 8, 1789)
        assert date.year == 1789
        assert date.month == 8
        assert date.day == 15
    
    def test_invalid_day(self):
        """Test validation jour invalide."""
        with pytest.raises(ValueError, match="Jour invalide"):
            Date(day=32, month=1, year=2000)
    
    def test_invalid_month(self):
        """Test validation mois invalide."""
        with pytest.raises(ValueError, match="Mois invalide"):
            Date(day=1, month=13, year=2000)


class TestDateFormatting:
    """Tests de formatage des dates."""
    
    def test_format_year_only(self):
        """Test format année seule."""
        date = Date.from_year(1789)
        assert date.to_gw_format() == "1789"
    
    def test_format_month_year(self):
        """Test format mois/année."""
        date = Date.from_month_year(8, 1789)
        assert date.to_gw_format() == "8/1789"
    
    def test_format_full_date(self):
        """Test format date complète."""
        date = Date.from_full_date(15, 8, 1789)
        assert date.to_gw_format() == "15/8/1789"
    
    def test_format_year_zero(self):
        """Test format année 0."""
        date = Date.from_year(0)
        assert date.to_gw_format() == "-0"
    
    def test_format_about(self):
        """Test format 'about' (~)."""
        date = Date.from_year(1789, precision=DatePrecision.ABOUT)
        assert date.to_gw_format() == "~1789"
    
    def test_format_maybe(self):
        """Test format 'maybe' (?)."""
        date = Date.from_year(1789, precision=DatePrecision.MAYBE)
        assert date.to_gw_format() == "?1789"
    
    def test_format_before(self):
        """Test format 'before' (<)."""
        date = Date.from_year(1789, precision=DatePrecision.BEFORE)
        assert date.to_gw_format() == "<1789"
    
    def test_format_after(self):
        """Test format 'after' (>)."""
        date = Date.from_year(1789, precision=DatePrecision.AFTER)
        assert date.to_gw_format() == ">1789"


class TestDatePeriods:
    """Tests des périodes de dates."""
    
    def test_format_or_year(self):
        """Test format OrYear (|)."""
        date = Date(
            year=1789,
            precision=DatePrecision.OR_YEAR,
            year2=1790
        )
        assert date.to_gw_format() == "1789|1790"
    
    def test_format_or_year_with_month(self):
        """Test format OrYear avec mois."""
        date = Date(
            month=8,
            year=1789,
            precision=DatePrecision.OR_YEAR,
            month2=9,
            year2=1790
        )
        assert date.to_gw_format() == "8/1789|9/1790"
    
    def test_format_or_year_full_date(self):
        """Test format OrYear avec date complète."""
        date = Date(
            day=15,
            month=8,
            year=1789,
            precision=DatePrecision.OR_YEAR,
            day2=16,
            month2=9,
            year2=1790
        )
        assert date.to_gw_format() == "15/8/1789|16/9/1790"
    
    def test_format_year_interval(self):
        """Test format YearInterval (..)."""
        date = Date(
            year=1789,
            precision=DatePrecision.YEAR_INTERVAL,
            year2=1790
        )
        assert date.to_gw_format() == "1789..1790"
    
    def test_format_year_interval_with_month(self):
        """Test format YearInterval avec mois."""
        date = Date(
            month=8,
            year=1789,
            precision=DatePrecision.YEAR_INTERVAL,
            month2=9,
            year2=1790
        )
        assert date.to_gw_format() == "8/1789..9/1790"
    
    def test_format_or_year_old_gw(self):
        """Test format OrYear en mode old_gw."""
        date = Date(
            month=8,
            year=1789,
            precision=DatePrecision.OR_YEAR,
            month2=9,
            year2=1790
        )
        # En mode old_gw, on n'affiche que l'année pour la période
        assert date.to_gw_format(old_gw=True) == "8/1789|1790"
    
    def test_format_year_interval_old_gw(self):
        """Test format YearInterval en mode old_gw."""
        date = Date(
            month=8,
            year=1789,
            precision=DatePrecision.YEAR_INTERVAL,
            month2=9,
            year2=1790
        )
        assert date.to_gw_format(old_gw=True) == "8/1789..1790"


class TestDatePredicates:
    """Tests des prédicats de date."""
    
    def test_is_complete(self):
        """Test date complète."""
        date = Date.from_full_date(15, 8, 1789)
        assert date.is_complete()
        assert not date.is_partial()
    
    def test_is_partial_month_year(self):
        """Test date partielle (mois/année)."""
        date = Date.from_month_year(8, 1789)
        assert not date.is_complete()
        assert date.is_partial()
    
    def test_is_partial_year_only(self):
        """Test date partielle (année seule)."""
        date = Date.from_year(1789)
        assert not date.is_complete()
        assert date.is_partial()
    
    def test_has_period_or_year(self):
        """Test détection période OrYear."""
        date = Date(year=1789, precision=DatePrecision.OR_YEAR, year2=1790)
        assert date.has_period()
    
    def test_has_period_year_interval(self):
        """Test détection période YearInterval."""
        date = Date(year=1789, precision=DatePrecision.YEAR_INTERVAL, year2=1790)
        assert date.has_period()
    
    def test_no_period(self):
        """Test absence de période."""
        date = Date.from_year(1789)
        assert not date.has_period()


class TestDateStringRepresentation:
    """Tests de représentation string."""
    
    def test_str_representation(self):
        """Test représentation __str__."""
        date = Date.from_full_date(15, 8, 1789)
        assert str(date) == "15/8/1789"
    
    def test_str_with_precision(self):
        """Test __str__ avec précision."""
        date = Date.from_year(1789, precision=DatePrecision.ABOUT)
        assert str(date) == "~1789"
