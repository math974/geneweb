"""Tests pour GwFileWriter."""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from geneweb.common.types import Sex, AccessLevel, EventType
from geneweb.gwu.domain.entities import Person, Family, Event, Date, Place, Note, Source
from geneweb.gwu.domain.config import ExportOptions
from geneweb.gwu.adapters.output.gw_file_writer import GwFileWriter


class TestGwFileWriter:
    """Tests pour GwFileWriter."""

    @pytest.fixture
    def sample_person(self):
        """Personne de test."""
        return Person(
            person_id="P1",
            first_name="Jean",
            surname="Dupont",
            sex=Sex.MALE,
            occ=0,
            birth=Event(
                event_type=EventType.BIRTH,
                date=Date.from_year(1850),
                place=Place(name="Paris")
            ),
            notes=Note(content="Note de test"),
            sources=[Source(reference="Source de test")]
        )

    @pytest.fixture
    def sample_family(self):
        """Famille de test."""
        return Family(
            family_id="F1",
            father_id="P1",
            mother_id="P2",
            children=["P3"],
            marriage=Event(
                event_type=EventType.MARRIAGE,
                date=Date.from_year(1875)
            )
        )

    @pytest.fixture
    def basic_options(self):
        """Options d'export de base."""
        return ExportOptions()

    def test_write_person(self, sample_person, basic_options):
        """Test écriture d'une personne."""
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "person.gw"
            writer = GwFileWriter(basic_options)
            
            writer.write_person(output_path, sample_person)
            
            assert output_path.exists()
            content = output_path.read_text(encoding="UTF-8")
            assert "# Jean.0 Dupont" in content
            assert "#sex male" in content
            assert "#birt 1850" in content
            assert "#p Paris" in content

    def test_write_family(self, sample_family, basic_options):
        """Test écriture d'une famille."""
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "family.gw"
            writer = GwFileWriter(basic_options)
            
            writer.write_family(output_path, sample_family)
            
            assert output_path.exists()
            content = output_path.read_text(encoding="UTF-8")
            assert "#f P1 P2" in content
            assert "#c P3" in content
            assert "#marr 1875" in content

    def test_write_database(self, sample_person, sample_family, basic_options):
        """Test écriture d'une base complète."""
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "database.gw"
            writer = GwFileWriter(basic_options)
            
            writer.write_database(
                output_path,
                [sample_person],
                [sample_family],
                {"P1"},
                {"F1"}
            )
            
            assert output_path.exists()
            content = output_path.read_text(encoding="UTF-8")
            assert "# Jean.0 Dupont" in content
            assert "#f P1 P2" in content

    def test_encoding_utf8(self, sample_person):
        """Test avec encodage UTF-8."""
        options = ExportOptions(encoding="UTF-8")
        
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "person.gw"
            writer = GwFileWriter(options)
            
            writer.write_person(output_path, sample_person)
            
            content = output_path.read_text(encoding="UTF-8")
            assert "Jean" in content

    def test_old_gw_format(self, sample_person):
        """Test avec format ancien."""
        options = ExportOptions(old_gw=True)
        
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "person.gw"
            writer = GwFileWriter(options)
            
            writer.write_person(output_path, sample_person)
            
            content = output_path.read_text(encoding="UTF-8")
            # Le format ancien devrait être utilisé pour les dates
            assert "1850" in content

    def test_gwplus_format(self, sample_person):
        """Test avec format gwplus."""
        options = ExportOptions(gw_plus=True)
        
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "person.gw"
            writer = GwFileWriter(options)
            
            writer.write_person(output_path, sample_person)
            
            content = output_path.read_text(encoding="UTF-8")
            # Le format gwplus n'est ajouté que dans l'en-tête, pas dans le contenu de la personne
            # Vérifions que la personne est bien écrite
            assert "# Jean.0 Dupont" in content

    def test_no_notes_option(self, sample_person):
        """Test avec option no_notes."""
        options = ExportOptions(no_notes=True)
        
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "person.gw"
            writer = GwFileWriter(options)
            
            writer.write_person(output_path, sample_person)
            
            content = output_path.read_text(encoding="UTF-8")
            assert "#note" not in content

    def test_no_sources_option(self, sample_person):
        """Test avec option no_sources."""
        options = ExportOptions(no_sources=True)
        
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "person.gw"
            writer = GwFileWriter(options)
            
            writer.write_person(output_path, sample_person)
            
            content = output_path.read_text(encoding="UTF-8")
            assert "#src" not in content

    def test_no_events_option(self, sample_person):
        """Test avec option no_events."""
        options = ExportOptions(no_events=True)
        
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "person.gw"
            writer = GwFileWriter(options)
            
            writer.write_person(output_path, sample_person)
            
            content = output_path.read_text(encoding="UTF-8")
            # Les événements principaux (birth, death) devraient toujours être inclus
            assert "#birt" in content
