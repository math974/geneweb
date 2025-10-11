"""Tests unitaires pour GwFileRepository."""

import io
from pathlib import Path
import pytest

from geneweb.gwu.adapters.input.gw_file_repository import (
    GwFileRepository,
    GwFilePersonRepository,
    GwFileFamilyRepository,
)


class TestGwFilePersonRepository:
    """Tests du PersonRepository pour fichiers .gw."""
    
    @pytest.fixture
    def simple_gw_file(self, tmp_path):
        """Crée un fichier .gw temporaire simple."""
        content = """encoding: utf-8
gwplus

fam Dupont Jean + Martin Marie
beg
- h Pierre 1825
- f Anne 1827
end

pevt Dupont Pierre
#birt 1825 #p Paris,75,France
#deat 1900
end pevt
"""
        file_path = tmp_path / "test.gw"
        file_path.write_text(content)
        return file_path
    
    def test_get_all_persons(self, simple_gw_file):
        """Test récupération de toutes les personnes."""
        repo = GwFilePersonRepository(simple_gw_file)
        
        persons = list(repo.get_all())
        assert len(persons) == 4  # Jean, Marie, Pierre, Anne
    
    def test_get_count(self, simple_gw_file):
        """Test comptage des personnes."""
        repo = GwFilePersonRepository(simple_gw_file)
        assert repo.get_count() == 4
    
    def test_get_by_id(self, simple_gw_file):
        """Test récupération par ID."""
        repo = GwFilePersonRepository(simple_gw_file)
        
        # Récupérer toutes les personnes
        persons = list(repo.get_all())
        first_person = persons[0]
        
        # Récupérer par ID
        found = repo.get_by_id(first_person.person_id)
        assert found is not None
        assert found.person_id == first_person.person_id
    
    def test_get_by_key(self, simple_gw_file):
        """Test récupération par clé (nom.occ)."""
        repo = GwFilePersonRepository(simple_gw_file)
        
        # Chercher Pierre Dupont.0
        pierre = repo.get_by_key("Pierre", "Dupont", 0)
        assert pierre is not None
        assert pierre.first_name == "Pierre"
        assert pierre.surname == "Dupont"
        assert pierre.occ == 0
    
    def test_get_by_key_not_found(self, simple_gw_file):
        """Test récupération par clé non existante."""
        repo = GwFilePersonRepository(simple_gw_file)
        
        person = repo.get_by_key("Inconnu", "Dupont", 0)
        assert person is None
    
    def test_search_by_name(self, simple_gw_file):
        """Test recherche par nom."""
        repo = GwFilePersonRepository(simple_gw_file)
        
        # Chercher "Dupont"
        results = repo.search_by_name("Dupont")
        assert len(results) >= 2  # Pierre et Anne au minimum
        
        # Chercher "Pierre"
        results = repo.search_by_name("Pierre")
        assert len(results) >= 1
    
    def test_get_isolated_persons(self, simple_gw_file):
        """Test récupération des personnes isolées."""
        repo = GwFilePersonRepository(simple_gw_file)
        
        isolated = list(repo.get_isolated_persons())
        # Aucune personne isolée dans ce fichier (tous ont parents ou conjoints)
        assert len(isolated) == 0
    
    def test_save_not_implemented(self, simple_gw_file):
        """Test que save() lève NotImplementedError."""
        repo = GwFilePersonRepository(simple_gw_file)
        persons = list(repo.get_all())
        
        with pytest.raises(NotImplementedError):
            repo.save(persons[0])


class TestGwFileFamilyRepository:
    """Tests du FamilyRepository pour fichiers .gw."""
    
    @pytest.fixture
    def simple_gw_file(self, tmp_path):
        """Crée un fichier .gw temporaire simple."""
        content = """encoding: utf-8
gwplus

fam Dupont Jean + Martin Marie
fevt
#marr 1820 #p Paris,75,France
end fevt
beg
- h Pierre 1825
end

fam Dupont Pierre + Durand Sophie
beg
- f Jeanne 1850
end
"""
        file_path = tmp_path / "test.gw"
        file_path.write_text(content)
        return file_path
    
    def test_get_all_families(self, simple_gw_file):
        """Test récupération de toutes les familles."""
        repo = GwFileFamilyRepository(simple_gw_file)
        
        families = list(repo.get_all())
        assert len(families) == 2
    
    def test_get_count(self, simple_gw_file):
        """Test comptage des familles."""
        repo = GwFileFamilyRepository(simple_gw_file)
        assert repo.get_count() == 2
    
    def test_get_by_id(self, simple_gw_file):
        """Test récupération famille par ID."""
        repo = GwFileFamilyRepository(simple_gw_file)
        
        families = list(repo.get_all())
        first_family = families[0]
        
        found = repo.get_by_id(first_family.family_id)
        assert found is not None
        assert found.family_id == first_family.family_id
    
    def test_get_families_of_person(self, simple_gw_file):
        """Test récupération familles d'une personne."""
        repo = GwFileFamilyRepository(simple_gw_file)
        families = list(repo.get_all())
        
        # Pierre devrait être dans 2 familles (enfant puis père)
        # Note: Actuellement avec duplication, ce sont 2 personnes différentes
        family1 = families[0]
        father_families = repo.get_families_of_person(family1.father_id)
        assert len(father_families) >= 1
    
    def test_save_not_implemented(self, simple_gw_file):
        """Test que save() lève NotImplementedError."""
        repo = GwFileFamilyRepository(simple_gw_file)
        families = list(repo.get_all())
        
        with pytest.raises(NotImplementedError):
            repo.save(families[0])


class TestGwFileRepository:
    """Tests du repository combiné."""
    
    @pytest.fixture
    def simple_gw_file(self, tmp_path):
        """Crée un fichier .gw temporaire simple."""
        content = """encoding: utf-8
gwplus

fam Dupont Jean + Martin Marie
fevt
#marr 1820
end fevt
beg
- h Pierre 1825
- f Anne 1827
end

pevt Dupont Pierre
#birt 1825
end pevt
"""
        file_path = tmp_path / "test.gw"
        file_path.write_text(content)
        return file_path
    
    def test_combined_repository(self, simple_gw_file):
        """Test repository combiné."""
        repo = GwFileRepository(simple_gw_file)
        
        # Accès personnes
        assert repo.persons.get_count() == 4
        
        # Accès familles
        assert repo.families.get_count() == 1
    
    def test_shared_database(self, simple_gw_file):
        """Test que les repositories partagent la même database."""
        repo = GwFileRepository(simple_gw_file)
        
        # Les deux repositories devraient partager la même database
        assert repo.persons.database is repo.families.database
    
    @pytest.fixture
    def galichet_file(self):
        """Fixture pour le fichier galichet.gw."""
        project_root = Path(__file__).parent.parent.parent.parent.parent
        galichet_path = project_root / "test" / "galichet.gw"
        
        if not galichet_path.exists():
            pytest.skip(f"Fichier galichet.gw non trouvé: {galichet_path}")
        
        return galichet_path
    
    def test_galichet_repository(self, galichet_file):
        """Test avec le fichier galichet.gw réel."""
        repo = GwFileRepository(galichet_file)
        
        # Statistiques
        person_count = repo.persons.get_count()
        family_count = repo.families.get_count()
        
        print(f"\nGalichet via Repository:")
        print(f"  Personnes: {person_count}")
        print(f"  Familles: {family_count}")
        
        # Avec déduplication, 35 personnes uniques (au lieu de 47 avec doublons)
        assert person_count == 35
        assert family_count == 15
        
        # Recherche par nom
        galichets = repo.persons.search_by_name("Galichet")
        print(f"  Personnes 'Galichet': {len(galichets)}")
        assert len(galichets) > 0
        
        # Récupération par clé
        jean_pierre = repo.persons.get_by_key("Jean Pierre", "Galichet", 0)
        assert jean_pierre is not None
        print(f"  Trouvé: {jean_pierre.format_name()}")
        
        # Vérifier qu'il a des événements
        assert jean_pierre.has_death()
        
        # Personnes isolées
        isolated = list(repo.persons.get_isolated_persons())
        print(f"  Personnes isolées: {len(isolated)}")
