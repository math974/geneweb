"""Tests unitaires pour la déduplication des personnes dans GwParser."""

import io
from pathlib import Path
import pytest

from geneweb.gwu.adapters.input.gw_parser import GwParser


class TestPersonDeduplication:
    """Tests de la déduplication des personnes."""
    
    def test_child_becomes_parent_deduplicated(self):
        """Test qu'une personne enfant puis parent n'est créée qu'une fois."""
        content = """encoding: utf-8
gwplus

fam Dupont Jean + Martin Marie
beg
- h Pierre 1850
end

fam Dupont Pierre + Durand Sophie
beg
- f Jeanne 1875
end
"""
        parser = GwParser()
        db = parser.parse_stream(io.StringIO(content))
        
        # Pierre devrait apparaître une seule fois
        pierres = [p for p in db.persons.values() if p.first_name == "Pierre"]
        assert len(pierres) == 1, "Pierre devrait être unique"
        
        pierre = pierres[0]
        
        # Pierre devrait être lié à ses parents (famille 1)
        assert pierre.parents is not None, "Pierre devrait avoir des parents"
        
        # Pierre devrait être lié à son conjoint (famille 2)
        assert len(pierre.spouses) == 1, "Pierre devrait avoir un conjoint"
    
    def test_person_key_index(self):
        """Test que l'index par clé fonctionne correctement."""
        content = """encoding: utf-8
gwplus

fam Dupont Jean + Martin Marie
beg
- h Pierre 1850
end

fam Dupont Pierre + Durand Sophie
end
"""
        parser = GwParser()
        db = parser.parse_stream(io.StringIO(content))
        
        # Vérifier que l'index contient la clé (Pierre, Dupont, 0)
        key = ("Pierre", "Dupont", 0)
        assert key in db.person_key_index, "La clé devrait être dans l'index"
        
        # Vérifier que l'ID correspond à la personne
        person_id = db.person_key_index[key]
        person = db.persons[person_id]
        assert person.first_name == "Pierre"
        assert person.surname == "Dupont"
        assert person.occ == 0
    
    def test_different_occ_creates_different_persons(self):
        """Test que des occurrences différentes créent des personnes distinctes."""
        content = """encoding: utf-8
gwplus

fam Dupont Jean.0 + Martin Marie
end

fam Dupont Jean.1 + Durand Sophie
end
"""
        parser = GwParser()
        db = parser.parse_stream(io.StringIO(content))
        
        # Il devrait y avoir 2 Jean Dupont (occ 0 et occ 1)
        jeans = [p for p in db.persons.values() if p.first_name == "Jean" and p.surname == "Dupont"]
        assert len(jeans) == 2, "Il devrait y avoir 2 Jean Dupont"
        
        # Vérifier que les occurrences sont différentes
        occs = sorted([j.occ for j in jeans])
        assert occs == [0, 1], "Les occurrences devraient être 0 et 1"
    
    def test_same_name_different_surname(self):
        """Test que même prénom avec nom différent crée 2 personnes."""
        content = """encoding: utf-8
gwplus

fam Dupont Pierre + Martin Marie
end

fam Durand Pierre + Blanc Sophie
end
"""
        parser = GwParser()
        db = parser.parse_stream(io.StringIO(content))
        
        # Il devrait y avoir 2 Pierre (Dupont et Durand)
        pierres = [p for p in db.persons.values() if p.first_name == "Pierre"]
        assert len(pierres) == 2, "Il devrait y avoir 2 Pierre"
        
        surnames = sorted([p.surname for p in pierres])
        assert surnames == ["Dupont", "Durand"]
    
    def test_total_person_count_with_deduplication(self):
        """Test que le nombre total de personnes est correct avec déduplication."""
        content = """encoding: utf-8
gwplus

fam Dupont Jean + Martin Marie
beg
- h Pierre 1850
- f Anne 1852
end

fam Dupont Pierre + Durand Sophie
beg
- f Jeanne 1875
end
"""
        parser = GwParser()
        db = parser.parse_stream(io.StringIO(content))
        
        # Personnes : Jean, Marie, Pierre, Anne, Sophie, Jeanne = 6
        assert len(db.persons) == 6, f"Devrait avoir 6 personnes, trouvé {len(db.persons)}"
        
        # Vérifier les noms
        names = [(p.first_name, p.surname) for p in db.persons.values()]
        expected_names = [
            ("Jean", "Dupont"),
            ("Marie", "Martin"),
            ("Pierre", "Dupont"),
            ("Anne", "Dupont"),
            ("Sophie", "Durand"),
            ("Jeanne", "Dupont"),
        ]
        
        for expected_name in expected_names:
            assert expected_name in names, f"{expected_name} devrait être présent"
    
    def test_multiple_families_same_person(self):
        """Test qu'une personne peut être dans plusieurs familles."""
        content = """encoding: utf-8
gwplus

fam Dupont Jean + Martin Marie.0
beg
- h Pierre 1850
end

fam Dupont Jean + Martin Marie.1
beg
- f Anne 1855
end
"""
        parser = GwParser()
        db = parser.parse_stream(io.StringIO(content))
        
        # Jean devrait avoir 2 familles
        jeans = [p for p in db.persons.values() if p.first_name == "Jean" and p.surname == "Dupont"]
        assert len(jeans) == 1, "Jean devrait être unique"
        
        jean = jeans[0]
        assert len(jean.spouses) == 2, f"Jean devrait avoir 2 conjointes, a {len(jean.spouses)}"


class TestDeduplicationWithEvents:
    """Tests de la déduplication avec événements."""
    
    def test_events_merged_correctly(self):
        """Test que les événements sont correctement assignés à la personne dédupliquée."""
        content = """encoding: utf-8
gwplus

fam Dupont Jean + Martin Marie
beg
- h Pierre 1850
end

pevt Dupont Pierre
#birt 1850 #p Paris,75,France
#deat 1920 #p Lyon,69,France
end pevt

fam Dupont Pierre + Durand Sophie
end
"""
        parser = GwParser()
        db = parser.parse_stream(io.StringIO(content))
        
        # Pierre devrait être unique
        pierres = [p for p in db.persons.values() if p.first_name == "Pierre"]
        assert len(pierres) == 1
        
        pierre = pierres[0]
        
        # Pierre devrait avoir les événements
        assert pierre.has_birth(), "Pierre devrait avoir une naissance"
        assert pierre.has_death(), "Pierre devrait avoir un décès"
        
        # Pierre devrait être lié aux 2 familles
        assert pierre.parents is not None, "Pierre devrait avoir des parents"
        assert len(pierre.spouses) == 1, "Pierre devrait avoir un conjoint"


class TestGalichetDeduplication:
    """Tests de déduplication avec le fichier galichet.gw."""
    
    @pytest.fixture
    def galichet_file(self):
        """Fixture pour le fichier galichet.gw."""
        project_root = Path(__file__).parent.parent.parent.parent.parent
        galichet_path = project_root / "test" / "galichet.gw"
        
        if not galichet_path.exists():
            pytest.skip(f"Fichier galichet.gw non trouvé: {galichet_path}")
        
        return galichet_path
    
    def test_galichet_person_count(self, galichet_file):
        """Test que le nombre de personnes dans galichet.gw est correct avec déduplication."""
        parser = GwParser()
        db = parser.parse_file(galichet_file)
        
        # Afficher des statistiques
        print(f"\nGalichet avec déduplication:")
        print(f"  Personnes: {len(db.persons)}")
        print(f"  Familles: {len(db.families)}")
        print(f"  Index: {len(db.person_key_index)} clés")
        
        # Le nombre de personnes devrait être <= 47 (avant déduplication)
        # Si des personnes apparaissent comme enfant puis parent, le nombre sera < 47
        assert len(db.persons) <= 47
        
        # Le nombre de clés dans l'index devrait égaler le nombre de personnes
        assert len(db.person_key_index) == len(db.persons)
    
    def test_galichet_no_duplicate_keys(self, galichet_file):
        """Test qu'il n'y a pas de doublons dans galichet.gw."""
        parser = GwParser()
        db = parser.parse_file(galichet_file)
        
        # Vérifier que chaque personne a une clé unique
        keys_seen = set()
        for person in db.persons.values():
            key = (person.first_name, person.surname, person.occ)
            assert key not in keys_seen, f"Clé dupliquée: {key}"
            keys_seen.add(key)
        
        # Le nombre de clés devrait égaler le nombre de personnes
        assert len(keys_seen) == len(db.persons)
