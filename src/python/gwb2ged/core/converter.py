"""Converter from GeneWeb Base to GEDCOM Database"""

import logging
from typing import Dict, Optional

from lib.db.database.base import Base
from lib.db.core.types import Iper, Ifam
from lib.db.models.events import Date as GeneWebDate
from gedcom.models import (
    GedcomDatabase,
    GedcomHeader,
    GedcomIndividual,
    GedcomFamily,
    GedcomName,
    GedcomEvent,
    GedcomDate,
    GedcomPlace,
)
from gedcom.exporters.individual_exporter import IndividualExporter

from .options import ExportOptions, NoNotes


class BaseToGedcomConverter:
    """Convert GeneWeb Base to GEDCOM Database"""

    def __init__(self, base: Base, options: ExportOptions):
        """
        Initialize converter

        Args:
            base: GeneWeb Base object
            options: Export options
        """
        self.base = base
        self.options = options
        self.logger = logging.getLogger(__name__)
        self.date_formatter = IndividualExporter()  # Use for date formatting

        # Mapping from internal IDs to GEDCOM XREFs
        self.iper_to_xref: Dict[Iper, str] = {}
        self.ifam_to_xref: Dict[Ifam, str] = {}

    def convert(self) -> GedcomDatabase:
        """
        Convert Base to GedcomDatabase

        Returns:
            GedcomDatabase instance
        """
        self.logger.debug("Starting Base to GEDCOM conversion")

        # Create header
        header = self._create_header()

        # Create GEDCOM database
        gedcom_db = GedcomDatabase(header=header)

        # Convert persons
        self.logger.debug(f"Converting {self.base.nb_of_persons()} persons")
        for iper, person in self.base.persons().items():
            xref = self._get_person_xref(iper)
            individual = self._convert_person(person, iper, xref)
            if individual:
                gedcom_db.individuals[xref] = individual
                gedcom_db.record_order.append(("INDI", xref))

        # Convert families
        self.logger.debug(f"Converting {self.base.nb_of_families()} families")
        for ifam, family in self.base.families().items():
            xref = self._get_family_xref(ifam)
            gedcom_family = self._convert_family(family, ifam, xref)
            if gedcom_family:
                gedcom_db.families[xref] = gedcom_family
                gedcom_db.record_order.append(("FAM", xref))

        self.logger.info(
            f"Converted {len(gedcom_db.individuals)} individuals, "
            f"{len(gedcom_db.families)} families"
        )

        return gedcom_db

    def _create_header(self) -> GedcomHeader:
        """Create GEDCOM header"""
        # Determine version based on charset
        version = "5.5.1" if self.options.charset.value == "UTF-8" else "5.5"

        header = GedcomHeader(
            source="GeneWeb",
            charset=self.options.charset.value,
            version=version,
            filename=(
                str(self.options.output_file.name) if self.options.output_file else None
            ),
        )

        return header

    def _get_person_xref(self, iper: Iper) -> str:
        """Get GEDCOM XREF for person ID"""
        if iper not in self.iper_to_xref:
            # ged2gwb already stores GEDCOM IDs directly (Iper(1) from @I1@)
            # So we use the Iper value directly without adding +1
            xref_num = int(iper)
            xref = f"@I{xref_num}@"
            self.iper_to_xref[iper] = xref

            # Add index if requested
            if self.options.indexes:
                # Store original GeneWeb ID in private field
                pass  # Will be handled in export

        return self.iper_to_xref[iper]

    def _get_family_xref(self, ifam: Ifam) -> str:
        """Get GEDCOM XREF for family ID"""
        if ifam not in self.ifam_to_xref:
            # ged2gwb already stores GEDCOM IDs directly (Ifam(1) from @F1@)
            # So we use the Ifam value directly without adding +1
            xref_num = int(ifam)
            xref = f"@F{xref_num}@"
            self.ifam_to_xref[ifam] = xref
        return self.ifam_to_xref[ifam]

    def _convert_person(self, person, iper: Iper, xref: str) -> GedcomIndividual:
        """Convert GenPerson to GedcomIndividual"""
        individual = GedcomIndividual(xref=xref)

        first_name = person.first_name
        surname = person.surname

        if first_name or surname:
            name = GedcomName(
                full=f"{first_name or '?'} /{surname or '?'}/",
                given=first_name or None,
                surname=surname or None,
            )
            individual.names.append(name)

        # Convert sex (Sex enum: MALE="M", FEMALE="F", NEUTER="U")
        if person.sex:
            from lib.db.core.enums import Sex

            if person.sex == Sex.MALE:
                individual.sex = "M"
            elif person.sex == Sex.FEMALE:
                individual.sex = "F"
            else:
                individual.sex = "U"

        # Convert birth
        if person.birth and not (
            person.birth.year == 0 and person.birth.month == 0 and person.birth.day == 0
        ):
            birth_date = self._convert_date_to_gedcom(person.birth)
            if birth_date:
                # Look for birth place in events (if stored as Event with place)
                birth_place = None
                for event in person.events:
                    if event.name.lower() in ["birth", "birt", "naissance"] and event.place:
                        birth_place = event.place
                        break
                # Create birth event with place if available
                individual.birth = GedcomEvent(
                    tag="BIRT",
                    date=birth_date,
                    place=GedcomPlace(name=birth_place) if birth_place else None,
                )

        # Convert death
        if person.death and not (
            person.death.year == 0 and person.death.month == 0 and person.death.day == 0
        ):
            death_date = self._convert_date_to_gedcom(person.death)
            if death_date:
                # Look for death place in events (if stored as Event with place)
                death_place = None
                for event in person.events:
                    if event.name.lower() in ["death", "deat", "décès", "deces"] and event.place:
                        death_place = event.place
                        break
                # Create death event with place if available
                individual.death = GedcomEvent(
                    tag="DEAT",
                    date=death_date,
                    place=GedcomPlace(name=death_place) if death_place else None,
                )

        # Convert notes (if not excluded)
        if self.options.no_notes != NoNotes.NNN:
            if person.notes:
                individual.notes.append(person.notes)

        # Convert families relationships (family as child)
        ascend = self.base.ascend(iper)
        if ascend and ascend.parents:
            # ascend.parents is a list of Iper (the parents)
            # We need to find the family (Ifam) that has this couple
            if isinstance(ascend.parents, list) and len(ascend.parents) >= 1:
                # Find family where couple matches these parents
                parent_iper_set = set(ascend.parents)
                for ifam, family_couple in self.base.data.couples.items():
                    couple = family_couple
                    # Check if this couple matches the parents (father and/or mother in parent list)
                    if (
                        couple.father in parent_iper_set
                        or couple.mother in parent_iper_set
                    ):
                        xref = self._get_family_xref(ifam)
                        if xref.strip("@") not in individual.famc:
                            individual.famc.append(xref.strip("@"))
                        # If we found both parents, we can break
                        if (
                            couple.father in parent_iper_set
                            and couple.mother in parent_iper_set
                        ):
                            break

        union = self.base.union(iper)
        if union and union.family:
            for ifam in union.family:
                xref = self._get_family_xref(ifam)
                individual.fams.append(xref.strip("@"))

        return individual

    def _convert_family(self, family, ifam: Ifam, xref: str) -> GedcomFamily:
        """Convert GenFamily to GedcomFamily"""
        gedcom_family = GedcomFamily(xref=xref)

        # Get couple information (husband/wife from GenCouple)
        couple = self.base.couple(ifam)
        if couple:
            if couple.father and couple.father != Iper(0):
                husband_xref = self._get_person_xref(couple.father)
                gedcom_family.husband = husband_xref.strip("@")
            if couple.mother and couple.mother != Iper(0):
                wife_xref = self._get_person_xref(couple.mother)
                gedcom_family.wife = wife_xref.strip("@")

        # Convert children
        descend = self.base.descend(ifam)
        if descend and descend.children:
            for child_iper in descend.children:
                child_xref = self._get_person_xref(child_iper)
                gedcom_family.children.append(child_xref.strip("@"))

        # Convert marriage
        if family.marriage and not (
            family.marriage.year == 0
            and family.marriage.month == 0
            and family.marriage.day == 0
        ):
            marriage_date = self._convert_date_to_gedcom(family.marriage)
            if marriage_date:
                # marriage_place is stored as string in MessagePack
                place_str = family.marriage_place if family.marriage_place else None
                marriage_event = GedcomEvent(
                    tag="MARR",
                    date=marriage_date,
                    place=GedcomPlace(name=place_str) if place_str else None,
                )

                # Add marriage note if not excluded
                if self.options.no_notes != NoNotes.NNN and family.marriage_note:
                    marriage_event.note = family.marriage_note

                gedcom_family.marriage = marriage_event

        # Convert notes (if not excluded)
        if self.options.no_notes != NoNotes.NNN:
            if family.notes:
                gedcom_family.notes.append(family.notes)

        return gedcom_family

    def _convert_event(self, event, tag: str) -> Optional[GedcomEvent]:
        """Convert event to GedcomEvent"""
        # Event can be a Date (for birth/death) or Event object
        gedcom_event = GedcomEvent(tag=tag)

        # Handle Date object (for birth/death)
        if isinstance(event, GeneWebDate):
            date_obj = self._convert_date_to_gedcom(event)
            if date_obj:
                gedcom_event.date = date_obj
            else:
                return None
        # Handle Event object
        elif hasattr(event, "date"):
            if event.date:
                date_obj = self._convert_date_to_gedcom(event.date)
                if date_obj:
                    gedcom_event.date = date_obj

            # Convert place (Event.place is stored as string)
            if hasattr(event, "place") and event.place:
                gedcom_event.place = GedcomPlace(name=event.place)

            # Convert note (if not excluded, Event.note is stored as string)
            if self.options.no_notes != NoNotes.NNN:
                if hasattr(event, "note") and event.note:
                    gedcom_event.note = event.note

        return gedcom_event

    def _convert_date_to_gedcom(self, date: GeneWebDate) -> Optional[GedcomDate]:
        """Convert GeneWeb Date to GedcomDate"""
        if not date or (date.year == 0 and date.month == 0 and date.day == 0):
            return None

        # Create GedcomDate with components
        gedcom_date = GedcomDate(
            raw="",  # Will be formatted
            year=date.year if date.year > 0 else None,
            month=date.month if date.month > 0 else None,
            day=date.day if date.day > 0 else None,
        )

        # Set flags
        gedcom_date.has_year = date.year > 0
        gedcom_date.has_month = date.month > 0
        gedcom_date.has_day = date.day > 0

        # Format the raw string using the date formatter
        if gedcom_date.year or gedcom_date.month or gedcom_date.day:
            raw_str = self.date_formatter._format_simple_date(gedcom_date)
            gedcom_date.raw = raw_str if raw_str else ""

        return gedcom_date
