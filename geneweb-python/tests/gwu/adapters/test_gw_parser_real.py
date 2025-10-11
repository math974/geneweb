"""Tests d'intégration du parser avec des fichiers réels."""

from pathlib import Path
import pytest

from geneweb.gwu.adapters.input.gw_parser import GwParser


class TestGwParserRealFile:
    """Tests avec le fichier galichet.gw réel."""
    
    @pytest.fixture
    def galichet_file(self):
        """Fixture pour le fichier galichet.gw."""
        # Le fichier galichet.gw est dans test/ à la racine du projet
        project_root = Path(__file__).parent.parent.parent.parent.parent
        galichet_path = project_root / "test" / "galichet.gw"
        
        if not galichet_path.exists():
            pytest.skip(f"Fichier galichet.gw non trouvé: {galichet_path}")
        
        return galichet_path
    
    def test_parse_galichet_file(self, galichet_file):
        """Test parsing du fichier galichet.gw complet."""
        parser = GwParser()
        db = parser.parse_file(galichet_file)
        
        # Vérifier que des données ont été parsées
        person_count = parser.get_person_count()
        family_count = parser.get_family_count()
        
        print(f"\nStatistiques galichet.gw:")
        print(f"  Personnes: {person_count}")
        print(f"  Familles: {family_count}")
        
        assert person_count > 0, "Aucune personne parsée"
        assert family_count > 0, "Aucune famille parsée"
        
        # Vérifier que les relations sont correctes
        persons = list(parser.get_all_persons())
        families = list(parser.get_all_families())
        
        # Au moins une personne devrait avoir des parents
        persons_with_parents = [p for p in persons if p.parents is not None]
        assert len(persons_with_parents) > 0, "Aucune personne n'a de parents"
        
        # Au moins une famille devrait avoir des enfants
        families_with_children = [f for f in families if f.children_count() > 0]
        assert len(families_with_children) > 0, "Aucune famille n'a d'enfants"
        
        # Vérifier qu'il y a des notes
        assert len(db.notes_map) > 0, "Aucune note parsée"
    
    def test_galichet_specific_persons(self, galichet_file):
        """Test parsing de personnes spécifiques de galichet.gw."""
        parser = GwParser()
        db = parser.parse_file(galichet_file)
        
        persons = list(parser.get_all_persons())
        
        # Chercher Jean Pierre Galichet
        galichet_jp = [
            p for p in persons 
            if p.surname == "Galichet" and "Jean" in p.first_name and "Pierre" in p.first_name
        ]
        
        if galichet_jp:
            jp = galichet_jp[0]
            print(f"\nTrouvé: {jp.format_name()}")
            assert jp.first_name == "Jean Pierre", f"Prénom incorrect: {jp.first_name}"
            
            # Devrait avoir au moins un conjoint
            assert len(jp.spouses) > 0, "Jean Pierre devrait avoir au moins un conjoint"
    
    def test_galichet_family_structure(self, galichet_file):
        """Test structure familiale de galichet.gw."""
        parser = GwParser()
        db = parser.parse_file(galichet_file)
        
        families = list(parser.get_all_families())
        persons = list(parser.get_all_persons())
        
        # Pour chaque famille, vérifier la cohérence
        for family in families:
            # Le père et la mère doivent exister
            father = next((p for p in persons if p.person_id == family.father_id), None)
            mother = next((p for p in persons if p.person_id == family.mother_id), None)
            
            assert father is not None, f"Père non trouvé pour famille {family.family_id}"
            assert mother is not None, f"Mère non trouvée pour famille {family.family_id}"
            
            # Les enfants doivent exister
            for child_id in family.children:
                child = next((p for p in persons if p.person_id == child_id), None)
                assert child is not None, f"Enfant {child_id} non trouvé"
                assert child.parents == family.family_id, "Lien parent-enfant incohérent"
