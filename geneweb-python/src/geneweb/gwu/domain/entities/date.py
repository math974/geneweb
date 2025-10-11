"""Entité Date pour GeneWeb."""

from dataclasses import dataclass
from typing import Optional

from geneweb.common.types import Calendar, DatePrecision


@dataclass
class Date:
    """
    Date généalogique avec précision et période.
    
    Supporte:
    - Dates complètes (jour/mois/année)
    - Dates partielles (mois/année ou année seule)
    - Précisions (about, maybe, before, after)
    - Périodes (OrYear, YearInterval)
    - Différents calendriers
    """
    
    # Date principale
    day: int = 0
    month: int = 0
    year: int = 0
    
    # Précision
    precision: DatePrecision = DatePrecision.SURE
    
    # Période (pour OrYear et YearInterval)
    day2: int = 0
    month2: int = 0
    year2: int = 0
    
    # Calendrier
    calendar: Calendar = Calendar.GREGORIAN
    
    def __post_init__(self):
        """Validation post-initialisation."""
        if self.day < 0 or self.day > 31:
            raise ValueError(f"Jour invalide: {self.day}")
        if self.month < 0 or self.month > 12:
            raise ValueError(f"Mois invalide: {self.month}")
    
    @staticmethod
    def _format_year(year: int) -> str:
        """Formate une année (-0 pour l'an 0, sinon nombre)."""
        return "-0" if year == 0 else str(year)
    
    def to_gw_format(self, old_gw: bool = False) -> str:
        """
        Convertit la date en format .gw.
        
        Args:
            old_gw: Si True, utilise le format ancien (< 7.00)
        
        Returns:
            String au format .gw
        
        Examples:
            Date(day=15, month=8, year=1789) -> "15/8/1789"
            Date(month=8, year=1789) -> "8/1789"
            Date(year=1789) -> "1789"
            Date(year=1789, precision=DatePrecision.ABOUT) -> "~1789"
            Date(year=1789, precision=DatePrecision.BEFORE) -> "<1789"
        """
        result = []
        
        # Préfixe de précision
        if self.precision == DatePrecision.ABOUT:
            result.append("~")
        elif self.precision == DatePrecision.MAYBE:
            result.append("?")
        elif self.precision == DatePrecision.BEFORE:
            result.append("<")
        elif self.precision == DatePrecision.AFTER:
            result.append(">")
        
        # Date principale
        year_str = self._format_year(self.year)
        if self.month == 0:
            result.append(year_str)
        elif self.day == 0:
            result.append(f"{self.month}/{year_str}")
        else:
            result.append(f"{self.day}/{self.month}/{year_str}")
        
        # Période (OrYear ou YearInterval)
        if self.precision == DatePrecision.OR_YEAR:
            year2_str = self._format_year(self.year2)
            if old_gw:
                # Format ancien : juste |year2
                result.append(f"|{year2_str}")
            else:
                # Format nouveau : support date complète
                if self.month2 == 0:
                    result.append(f"|{year2_str}")
                elif self.day2 == 0:
                    result.append(f"|{self.month2}/{year2_str}")
                else:
                    result.append(f"|{self.day2}/{self.month2}/{year2_str}")
        
        elif self.precision == DatePrecision.YEAR_INTERVAL:
            year2_str = self._format_year(self.year2)
            if old_gw:
                # Format ancien : juste ..year2
                result.append(f"..{year2_str}")
            else:
                # Format nouveau : support date complète
                if self.month2 == 0:
                    result.append(f"..{year2_str}")
                elif self.day2 == 0:
                    result.append(f"..{self.month2}/{year2_str}")
                else:
                    result.append(f"..{self.day2}/{self.month2}/{year2_str}")
        
        return "".join(result)
    
    @classmethod
    def from_year(cls, year: int, precision: DatePrecision = DatePrecision.SURE) -> "Date":
        """Crée une date à partir d'une année seule."""
        return cls(year=year, precision=precision)
    
    @classmethod
    def from_month_year(
        cls, month: int, year: int, precision: DatePrecision = DatePrecision.SURE
    ) -> "Date":
        """Crée une date à partir d'un mois et d'une année."""
        return cls(month=month, year=year, precision=precision)
    
    @classmethod
    def from_full_date(
        cls,
        day: int,
        month: int,
        year: int,
        precision: DatePrecision = DatePrecision.SURE,
    ) -> "Date":
        """Crée une date complète."""
        return cls(day=day, month=month, year=year, precision=precision)
    
    def is_complete(self) -> bool:
        """Vérifie si la date a jour, mois et année."""
        return self.day > 0 and self.month > 0 and self.year != 0
    
    def is_partial(self) -> bool:
        """Vérifie si la date est partielle (manque jour ou mois)."""
        return not self.is_complete() and self.year != 0
    
    def has_period(self) -> bool:
        """Vérifie si la date a une période (OrYear ou YearInterval)."""
        return self.precision in (DatePrecision.OR_YEAR, DatePrecision.YEAR_INTERVAL)
    
    def __str__(self) -> str:
        """Représentation string (format .gw)."""
        return self.to_gw_format()
