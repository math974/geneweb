"""Parser pour les dates au format .gw."""

import re
from typing import Optional

from geneweb.common.types import DatePrecision
from geneweb.gwu.domain.entities import Date


class DateParser:
    """
    Parser pour les dates au format .gw.
    
    Formats supportés:
    - Année seule: 1789
    - Mois/Année: 8/1789
    - Jour/Mois/Année: 15/8/1789
    - Avant: <1789
    - Après: >1789
    - Circa: ~1789
    - Maybe: ?1789
    - Ou: 1789|1790
    - Intervalle: 1789..1790
    - Année zéro: -0
    """
    
    # Regex pour matcher une date complète avec tous ses composants
    DATE_PATTERN = re.compile(
        r'^([~?<>])?'  # Préfixe de précision (optionnel)
        r'(\d+|[-]0)'  # Jour ou année (ou -0 pour année zéro)
        r'(?:/(\d+|[-]0))?'  # /mois (optionnel)
        r'(?:/(\d+|[-]0))?'  # /année (optionnel)
        r'([|].*)?'  # Période OrYear (optionnel)
        r'([.][.].*)?'  # Période YearInterval (optionnel)
    )
    
    @classmethod
    def parse(cls, date_str: str) -> Optional[Date]:
        """
        Parse une date au format .gw.
        
        Args:
            date_str: String contenant la date
        
        Returns:
            Date parsée ou None si invalide
        
        Examples:
            >>> DateParser.parse("1789")
            Date(year=1789)
            
            >>> DateParser.parse("15/8/1789")
            Date(day=15, month=8, year=1789)
            
            >>> DateParser.parse("~1789")
            Date(year=1789, precision=DatePrecision.ABOUT)
            
            >>> DateParser.parse("1789|1790")
            Date(year=1789, year2=1790, precision=DatePrecision.OR_YEAR)
        """
        if not date_str or not date_str.strip():
            return None
        
        date_str = date_str.strip()
        
        # Gérer les périodes (OrYear et YearInterval)
        if '|' in date_str:
            return cls._parse_or_year(date_str)
        elif '..' in date_str:
            return cls._parse_year_interval(date_str)
        
        # Parse date simple
        match = cls.DATE_PATTERN.match(date_str)
        if not match:
            return None
        
        precision_char = match.group(1)
        part1 = match.group(2)
        part2 = match.group(3)
        part3 = match.group(4)
        
        # Déterminer la précision
        precision = DatePrecision.SURE
        if precision_char == '~':
            precision = DatePrecision.ABOUT
        elif precision_char == '?':
            precision = DatePrecision.MAYBE
        elif precision_char == '<':
            precision = DatePrecision.BEFORE
        elif precision_char == '>':
            precision = DatePrecision.AFTER
        
        # Parser les composants
        if part3:
            # Jour/Mois/Année
            day = cls._parse_number(part1)
            month = cls._parse_number(part2)
            year = cls._parse_number(part3)
            return Date(day=day, month=month, year=year, precision=precision)
        elif part2:
            # Mois/Année
            month = cls._parse_number(part1)
            year = cls._parse_number(part2)
            return Date(month=month, year=year, precision=precision)
        else:
            # Année seule
            year = cls._parse_number(part1)
            return Date(year=year, precision=precision)
    
    @classmethod
    def _parse_or_year(cls, date_str: str) -> Optional[Date]:
        """Parse une date avec OrYear (1789|1790)."""
        parts = date_str.split('|')
        if len(parts) != 2:
            return None
        
        date1 = cls.parse(parts[0])
        date2_str = parts[1].strip()
        
        if not date1:
            return None
        
        # Parse la deuxième partie (peut être juste une année ou une date complète)
        if '/' in date2_str:
            # Date complète
            date2_parts = date2_str.split('/')
            if len(date2_parts) == 3:
                day2 = cls._parse_number(date2_parts[0])
                month2 = cls._parse_number(date2_parts[1])
                year2 = cls._parse_number(date2_parts[2])
            elif len(date2_parts) == 2:
                day2 = 0
                month2 = cls._parse_number(date2_parts[0])
                year2 = cls._parse_number(date2_parts[1])
            else:
                return None
        else:
            # Année seule
            day2 = 0
            month2 = 0
            year2 = cls._parse_number(date2_str)
        
        return Date(
            day=date1.day,
            month=date1.month,
            year=date1.year,
            day2=day2,
            month2=month2,
            year2=year2,
            precision=DatePrecision.OR_YEAR,
        )
    
    @classmethod
    def _parse_year_interval(cls, date_str: str) -> Optional[Date]:
        """Parse une date avec YearInterval (1789..1790)."""
        parts = date_str.split('..')
        if len(parts) != 2:
            return None
        
        date1 = cls.parse(parts[0])
        date2_str = parts[1].strip()
        
        if not date1:
            return None
        
        # Parse la deuxième partie
        if '/' in date2_str:
            date2_parts = date2_str.split('/')
            if len(date2_parts) == 3:
                day2 = cls._parse_number(date2_parts[0])
                month2 = cls._parse_number(date2_parts[1])
                year2 = cls._parse_number(date2_parts[2])
            elif len(date2_parts) == 2:
                day2 = 0
                month2 = cls._parse_number(date2_parts[0])
                year2 = cls._parse_number(date2_parts[1])
            else:
                return None
        else:
            day2 = 0
            month2 = 0
            year2 = cls._parse_number(date2_str)
        
        return Date(
            day=date1.day,
            month=date1.month,
            year=date1.year,
            day2=day2,
            month2=month2,
            year2=year2,
            precision=DatePrecision.YEAR_INTERVAL,
        )
    
    @classmethod
    def _parse_number(cls, num_str: str) -> int:
        """
        Parse un nombre (gère l'année zéro comme -0).
        
        Args:
            num_str: String contenant le nombre
        
        Returns:
            Nombre parsé (0 pour -0)
        """
        if not num_str:
            return 0
        
        num_str = num_str.strip()
        
        if num_str == '-0':
            return 0
        
        try:
            return int(num_str)
        except ValueError:
            return 0
