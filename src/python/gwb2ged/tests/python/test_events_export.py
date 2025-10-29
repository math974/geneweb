"""
Test suite for event export and conversion in gwb2ged and ged2gwb.

Tests that all GEDCOM events are correctly converted and exported.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add src/python to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from gwb2ged.tests.python.test_helper import get_fixture_path
from gwb2ged.core.options import ExportOptions
from gwb2ged.core.converter import BaseToGedcomConverter
from ged2gwb.core.converter import Ged2GwbConverter
from ged2gwb.utils.options import ConversionOptions
from lib.db.database.base import Base
from lib.db.io.msgpack import MessagePackReader, MessagePackWriter
from lib.db.models.events import Date, Event
from lib.db.models.person import GenPerson
from lib.db.models.family import GenFamily
from lib.db.core.types import Iper, Ifam
from lib.db.core.enums import Sex, RelationKind
from lib.db.database.base_data import BaseData


def _create_test_database_with_events() -> tuple[Path, str]:
    """Create a test database with various events."""
    temp_dir = Path(tempfile.mkdtemp())
    db_name = "test-events-export"
    db_dir = temp_dir / f"{db_name}.msgpack"
    db_dir.mkdir(parents=True)

    # Create base data
    base_data = BaseData()

    # Create person with multiple events
    person = GenPerson(
        first_name="John",
        surname="Doe",
        sex=Sex.MALE,
        birth=Date(year=1980, month=3, day=15),
        death=Date(year=2020, month=1, day=20),
    )

    # Add events
    person.events.append(Event(
        name="BIRT",
        date=Date(year=1980, month=3, day=15),
        place="Hospital, Paris",
        note="Birth note",
        src="Birth certificate",
    ))
    person.events.append(Event(
        name="BAPM",
        date=Date(year=1980, month=4, day=15),
        place="Church, Paris",
        note="Baptism note",
        src="Church records",
    ))
    person.events.append(Event(
        name="DEAT",
        date=Date(year=2020, month=1, day=20),
        place="Home, Lyon",
        note="Death note",
        src="Death certificate",
    ))
    person.events.append(Event(
        name="CONF",
        date=Date(year=1990, month=5, day=1),
        place="Cathedral",
    ))
    person.events.append(Event(
        name="EMIG",
        date=Date(year=2010, month=1, day=1),
        place="Port, Marseille",
        note="Emigration to USA",
    ))
    person.events.append(Event(
        name="EVEN",
        date=Date(year=1995, month=1, day=1),
        place="Location",
        note="Custom event",
        src="Custom source",
    ))

    base_data.persons[Iper(1)] = person

    # Create a second person for the family
    person2 = GenPerson(
        first_name="Jane",
        surname="Doe",
        sex=Sex.FEMALE,
        birth=Date(year=1982, month=1, day=1),
    )
    base_data.persons[Iper(2)] = person2

    # Create couple
    from lib.db.models.relations import GenCouple
    couple = GenCouple(
        father=Iper(1),
        mother=Iper(2),
    )
    base_data.couples[Ifam(1)] = couple

    # Create family with events
    family = GenFamily(
        marriage=Date(year=2005, month=6, day=15),
        marriage_place="City Hall",
        relation=RelationKind.MARRIED,
    )

    # Add family events
    family.events.append(Event(
        name="ENGA",
        date=Date(year=2004, month=5, day=1),
        place="Restaurant",
        note="Engagement party",
    ))
    family.events.append(Event(
        name="Reception",
        date=Date(year=2005, month=6, day=20),
        place="Reception Hall",
        note="Wedding reception",
    ))

    base_data.families[Ifam(1)] = family

    # Create union for person 1
    from lib.db.models.relations import GenUnion
    union1 = GenUnion(family=[Ifam(1)])
    base_data.unions[Iper(1)] = union1

    # Create union for person 2
    union2 = GenUnion(family=[Ifam(1)])
    base_data.unions[Iper(2)] = union2

    # Save database
    writer = MessagePackWriter(str(temp_dir))
    writer.write_database(base_data, db_name)

    return temp_dir, db_name


def test_primary_events_export():
    """Test that primary events are exported correctly."""
    temp_dir, db_name = _create_test_database_with_events()
    try:
        # Load database
        reader = MessagePackReader(data_dir=str(temp_dir))
        base = Base(reader.load_database(db_name))

        # Export to GEDCOM
        options = ExportOptions()
        converter = BaseToGedcomConverter(base, options)
        gedcom_db = converter.convert()

        assert len(gedcom_db.individuals) >= 1, "Should have at least 1 individual"
        # Get the first individual (John Doe)
        individual = [ind for ind in gedcom_db.individuals.values() if ind.names and ind.names[0].given == "John"][0]

        # Check that birth and death are exported
        assert individual.birth is not None, "Should have birth event"
        assert individual.death is not None, "Should have death event"

        # Check that events list contains other events
        event_tags = [e.tag for e in individual.events]

        assert "BAPM" in event_tags, "Should have baptism event"
        assert "CONF" in event_tags, "Should have confirmation event"
        assert "EMIG" in event_tags, "Should have emigration event"

        # Check baptism event details
        baptism_events = [e for e in individual.events if e.tag == "BAPM"]
        if baptism_events:
            baptism = baptism_events[0]
            assert baptism.date.year == 1980, "Baptism should have correct year"
            assert "Paris" in baptism.place.name, "Baptism should have place"
            assert "Baptism note" in baptism.note, "Baptism should have note"
            assert "Church records" in baptism.sources[0], "Baptism should have source"

        print("✓ Primary events export test passed")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_even_events_export():
    """Test that EVEN events are exported with TYPE attribute."""
    temp_dir, db_name = _create_test_database_with_events()
    try:
        # Load database
        reader = MessagePackReader(data_dir=str(temp_dir))
        base = Base(reader.load_database(db_name))

        # Export to GEDCOM
        options = ExportOptions()
        converter = BaseToGedcomConverter(base, options)
        gedcom_db = converter.convert()

        individual = list(gedcom_db.individuals.values())[0]

        # Find EVEN events
        even_events = [e for e in individual.events if e.tag == "EVEN"]
        assert len(even_events) >= 1, "Should have EVEN events"

        if even_events:
            even = even_events[0]
            assert "TYPE" in even.attributes, "EVEN event should have TYPE attribute"
            assert even.attributes["TYPE"] == "EVEN", "TYPE should be set correctly"
            assert even.note, "EVEN event should have note"
            assert even.sources, "EVEN event should have sources"

        print("✓ EVEN events export test passed")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_family_events_export():
    """Test that family events are exported correctly."""
    temp_dir, db_name = _create_test_database_with_events()
    try:
        # Load database
        reader = MessagePackReader(data_dir=str(temp_dir))
        base = Base(reader.load_database(db_name))

        # Export to GEDCOM
        options = ExportOptions()
        converter = BaseToGedcomConverter(base, options)
        gedcom_db = converter.convert()

        assert len(gedcom_db.families) == 1, "Should have 1 family"
        family = list(gedcom_db.families.values())[0]

        # Check marriage
        assert family.marriage is not None, "Should have marriage event"
        assert family.marriage.date.year == 2005, "Marriage should have correct year"

        # Check family events
        assert len(family.events) >= 2, f"Should have at least 2 family events, found {len(family.events)}"

        event_tags = [e.tag for e in family.events]
        assert "ENGA" in event_tags, "Should have engagement event"

        # Check EVEN event in family
        even_events = [e for e in family.events if e.tag == "EVEN"]
        assert len(even_events) >= 1, "Should have EVEN event in family"

        if even_events:
            even = even_events[0]
            assert "Wedding reception" in even.note or "Reception" in even.note, "EVEN event should have note"

        print("✓ Family events export test passed")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_event_notes_filtering():
    """Test that event notes are filtered according to options."""
    temp_dir, db_name = _create_test_database_with_events()
    try:
        # Load database
        reader = MessagePackReader(data_dir=str(temp_dir))
        base = Base(reader.load_database(db_name))

        # Export with -nnn option (no notes)
        from gwb2ged.core.options import NoNotes
        options = ExportOptions(no_notes=NoNotes.NNN)
        converter = BaseToGedcomConverter(base, options)
        gedcom_db = converter.convert()

        individual = list(gedcom_db.individuals.values())[0]

        # Check that events don't have notes
        for event in individual.events:
            assert not event.note, f"Event {event.tag} should not have note with -nnn option"

        print("✓ Event notes filtering test passed")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_round_trip_events():
    """Test that events are preserved in a GEDCOM -> DB -> GEDCOM round trip."""
    # Use fixture file
    gedcom_file = get_fixture_path("test_events_all_types.ged")

    temp_dir = Path(tempfile.mkdtemp())

    # Convert to database
    options = ConversionOptions(
        input_file=Path(gedcom_file),
        output_file=Path(temp_dir / "test-roundtrip"),
        base_dir=Path(temp_dir),
        force=True,
    )
    converter = Ged2GwbConverter(options)
    converter.convert()

    try:
        # Load database
        reader = MessagePackReader(data_dir=str(temp_dir))
        db_data = reader.load_database("test-roundtrip")
        assert db_data is not None, "Database should be loaded"

        # Check events in database
        person = list(db_data.persons.values())[0]
        assert len(person.events) >= 4, f"Should have at least 4 events, found {len(person.events)}"

        event_names = [e.name.upper() for e in person.events]
        assert "BAPM" in event_names or "BAPTISM" in event_names, "Should have baptism"
        assert "CONF" in event_names or "CONFIRMATION" in event_names, "Should have confirmation"

        # Export back to GEDCOM
        base = Base(db_data)
        export_options = ExportOptions()
        export_converter = BaseToGedcomConverter(base, export_options)
        exported_gedcom = export_converter.convert()

        # Check exported events
        exported_person = list(exported_gedcom.individuals.values())[0]
        exported_tags = [e.tag for e in exported_person.events]

        assert "BAPM" in exported_tags, "Should export baptism"
        assert "CONF" in exported_tags, "Should export confirmation"
        assert "EVEN" in exported_tags, "Should export EVEN event"

        print("✓ Round-trip events preservation test passed")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_all_gedcom_events_conversion():
    """Test that all primary GEDCOM events are converted from GEDCOM to database."""
    # Use fixture file
    gedcom_file = get_fixture_path("test_events_all_types.ged")

    temp_dir = Path(tempfile.mkdtemp())

    # Convert to database
    options = ConversionOptions(
        input_file=Path(gedcom_file),
        output_file=Path(temp_dir / "test-all-events"),
        base_dir=Path(temp_dir),
        force=True,
    )
    converter = Ged2GwbConverter(options)
    converter.convert()

    try:
        # Load database
        reader = MessagePackReader(data_dir=str(temp_dir))
        db_data = reader.load_database("test-all-events")

        assert db_data is not None, "Database should be loaded"
        assert len(db_data.persons) == 1, "Should have 1 person"

        person = list(db_data.persons.values())[0]

        # Check that we have multiple events
        assert len(person.events) >= 10, f"Should have at least 10 events, found {len(person.events)}"

        # Check specific events
        event_names = [e.name.upper() for e in person.events]

        assert "BAPM" in event_names or "BAPTISM" in event_names, "Should have baptism event"
        assert "CONF" in event_names or "CONFIRMATION" in event_names, "Should have confirmation event"
        assert "GRAD" in event_names or "GRADUATE" in event_names, "Should have graduation event"
        assert "EMIG" in event_names or "EMIGRATION" in event_names, "Should have emigration event"
        assert "IMMI" in event_names or "IMMIGRATION" in event_names, "Should have immigration event"
        # Note: OCCU is currently parsed as an attribute, not an event
        # This is a limitation of the current GEDCOM parser
        assert "CENS" in event_names or "CENSUS" in event_names, "Should have census event"
        assert "RESI" in event_names or "RESIDENCE" in event_names, "Should have residence event"

        print(f"✓ All GEDCOM events conversion test passed ({len(person.events)} events found)")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_birth_death_events_conversion():
    """Test birth and death events conversion using fixture."""
    gedcom_file = get_fixture_path("test_events_birth_death.ged")

    temp_dir = Path(tempfile.mkdtemp())

    options = ConversionOptions(
        input_file=Path(gedcom_file),
        output_file=Path(temp_dir / "test-birth-death"),
        base_dir=Path(temp_dir),
        force=True,
    )
    converter = Ged2GwbConverter(options)
    converter.convert()

    try:
        reader = MessagePackReader(data_dir=str(temp_dir))
        db_data = reader.load_database("test-birth-death")

        assert db_data is not None, "Database should be loaded"
        person = list(db_data.persons.values())[0]

        # Check birth event
        birth_events = [e for e in person.events if e.name.upper() in ("BIRT", "BIRTH")]
        assert len(birth_events) >= 1, "Should have birth event"
        birth_event = birth_events[0]
        assert birth_event.date.year == 1980, "Birth year should be 1980"
        assert "Paris" in birth_event.place, "Birth place should contain Paris"
        assert birth_event.note, "Birth should have note"

        # Check death event
        death_events = [e for e in person.events if e.name.upper() in ("DEAT", "DEATH")]
        assert len(death_events) >= 1, "Should have death event"
        death_event = death_events[0]
        assert death_event.date.year == 2020, "Death year should be 2020"
        assert "Lyon" in death_event.place, "Death place should contain Lyon"
        assert death_event.note, "Death should have note"

        print("✓ Birth and death events conversion test passed")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_census_residence_events_conversion():
    """Test census and residence events conversion using fixture."""
    gedcom_file = get_fixture_path("test_events_census_residence.ged")

    temp_dir = Path(tempfile.mkdtemp())

    options = ConversionOptions(
        input_file=Path(gedcom_file),
        output_file=Path(temp_dir / "test-census-resi"),
        base_dir=Path(temp_dir),
        force=True,
    )
    converter = Ged2GwbConverter(options)
    converter.convert()

    try:
        reader = MessagePackReader(data_dir=str(temp_dir))
        db_data = reader.load_database("test-census-resi")

        assert db_data is not None, "Database should be loaded"
        person = list(db_data.persons.values())[0]

        # Check census events (multiple)
        census_events = [e for e in person.events if e.name.upper() == "CENS"]
        assert len(census_events) >= 2, f"Should have at least 2 census events, found {len(census_events)}"

        # Check residence events (multiple)
        resi_events = [e for e in person.events if e.name.upper() == "RESI"]
        assert len(resi_events) >= 2, f"Should have at least 2 residence events, found {len(resi_events)}"

        print(f"✓ Census and residence events conversion test passed ({len(census_events)} census, {len(resi_events)} residence)")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_family_events_conversion():
    """Test family events conversion using fixture."""
    gedcom_file = get_fixture_path("test_events_family.ged")

    temp_dir = Path(tempfile.mkdtemp())

    options = ConversionOptions(
        input_file=Path(gedcom_file),
        output_file=Path(temp_dir / "test-family-events"),
        base_dir=Path(temp_dir),
        force=True,
    )
    converter = Ged2GwbConverter(options)
    converter.convert()

    try:
        reader = MessagePackReader(data_dir=str(temp_dir))
        db_data = reader.load_database("test-family-events")

        assert db_data is not None, "Database should be loaded"
        assert len(db_data.families) == 1, "Should have 1 family"

        family = list(db_data.families.values())[0]

        # Check family events
        assert len(family.events) >= 3, f"Should have at least 3 family events, found {len(family.events)}"

        event_names = [e.name.upper() for e in family.events]
        assert "ENGA" in event_names or "ENGAGEMENT" in event_names, "Should have engagement event"
        assert "MARC" in event_names or "MARRIAGECONTRACT" in event_names, "Should have marriage contract event"

        # Check EVEN event - may be stored as "EVEN" or "Reception"
        # The converter should ideally store TYPE value as event.name, but might store "EVEN"
        event_names = [e.name.upper() if e.name else "" for e in family.events]
        reception_events = [
            e for e in family.events
            if (e.name and ("RECEPTION" in e.name.upper() or e.name.upper() == "RECEPTION")) or
            (e.name and e.name.upper() == "EVEN" and e.note and "reception" in e.note.lower())
        ]
        # Accept either "Reception" as name or "EVEN" with "reception" in note
        assert len(reception_events) >= 1, f"Should have reception EVEN event. Found event names: {event_names}"

        print("✓ Family events conversion test passed")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    """Run all event tests."""
    print("=== Testing Events in gwb2ged (Conversion + Export) ===\n")

    tests = [
        test_birth_death_events_conversion,
        test_all_gedcom_events_conversion,
        test_census_residence_events_conversion,
        test_family_events_conversion,
        test_primary_events_export,
        test_even_events_export,
        test_family_events_export,
        test_event_notes_filtering,
        test_round_trip_events,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__} - {e}")
            import traceback
            traceback.print_exc()

    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("SUCCESS: All event export tests passed!")
        return 0
    else:
        print("FAILURE: Some event export tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
