"""Tests du parsing des événements dans GwParser."""

import io
import pytest

from geneweb.common.types import Sex, EventType
from geneweb.gwu.adapters.input.gw_parser import GwParser


class TestGwParserPersonEvents:
    """Tests de parsing des événements de personnes."""
    
    def test_parse_birth_event_with_date(self):
        """Test parsing événement naissance avec date."""
        parser = GwParser()
        content = """encoding: utf-8
gwplus

fam Dupont Jean + Martin Marie
beg
- h Pierre 1825
end

pevt Dupont Pierre
#birt 1825
end pevt
"""
        stream = io.StringIO(content)
        db = parser.parse_stream(stream)
        
        persons = list(parser.get_all_persons())
        pierre = next(p for p in persons if p.first_name == "Pierre")
        
        assert pierre.has_birth()
        assert pierre.birth.date is not None
        assert pierre.birth.date.year == 1825
    
    def test_parse_birth_with_full_date(self):
        """Test parsing naissance avec date complète."""
        parser = GwParser()
        content = """encoding: utf-8
gwplus

fam Dupont Jean + Martin Marie
beg
- f Marie 1827
end

pevt Dupont Marie
#birt 15/8/1827
end pevt
"""
        stream = io.StringIO(content)
        db = parser.parse_stream(stream)
        
        persons = list(parser.get_all_persons())
        marie = next(p for p in persons if p.first_name == "Marie" and p.surname == "Dupont")
        
        assert marie.has_birth()
        assert marie.birth.date.day == 15
        assert marie.birth.date.month == 8
        assert marie.birth.date.year == 1827
    
    def test_parse_birth_with_place(self):
        """Test parsing naissance avec lieu."""
        parser = GwParser()
        content = """encoding: utf-8
gwplus

fam Dupont Jean + Martin Marie
beg
- h Paul 1830
end

pevt Dupont Paul
#birt 1830 #p Paris,75,France
end pevt
"""
        stream = io.StringIO(content)
        db = parser.parse_stream(stream)
        
        persons = list(parser.get_all_persons())
        paul = next(p for p in persons if p.first_name == "Paul")
        
        assert paul.has_birth()
        assert paul.birth.place is not None
        assert "Paris" in paul.birth.place.name
    
    def test_parse_death_event(self):
        """Test parsing événement décès."""
        parser = GwParser()
        content = """encoding: utf-8
gwplus

fam Dupont Jean + Martin Marie

pevt Dupont Jean
#deat 1850 #p Lyon,69,France
end pevt
"""
        stream = io.StringIO(content)
        db = parser.parse_stream(stream)
        
        persons = list(parser.get_all_persons())
        jean = next(p for p in persons if p.first_name == "Jean")
        
        assert jean.has_death()
        assert jean.death.date.year == 1850
        assert jean.death.place is not None
        assert "Lyon" in jean.death.place.name
    
    def test_parse_death_with_precision(self):
        """Test parsing décès avec précision."""
        parser = GwParser()
        content = """encoding: utf-8
gwplus

fam Dupont Jean + Martin Marie

pevt Dupont Jean
#deat <1850
end pevt
"""
        stream = io.StringIO(content)
        db = parser.parse_stream(stream)
        
        persons = list(parser.get_all_persons())
        jean = next(p for p in persons if p.first_name == "Jean")
        
        assert jean.has_death()
        assert jean.death.date.year == 1850
        # La précision devrait être BEFORE
        from geneweb.common.types import DatePrecision
        assert jean.death.date.precision == DatePrecision.BEFORE


class TestGwParserFamilyEvents:
    """Tests de parsing des événements de familles."""
    
    def test_parse_marriage_event(self):
        """Test parsing événement mariage."""
        parser = GwParser()
        content = """encoding: utf-8
gwplus

fam Dupont Jean + Martin Marie
fevt
#marr 1820 #p Paris,75,France
end fevt
"""
        stream = io.StringIO(content)
        db = parser.parse_stream(stream)
        
        families = list(parser.get_all_families())
        family = families[0]
        
        assert family.has_marriage()
        assert family.marriage.date.year == 1820
        assert family.marriage.place is not None
        assert "Paris" in family.marriage.place.name
    
    def test_parse_marriage_without_date(self):
        """Test parsing mariage sans date."""
        parser = GwParser()
        content = """encoding: utf-8
gwplus

fam Dupont Jean + Martin Marie
fevt
#marr 
end fevt
"""
        stream = io.StringIO(content)
        db = parser.parse_stream(stream)
        
        families = list(parser.get_all_families())
        family = families[0]
        
        # Mariage devrait exister même sans date
        assert family.has_marriage()
        assert family.marriage.date is None
    
    def test_parse_divorce_event(self):
        """Test parsing événement divorce."""
        parser = GwParser()
        content = """encoding: utf-8
gwplus

fam Dupont Jean + Martin Marie
fevt
#marr 1820
#div 1825
end fevt
"""
        stream = io.StringIO(content)
        db = parser.parse_stream(stream)
        
        families = list(parser.get_all_families())
        family = families[0]
        
        assert family.has_marriage()
        assert family.has_divorce()
        assert family.divorce.date.year == 1825
        assert family.is_divorced()
        assert not family.is_married()  # Divorcé = pas marié


class TestGwParserRealEventsGalichet:
    """Tests avec les événements réels de galichet.gw."""
    
    @pytest.fixture
    def galichet_file(self):
        """Fixture pour le fichier galichet.gw."""
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent.parent.parent
        galichet_path = project_root / "test" / "galichet.gw"
        
        if not galichet_path.exists():
            pytest.skip(f"Fichier galichet.gw non trouvé: {galichet_path}")
        
        return galichet_path
    
    def test_parse_galichet_events(self, galichet_file):
        """Test parsing événements du fichier galichet.gw."""
        parser = GwParser()
        db = parser.parse_file(galichet_file)
        
        persons = list(parser.get_all_persons())
        
        # Compter les personnes avec événements
        persons_with_birth = [p for p in persons if p.has_birth()]
        persons_with_death = [p for p in persons if p.has_death()]
        
        print(f"\nÉvénements galichet.gw:")
        print(f"  Personnes avec naissance: {len(persons_with_birth)}")
        print(f"  Personnes avec décès: {len(persons_with_death)}")
        
        assert len(persons_with_birth) > 0, "Aucune naissance parsée"
        assert len(persons_with_death) > 0, "Aucun décès parsé"
        
        # Vérifier une personne spécifique (Jean Charles Galichet)
        jean_charles = next(
            (p for p in persons 
             if p.surname == "Galichet" and "Jean" in p.first_name and "Charles" in p.first_name),
            None
        )
        
        if jean_charles:
            print(f"\n  Jean Charles Galichet:")
            print(f"    Naissance: {jean_charles.birth is not None}")
            if jean_charles.birth and jean_charles.birth.date:
                print(f"    Date naissance: {jean_charles.birth.date.year}")
