"""
Conversion module for GEDCOM to GeneWeb.

This module contains all conversion functions from GEDCOM to GeneWeb data structures.
"""

from typing import List, Tuple
from lib.db.core.enums import DivorceStatus, RelationKind, Sex
from lib.db.core.types import Iper, dummy_iper
from lib.db.models.events import Date, Event
from lib.db.models.family import GenFamily
from lib.db.models.person import GenPerson
from lib.db.models.relations import GenCouple


class GedcomConverter:
    """Converter for GEDCOM data structures to GeneWeb format."""

    def __init__(self, logger, options=None):
        """Initialize converter with logger and options."""
        self.logger = logger
        self.options = options

    def convert_individual(self, individual) -> GenPerson:
        """Convert GEDCOM individual to GenPerson."""
        try:
            first_name = ""
            surname = ""
            if individual.names:
                primary_name = individual.names[0]
                first_name = primary_name.given or ""
                surname = primary_name.surname or ""

                # Apply name processing options
                first_name = self._process_first_name(first_name)
                surname = self._process_surname(surname)

            sex = Sex.NEUTER
            if individual.sex == "M":
                sex = Sex.MALE
            elif individual.sex == "F":
                sex = Sex.FEMALE

            birth_date = None
            birth_place = None
            if individual.birth:
                if individual.birth.date:
                    birth_date = self.convert_date(individual.birth.date)
                if individual.birth.place:
                    # Extract place name from GedcomPlace
                    birth_place = (
                        individual.birth.place.name
                        if hasattr(individual.birth.place, "name")
                        else str(individual.birth.place)
                    )

            baptism_date = None
            if individual.baptism and individual.baptism.date:
                baptism_date = self.convert_date(individual.baptism.date)

            death_date = None
            death_place = None
            if individual.death:
                if individual.death.date:
                    death_date = self.convert_date(individual.death.date)
                if individual.death.place:
                    # Extract place name from GedcomPlace
                    death_place = (
                        individual.death.place.name
                        if hasattr(individual.death.place, "name")
                        else str(individual.death.place)
                    )

            burial_date = None
            if individual.burial and individual.burial.date:
                burial_date = self.convert_date(individual.burial.date)

            # Convert notes and sources
            notes_text = ""
            if hasattr(individual, "notes") and individual.notes:
                notes_text = "\n".join(individual.notes)
                self.logger.info(
                    f"Converted notes for {first_name} {surname}: {notes_text}"
                )

            sources_text = ""
            if hasattr(individual, "sources") and individual.sources:
                sources_text = "\n".join(individual.sources)
                self.logger.info(
                    f"Converted sources for {first_name} {surname}: {sources_text}"
                )
            elif (
                hasattr(individual, "source_citations") and individual.source_citations
            ):
                # Convert source citations to text
                source_citations = []
                for citation in individual.source_citations:
                    if hasattr(citation, "source") and citation.source:
                        source_citations.append(citation.source)
                sources_text = "\n".join(source_citations)
                self.logger.info(
                    f"Converted source citations for {first_name} {surname}: {sources_text}"
                )

            person = GenPerson(
                first_name=first_name,
                surname=surname,
                sex=sex,
                birth=birth_date,
                baptism=baptism_date,
                death=death_date,
                burial=burial_date,
                notes=notes_text,
                sources=sources_text,
            )

            if birth_place or individual.birth:
                birth_note = ""
                birth_src = ""
                if individual.birth:
                    if getattr(individual.birth, "note", None):
                        birth_note = individual.birth.note or ""
                    if getattr(individual.birth, "sources", None):
                        try:
                            birth_src = ", ".join(individual.birth.sources)
                        except Exception:
                            birth_src = ""
                birth_event = Event(
                    name="BIRT",
                    date=birth_date,
                    place=birth_place or "",
                    note=birth_note,
                    src=birth_src,
                )
                person.events.append(birth_event)

            if death_place or individual.death:
                death_note = ""
                death_src = ""
                if individual.death:
                    if getattr(individual.death, "note", None):
                        death_note = individual.death.note or ""
                    if getattr(individual.death, "sources", None):
                        try:
                            death_src = ", ".join(individual.death.sources)
                        except Exception:
                            death_src = ""
                death_event = Event(
                    name="DEAT",
                    date=death_date,
                    place=death_place or "",
                    note=death_note,
                    src=death_src,
                )
                person.events.append(death_event)

            # Convert all other events from individual.events
            if hasattr(individual, "events") and individual.events:
                for gedcom_event in individual.events:
                    if not gedcom_event:
                        continue

                    # Get event name from tag or TYPE attribute
                    event_name = gedcom_event.tag
                    if event_name == "EVEN" and gedcom_event.attributes.get("TYPE"):
                        event_name = gedcom_event.attributes["TYPE"]
                    # Skip birth and death (already handled above)
                    if event_name in {"BIRT", "DEAT", "birth", "death"}:
                        continue

                    # Convert event date
                    event_date = None
                    if gedcom_event.date:
                        event_date = self.convert_date(gedcom_event.date)

                    # Convert event place
                    event_place = ""
                    if gedcom_event.place:
                        event_place = (
                            gedcom_event.place.name
                            if hasattr(gedcom_event.place, "name")
                            else str(gedcom_event.place)
                        )

                    # Convert event note
                    event_note = ""
                    if gedcom_event.note:
                        event_note = gedcom_event.note

                    # Convert event source
                    event_src = ""
                    if gedcom_event.sources:
                        event_src = ", ".join(gedcom_event.sources)

                    # Create Event object
                    event = Event(
                        name=event_name,
                        date=event_date,
                        place=event_place,
                        note=event_note,
                        src=event_src,
                    )
                    person.events.append(event)

            if individual.baptism:
                baptism_place = ""
                if individual.baptism.place:
                    baptism_place = (
                        individual.baptism.place.name
                        if hasattr(individual.baptism.place, "name")
                        else str(individual.baptism.place)
                    )
                baptism_event = Event(
                    name="BAPM",
                    date=baptism_date,
                    place=baptism_place,
                    note=individual.baptism.note if individual.baptism.note else "",
                    src=", ".join(individual.baptism.sources)
                    if individual.baptism.sources
                    else "",
                )
                person.events.append(baptism_event)

            # Burial
            if individual.burial:
                burial_place = ""
                if individual.burial.place:
                    burial_place = (
                        individual.burial.place.name
                        if hasattr(individual.burial.place, "name")
                        else str(individual.burial.place)
                    )
                burial_event = Event(
                    name="BURI",
                    date=burial_date,
                    place=burial_place,
                    note=individual.burial.note if individual.burial.note else "",
                    src=", ".join(individual.burial.sources)
                    if individual.burial.sources
                    else "",
                )
                person.events.append(burial_event)

            # Other dedicated event fields
            for event_attr in [
                "confirmation",
                "adult_christening",
                "bar_mitzvah",
                "bas_mitzvah",
                "blessing",
                "ordination",
                "adoption",
                "naturalization",
                "probate",
                "will",
                "emigration",
                "immigration",
                "retirement",
            ]:
                event_obj = getattr(individual, event_attr, None)
                if event_obj:
                    event_name = event_obj.tag
                    event_date = None
                    if event_obj.date:
                        event_date = self.convert_date(event_obj.date)
                    event_place = ""
                    if event_obj.place:
                        event_place = (
                            event_obj.place.name
                            if hasattr(event_obj.place, "name")
                            else str(event_obj.place)
                        )
                    event_note = event_obj.note if event_obj.note else ""
                    event_src = (
                        ", ".join(event_obj.sources) if event_obj.sources else ""
                    )

                    event = Event(
                        name=event_name,
                        date=event_date,
                        place=event_place,
                        note=event_note,
                        src=event_src,
                    )
                    person.events.append(event)

            # Census events (can be multiple)
            if hasattr(individual, "census") and individual.census:
                for census_event in individual.census:
                    event_date = None
                    if census_event.date:
                        event_date = self.convert_date(census_event.date)
                    event_place = ""
                    if census_event.place:
                        event_place = (
                            census_event.place.name
                            if hasattr(census_event.place, "name")
                            else str(census_event.place)
                        )
                    event_note = census_event.note if census_event.note else ""
                    event_src = (
                        ", ".join(census_event.sources) if census_event.sources else ""
                    )

                    event = Event(
                        name="CENS",
                        date=event_date,
                        place=event_place,
                        note=event_note,
                        src=event_src,
                    )
                    person.events.append(event)

            # Residence events (can be multiple)
            if hasattr(individual, "residence") and individual.residence:
                for resi_event in individual.residence:
                    event_date = None
                    if resi_event.date:
                        event_date = self.convert_date(resi_event.date)
                    event_place = ""
                    if resi_event.place:
                        event_place = (
                            resi_event.place.name
                            if hasattr(resi_event.place, "name")
                            else str(resi_event.place)
                        )
                    event_note = resi_event.note if resi_event.note else ""
                    event_src = (
                        ", ".join(resi_event.sources) if resi_event.sources else ""
                    )

                    event = Event(
                        name="RESI",
                        date=event_date,
                        place=event_place,
                        note=event_note,
                        src=event_src,
                    )
                    person.events.append(event)

            # Apply default source if specified and no sources exist
            if self.options and self.options.default_source:
                # Check if individual has any sources
                has_sources = bool(sources_text)

                if not has_sources:
                    if person.notes:
                        person.notes += (
                            f"\nDefault source: {self.options.default_source}"
                        )
                    else:
                        person.notes = f"Default source: {self.options.default_source}"

            # Handle --uin: put untreated GEDCOM tags in notes
            if self.options and self.options.uin:
                # Process untreated GEDCOM tags and add them as notes
                untreated_tags = self._extract_untreated_tags(individual)
                if untreated_tags:
                    untreated_text = "\n".join(untreated_tags)
                    if person.notes:
                        person.notes += f"\n{untreated_text}"
                    else:
                        person.notes = untreated_text

            return person
        except Exception as e:
            self.logger.error(f"Error converting individual: {e}")
            return GenPerson(first_name="?", surname="?", sex=Sex.NEUTER)

    def convert_family(self, family) -> Tuple[GenFamily, GenCouple, List]:
        """Convert GEDCOM family to GenFamily."""
        try:
            marriage_date = None
            marriage_place = None
            if family.marriage:
                if family.marriage.date:
                    marriage_date = self.convert_date(family.marriage.date)
                if family.marriage.place:
                    # Extract place name from GedcomPlace
                    marriage_place = (
                        family.marriage.place.name
                        if hasattr(family.marriage.place, "name")
                        else str(family.marriage.place)
                    )

            divorce_status = DivorceStatus.NOT_DIVORCED
            divorce_date = None
            divorce_place = None
            if family.divorce:
                divorce_status = DivorceStatus.DIVORCED
                if family.divorce.date:
                    divorce_date = self.convert_date(family.divorce.date)
                if family.divorce.place:
                    # Extract place name from GedcomPlace
                    divorce_place = (
                        family.divorce.place.name
                        if hasattr(family.divorce.place, "name")
                        else str(family.divorce.place)
                    )

            husband_id = dummy_iper()
            if family.husband:
                # Handle both formats: "@I1@" or "I1" (stripped)
                husband_str = family.husband.strip("@")
                if husband_str.startswith("I") or husband_str.isdigit():
                    try:
                        # Extract number: "I1" -> 1, "1" -> 1, "@I1@" -> 1
                        if husband_str.startswith("I"):
                            husband_id = Iper(int(husband_str[1:]))
                        else:
                            husband_id = Iper(int(husband_str))
                    except (ValueError, IndexError):
                        husband_id = Iper(hash(family.husband) % 1000000)
                else:
                    husband_id = Iper(hash(family.husband) % 1000000)

            wife_id = dummy_iper()
            if family.wife:
                # Handle both formats: "@I2@" or "I2" (stripped)
                wife_str = family.wife.strip("@")
                if wife_str.startswith("I") or wife_str.isdigit():
                    try:
                        # Extract number: "I2" -> 2, "2" -> 2, "@I2@" -> 2
                        if wife_str.startswith("I"):
                            wife_id = Iper(int(wife_str[1:]))
                        else:
                            wife_id = Iper(int(wife_str))
                    except (ValueError, IndexError):
                        wife_id = Iper(hash(family.wife) % 1000000)
                else:
                    wife_id = Iper(hash(family.wife) % 1000000)

            children_ids = []
            for child_ref in family.children:
                # Handle both formats: "@I3@" or "I3" (stripped)
                child_str = child_ref.strip("@")
                if child_str.startswith("I") or child_str.isdigit():
                    try:
                        # Extract number: "I3" -> 3, "3" -> 3, "@I3@" -> 3
                        if child_str.startswith("I"):
                            child_id = Iper(int(child_str[1:]))
                        else:
                            child_id = Iper(int(child_str))
                    except (ValueError, IndexError):
                        child_id = Iper(hash(child_ref) % 1000000)
                else:
                    child_id = Iper(hash(child_ref) % 1000000)
                children_ids.append(child_id)

            # Convert notes and sources
            notes_text = ""
            if hasattr(family, "notes") and family.notes:
                notes_text = "\n".join(family.notes)

            sources_text = ""
            if hasattr(family, "sources") and family.sources:
                sources_text = "\n".join(family.sources)

            geneweb_family = GenFamily(
                marriage=marriage_date,
                marriage_place=marriage_place or "",
                divorce=divorce_status,
                divorce_date=divorce_date,
                divorce_place=divorce_place or "",
                relation=RelationKind.MARRIED,
                notes=notes_text,
                sources=sources_text,
            )

            # Convert all other events from family.events
            if hasattr(family, "events") and family.events:
                for gedcom_event in family.events:
                    if not gedcom_event:
                        continue

                    # Get event name from tag or TYPE attribute
                    event_name = gedcom_event.tag
                    if event_name == "EVEN" and gedcom_event.attributes.get("TYPE"):
                        event_name = gedcom_event.attributes["TYPE"]

                    # Skip marriage and divorce (already handled above)
                    if event_name in {"MARR", "DIV", "marriage", "divorce"}:
                        continue

                    # Convert event date
                    event_date = None
                    if gedcom_event.date:
                        event_date = self.convert_date(gedcom_event.date)

                    # Convert event place
                    event_place = ""
                    if gedcom_event.place:
                        event_place = (
                            gedcom_event.place.name
                            if hasattr(gedcom_event.place, "name")
                            else str(gedcom_event.place)
                        )

                    # Convert event note
                    event_note = ""
                    if gedcom_event.note:
                        event_note = gedcom_event.note

                    # Convert event source
                    event_src = ""
                    if gedcom_event.sources:
                        event_src = ", ".join(gedcom_event.sources)

                    # Create Event object
                    event = Event(
                        name=event_name,
                        date=event_date,
                        place=event_place,
                        note=event_note,
                        src=event_src,
                    )
                    geneweb_family.events.append(event)

            # Convert events from dedicated family event fields
            for event_attr in [
                "engagement",
                "marriage_banns",
                "marriage_contract",
                "marriage_license",
                "marriage_settlement",
                "annulment",
            ]:
                event_obj = getattr(family, event_attr, None)
                if event_obj:
                    event_name = event_obj.tag
                    event_date = None
                    if event_obj.date:
                        event_date = self.convert_date(event_obj.date)
                    event_place = ""
                    if event_obj.place:
                        event_place = (
                            event_obj.place.name
                            if hasattr(event_obj.place, "name")
                            else str(event_obj.place)
                        )
                    event_note = event_obj.note if event_obj.note else ""
                    event_src = (
                        ", ".join(event_obj.sources) if event_obj.sources else ""
                    )

                    event = Event(
                        name=event_name,
                        date=event_date,
                        place=event_place,
                        note=event_note,
                        src=event_src,
                    )
                    geneweb_family.events.append(event)

            # Census events (can be multiple)
            if hasattr(family, "census") and family.census:
                for census_event in family.census:
                    event_date = None
                    if census_event.date:
                        event_date = self.convert_date(census_event.date)
                    event_place = ""
                    if census_event.place:
                        event_place = (
                            census_event.place.name
                            if hasattr(census_event.place, "name")
                            else str(census_event.place)
                        )
                    event_note = census_event.note if census_event.note else ""
                    event_src = (
                        ", ".join(census_event.sources) if census_event.sources else ""
                    )

                    event = Event(
                        name="CENS",
                        date=event_date,
                        place=event_place,
                        note=event_note,
                        src=event_src,
                    )
                    geneweb_family.events.append(event)

            couple = GenCouple(father=husband_id, mother=wife_id)

            return geneweb_family, couple, children_ids

        except Exception as e:
            self.logger.error(f"Error converting family: {e}")
            return (
                GenFamily(relation=RelationKind.MARRIED),
                GenCouple(father=dummy_iper(), mother=dummy_iper()),
                [],
            )

    def convert_date(self, gedcom_date) -> Date:
        """Convert GEDCOM date to GeneWeb Date."""
        try:
            if not gedcom_date:
                return Date.none()

            if hasattr(gedcom_date, "year"):
                day = gedcom_date.day if hasattr(gedcom_date, "day") else 0
                month = gedcom_date.month if hasattr(gedcom_date, "month") else 0
                year = gedcom_date.year if hasattr(gedcom_date, "year") else 0

                if day == "":
                    day = 0
                if month == "":
                    month = 0
                if year == "":
                    year = 0

                if isinstance(day, str):
                    try:
                        day = int(day) if day else 0
                    except ValueError:
                        day = 0
                if isinstance(month, str):
                    try:
                        month = int(month) if month else 0
                    except ValueError:
                        month = 0
                if isinstance(year, str):
                    try:
                        year = int(year) if year else 0
                    except ValueError:
                        year = 0

                # Apply date processing options
                day, month, year = self._process_date_components(day, month, year)

                return Date(day=day or 0, month=month or 0, year=year or 0)

            return Date.none()
        except Exception as e:
            self.logger.error(f"Error converting date: {e}")
            return Date.none()

    def _process_date_components(
        self, day: int, month: int, year: int
    ) -> tuple[int, int, int]:
        """Process date components according to options."""
        if not self.options:
            return day, month, year

        # Handle --dates-dm: day/month/year interpretation
        if self.options.dates_dm and not self.options.dates_md:
            # If we have both day and month, and day > 12, swap them
            if day and month and day > 12 and month <= 12:
                day, month = month, day

        # Handle --dates-md: month/day/year interpretation
        elif self.options.dates_md and not self.options.dates_dm:
            # If we have both day and month, and month > 12, swap them
            if day and month and month > 12 and day <= 12:
                day, month = month, day

        # Handle --no-nd: don't interpret minus as negative year
        if self.options.no_nd and year and year < 0:
            year = abs(year)

        # Handle --tnd: set negative dates when inconsistency
        if self.options.tnd and year and year < 0:
            # Keep negative years as is for --tnd
            pass

        return day, month, year

    def _process_first_name(self, first_name: str) -> str:
        """Process first name according to options."""
        if not first_name or not self.options:
            return first_name

        # Handle --efn: extract first name only
        if self.options.efn and not self.options.no_efn:
            names = first_name.split()
            if len(names) > 1:
                first_name = names[0]

        # Handle --fne: extract name between delimiters
        if self.options.fne and not self.options.no_efn:
            start_char = self.options.fne[0] if len(self.options.fne) > 0 else '"'
            end_char = self.options.fne[1] if len(self.options.fne) > 1 else '"'

            start_idx = first_name.find(start_char)
            if start_idx != -1:
                end_idx = first_name.find(end_char, start_idx + 1)
                if end_idx != -1:
                    extracted = first_name[start_idx + 1 : end_idx]
                    if extracted:
                        first_name = extracted

        # Handle --lf: lowercase first names
        if self.options.lf:
            first_name = first_name.lower()

        return first_name

    def _process_surname(self, surname: str) -> str:
        """Process surname according to options."""
        if not surname or not self.options:
            return surname

        # Handle --ls: lowercase with uppercase initials, keep particles lowercase
        if self.options.ls:
            surname = self._to_title_case_with_particles(surname)

        # Handle --us: uppercase (can be combined with --ls)
        if self.options.us:
            surname = surname.upper()

        return surname

    def _to_title_case(self, name: str) -> str:
        """Convert to title case (first letter uppercase, rest lowercase)."""
        if not name:
            return name
        return name.title()

    def _to_title_case_with_particles(self, name: str) -> str:
        """Convert to title case while keeping particles lowercase."""
        if not name:
            return name

        # Common particles to keep lowercase
        particles = {
            "de",
            "du",
            "la",
            "le",
            "des",
            "von",
            "van",
            "der",
            "den",
            "da",
            "di",
            "del",
            "della",
            "delle",
            "dello",
            "degli",
            "dei",
            "delle",
            "della",
            "dello",
            "degli",
            "dei",
        }

        words = name.split()
        result = []

        for word in words:
            if word.lower() in particles:
                result.append(word.lower())
            else:
                result.append(word.title())

        return " ".join(result)

    def _extract_untreated_tags(self, individual) -> list:
        """Extract untreated GEDCOM tags and return them as note strings."""
        untreated_tags = []

        handled_tags = {
            "NAME",
            "SEX",
            "BIRT",
            "BAPM",
            "DEAT",
            "BURI",
            "FAMC",
            "FAMS",
            "MARR",
            "DIV",
            "HUSB",
            "WIFE",
            "CHIL",
            "NOTE",
            "SOUR",
            "OBJE",
        }

        # Check for untreated tags in individual attributes
        for attr_name in dir(individual):
            if attr_name.startswith("_") or attr_name in [
                "xref",
                "names",
                "sex",
                "birth",
                "death",
                "burial",
                "baptism",
                "famc",
                "fams",
                "events",
                "notes",
                "sources",
                "source_citations",
            ]:
                continue

            attr_value = getattr(individual, attr_name)
            if attr_value and attr_name.upper() not in handled_tags:
                # This is likely an untreated tag
                if isinstance(attr_value, str):
                    untreated_tags.append(
                        f"Untreated tag {attr_name.upper()}: {attr_value}"
                    )
                elif isinstance(attr_value, list):
                    for item in attr_value:
                        if isinstance(item, str):
                            untreated_tags.append(
                                f"Untreated tag {attr_name.upper()}: {item}"
                            )
                        else:
                            untreated_tags.append(
                                f"Untreated tag {attr_name.upper()}: {str(item)}"
                            )
                else:
                    untreated_tags.append(
                        f"Untreated tag {attr_name.upper()}: {str(attr_value)}"
                    )

        return untreated_tags
