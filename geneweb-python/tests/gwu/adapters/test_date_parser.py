"""Tests unitaires pour le DateParser."""

import pytest

from geneweb.common.types import DatePrecision
from geneweb.gwu.adapters.input.date_parser import DateParser


class TestDateParserSimple:
    """Tests de parsing de dates simples."""
    
    def test_parse_year_only(self):
        """Test parsing année seule."""
        date = DateParser.parse("1789")
        assert date is not None
        assert date.year == 1789
        assert date.month == 0
        assert date.day == 0
        assert date.precision == DatePrecision.SURE
    
    def test_parse_month_year(self):
        """Test parsing mois/année."""
        date = DateParser.parse("8/1789")
        assert date is not None
        assert date.year == 1789
        assert date.month == 8
        assert date.day == 0
    
    def test_parse_full_date(self):
        """Test parsing date complète."""
        date = DateParser.parse("15/8/1789")
        assert date is not None
        assert date.year == 1789
        assert date.month == 8
        assert date.day == 15
    
    def test_parse_year_zero(self):
        """Test parsing année zéro (-0)."""
        date = DateParser.parse("-0")
        assert date is not None
        assert date.year == 0


class TestDateParserPrecision:
    """Tests de parsing avec précisions."""
    
    def test_parse_about(self):
        """Test parsing ~1789 (about/circa)."""
        date = DateParser.parse("~1789")
        assert date is not None
        assert date.year == 1789
        assert date.precision == DatePrecision.ABOUT
    
    def test_parse_maybe(self):
        """Test parsing ?1789 (maybe)."""
        date = DateParser.parse("?1789")
        assert date is not None
        assert date.year == 1789
        assert date.precision == DatePrecision.MAYBE
    
    def test_parse_before(self):
        """Test parsing <1789 (before)."""
        date = DateParser.parse("<1789")
        assert date is not None
        assert date.year == 1789
        assert date.precision == DatePrecision.BEFORE
    
    def test_parse_after(self):
        """Test parsing >1789 (after)."""
        date = DateParser.parse(">1789")
        assert date is not None
        assert date.year == 1789
        assert date.precision == DatePrecision.AFTER
    
    def test_parse_precision_with_full_date(self):
        """Test précision avec date complète."""
        date = DateParser.parse("~15/8/1789")
        assert date is not None
        assert date.year == 1789
        assert date.month == 8
        assert date.day == 15
        assert date.precision == DatePrecision.ABOUT


class TestDateParserPeriods:
    """Tests de parsing des périodes."""
    
    def test_parse_or_year(self):
        """Test parsing 1789|1790 (OrYear)."""
        date = DateParser.parse("1789|1790")
        assert date is not None
        assert date.year == 1789
        assert date.year2 == 1790
        assert date.precision == DatePrecision.OR_YEAR
    
    def test_parse_or_year_with_months(self):
        """Test parsing 8/1789|9/1790."""
        date = DateParser.parse("8/1789|9/1790")
        assert date is not None
        assert date.month == 8
        assert date.year == 1789
        assert date.month2 == 9
        assert date.year2 == 1790
        assert date.precision == DatePrecision.OR_YEAR
    
    def test_parse_or_year_full_dates(self):
        """Test parsing 15/8/1789|16/9/1790."""
        date = DateParser.parse("15/8/1789|16/9/1790")
        assert date is not None
        assert date.day == 15
        assert date.month == 8
        assert date.year == 1789
        assert date.day2 == 16
        assert date.month2 == 9
        assert date.year2 == 1790
        assert date.precision == DatePrecision.OR_YEAR
    
    def test_parse_year_interval(self):
        """Test parsing 1789..1790 (YearInterval)."""
        date = DateParser.parse("1789..1790")
        assert date is not None
        assert date.year == 1789
        assert date.year2 == 1790
        assert date.precision == DatePrecision.YEAR_INTERVAL
    
    def test_parse_year_interval_with_months(self):
        """Test parsing 8/1789..9/1790."""
        date = DateParser.parse("8/1789..9/1790")
        assert date is not None
        assert date.month == 8
        assert date.year == 1789
        assert date.month2 == 9
        assert date.year2 == 1790
        assert date.precision == DatePrecision.YEAR_INTERVAL


class TestDateParserEdgeCases:
    """Tests des cas limites."""
    
    def test_parse_empty_string(self):
        """Test parsing string vide."""
        date = DateParser.parse("")
        assert date is None
    
    def test_parse_none(self):
        """Test parsing None."""
        date = DateParser.parse(None)
        assert date is None
    
    def test_parse_whitespace(self):
        """Test parsing espaces."""
        date = DateParser.parse("   ")
        assert date is None
    
    def test_parse_with_leading_trailing_spaces(self):
        """Test parsing avec espaces avant/après."""
        date = DateParser.parse("  1789  ")
        assert date is not None
        assert date.year == 1789


class TestDateParserCompatibility:
    """Tests de compatibilité avec les dates réelles de galichet.gw."""
    
    def test_parse_galichet_dates(self):
        """Test parsing dates du fichier galichet.gw."""
        # Exemples de dates réelles du fichier
        test_cases = [
            ("1813", 1813, 0, 0),
            ("1814", 1814, 0, 0),
            ("7/9/1830", 1830, 9, 7),
            ("<1849", 1849, 0, 0),  # Before
            ("3/3/1835", 1835, 3, 3),
            ("2/2/1836", 1836, 2, 2),
            ("1/1/1815", 1815, 1, 1),
        ]
        
        for date_str, expected_year, expected_month, expected_day in test_cases:
            date = DateParser.parse(date_str)
            assert date is not None, f"Failed to parse: {date_str}"
            assert date.year == expected_year
            assert date.month == expected_month
            assert date.day == expected_day
