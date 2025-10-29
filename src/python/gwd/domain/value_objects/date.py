"""Value Object Date - 20 lignes max par fonction"""
from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass(frozen=True)
class DateRange:
    """Value object pour une plage de dates - 20 lignes max"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    @property
    def is_valid(self) -> bool:
        """Vérifie si la plage est valide - MAX 20 LIGNES"""
        if not self.start_date or not self.end_date:
            return True
        return self.start_date <= self.end_date
    
    @property
    def duration_days(self) -> Optional[int]:
        """Durée en jours - MAX 20 LIGNES"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return None
    
    def contains(self, check_date: date) -> bool:
        """Vérifie si une date est dans la plage - MAX 20 LIGNES"""
        if not self.start_date and not self.end_date:
            return False
        if self.start_date and check_date < self.start_date:
            return False
        if self.end_date and check_date > self.end_date:
            return False
        return True

