"""Converter from GeneWeb Base to GEDCOM Database"""

import logging
from typing import Dict, List, Optional

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

        # Apply selection filters to get selected persons and families
        selected_persons, selected_families = self._apply_selection()

        self.logger.debug(
            f"After selection: {len(selected_persons)} persons, {len(selected_families)} families"
        )

        # Convert selected persons
        for iper in selected_persons:
            person = self.base.person(iper)
            if person:
                xref = self._get_person_xref(iper)
                individual = self._convert_person(person, iper, xref)
                if individual:
                    gedcom_db.individuals[xref] = individual
                    gedcom_db.record_order.append(("INDI", xref))

        # Convert selected families (only if both spouses are selected)
        for ifam in selected_families:
            family = self.base.family(ifam)
            if family:
                couple = self.base.couple(ifam)
                if couple:
                    # Only include family if at least one spouse is selected
                    if (
                        couple.father in selected_persons
                        or couple.mother in selected_persons
                    ):
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
                    if (
                        event.name.lower() in ["birth", "birt", "naissance"]
                        and event.place
                    ):
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
                    if (
                        event.name.lower() in ["death", "deat", "décès", "deces"]
                        and event.place
                    ):
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
            if isinstance(ascend.parents, list) and ascend.parents:
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
                # marriage_place is stored as string in the database
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

    def _apply_selection(self) -> tuple[set[Iper], set[Ifam]]:
        """
        Apply selection options to determine which persons and families to export.

        Returns:
            Tuple of (selected_persons, selected_families) sets
        """
        selected_persons: set[Iper] = set()
        selected_families: set[Ifam] = set()

        # Start with all persons if no selection
        all_persons = set(self.base.persons().keys())

        # Apply selection filters
        if self.options.keys:
            # Select by keys (format: "First Name.occ SURNAME")
            key_persons = self._select_by_keys(self.options.keys)
            selected_persons.update(key_persons)
            self.logger.debug(f"Selected {len(key_persons)} persons by keys")

            # If parentship is enabled, select individuals in the path between key pairs
            if self.options.parentship:
                parentship_persons = self._select_parentship(self.options.keys)
                selected_persons.update(parentship_persons)
                self.logger.debug(
                    f"Selected {len(parentship_persons)} persons by parentship"
                )

            # Apply asc/desc/ascdesc based on selected keys
            if key_persons:
                for root_iper in key_persons:
                    if self.options.asc is not None:
                        asc_persons = self._select_ascendants(
                            root_iper, self.options.asc
                        )
                        selected_persons.update(asc_persons)
                        self.logger.debug(
                            f"Selected {len(asc_persons)} ascendants for {root_iper}"
                        )

                    if self.options.desc is not None:
                        desc_persons = self._select_descendants(
                            root_iper, self.options.desc
                        )
                        selected_persons.update(desc_persons)
                        self.logger.debug(
                            f"Selected {len(desc_persons)} descendants for {root_iper}"
                        )

                    if self.options.ascdesc is not None:
                        asc_persons = self._select_ascendants(
                            root_iper, self.options.ascdesc
                        )
                        selected_persons.update(asc_persons)
                        # For each ascendant, get their descendants
                        for asc_iper in asc_persons:
                            desc_persons = self._select_descendants(
                                asc_iper, self.options.ascdesc
                            )
                            selected_persons.update(desc_persons)
                        self.logger.debug(
                            f"Selected ascendants and their descendants for {root_iper}"
                        )

        elif self.options.surnames:
            # Select by surnames
            surname_persons = self._select_by_surnames(self.options.surnames)
            selected_persons.update(surname_persons)
            self.logger.debug(f"Selected {len(surname_persons)} persons by surnames")
        else:
            # No selection: export all
            selected_persons = all_persons

        selected_families = self._collect_families(selected_persons)

        # This ensures that when a person is selected, their family members are also exported
        selected_persons = self._expand_with_family_members(
            selected_persons, selected_families
        )

        selected_families = self._collect_families(selected_persons)

        return selected_persons, selected_families

    def _select_by_keys(self, keys: List[str]) -> set[Iper]:
        """
        Select persons by keys (format: "First Name.occ SURNAME").

        Args:
            keys: List of key strings

        Returns:
            Set of selected person IDs
        """
        selected: set[Iper] = set()

        for key_str in keys:
            # Parse key: "First Name.occ SURNAME" or "First Name SURNAME" or "SURNAME"
            parts = key_str.strip().split()
            if not parts:
                continue

            # Handle different formats
            if len(parts) == 1:
                # Just surname
                surname = parts[0]
                first_name = ""
                occ = 0
            elif len(parts) == 2:
                # "First Name SURNAME" or "First Name.occ SURNAME"
                first_part = parts[0]
                surname = parts[1]

                if "." in first_part:
                    # Has occurrence number
                    first_name, occ_str = first_part.rsplit(".", 1)
                    try:
                        occ = int(occ_str)
                    except ValueError:
                        occ = 0
                else:
                    first_name = first_part
                    occ = 0
            else:
                # Multiple words in first name: "First Middle.occ SURNAME"
                last_part = parts[-1]  # surname
                first_parts = parts[:-1]  # first name parts
                surname = last_part

                # Check if last first name part has occurrence
                last_first_part = first_parts[-1]
                if "." in last_first_part:
                    name_part, occ_str = last_first_part.rsplit(".", 1)
                    first_parts[-1] = name_part
                    try:
                        occ = int(occ_str)
                    except ValueError:
                        occ = 0
                else:
                    occ = 0

                first_name = " ".join(first_parts)

            # Search for matching persons
            for iper, person in self.base.persons().items():
                if (
                    person.surname == surname
                    and person.first_name == first_name
                    and person.occ == occ
                ):
                    selected.add(iper)

        return selected

    def _select_by_surnames(self, surnames: List[str]) -> set[Iper]:
        """
        Select persons by surnames.

        Args:
            surnames: List of surnames to match

        Returns:
            Set of selected person IDs
        """
        selected: set[Iper] = set()

        for surname in surnames:
            surname = surname.strip()
            if not surname:
                continue

            # Search persons by surname (case-insensitive)
            for iper, person in self.base.persons().items():
                if person.surname.lower() == surname.lower():
                    selected.add(iper)

        return selected

    def _select_ascendants(self, root_iper: Iper, max_generations: int) -> set[Iper]:
        """
        Select ascendants (ancestors) up to max_generations.

        Args:
            root_iper: Root person ID
            max_generations: Maximum number of generations to go up

        Returns:
            Set of selected person IDs including root
        """
        selected: set[Iper] = {root_iper}

        if max_generations <= 0:
            return selected

        def traverse_ascendants(iper: Iper, generation: int):
            if generation >= max_generations:
                return

            ascend = self.base.ascend(iper)
            if ascend and ascend.parents:
                # ascend.parents is Ifam (family ID), as per OCaml gen_ascend structure
                family_id = ascend.parents
                couple = self.base.couple(family_id)
                if couple:
                    if (
                        couple.father
                        and couple.father != Iper(0)
                        and couple.father not in selected
                    ):
                        selected.add(couple.father)
                        traverse_ascendants(couple.father, generation + 1)
                    if (
                        couple.mother
                        and couple.mother != Iper(0)
                        and couple.mother not in selected
                    ):
                        selected.add(couple.mother)
                        traverse_ascendants(couple.mother, generation + 1)

        traverse_ascendants(root_iper, 0)
        return selected

    def _select_descendants(self, root_iper: Iper, max_generations: int) -> set[Iper]:
        """
        Select descendants up to max_generations.

        Args:
            root_iper: Root person ID
            max_generations: Maximum number of generations to go down

        Returns:
            Set of selected person IDs including root
        """
        selected: set[Iper] = {root_iper}

        if max_generations <= 0:
            return selected

        def traverse_descendants(iper: Iper, generation: int):
            if generation >= max_generations:
                return

            union = self.base.union(iper)
            if union and union.family:
                for ifam in union.family:
                    descend = self.base.descend(ifam)
                    if descend and descend.children:
                        for child_iper in descend.children:
                            if child_iper and child_iper not in selected:
                                selected.add(child_iper)
                                traverse_descendants(child_iper, generation + 1)

        traverse_descendants(root_iper, 0)
        return selected

    def _select_parentship(self, keys: List[str]) -> set[Iper]:
        """
        Select individuals involved in parentship computation between key pairs.
        Pairs must be defined with -key option, descendant first.

        Args:
            keys: List of keys (should be pairs: descendant, ancestor)

        Returns:
            Set of selected person IDs
        """
        selected: set[Iper] = set()

        if len(keys) < 2:
            return selected

        # Process keys in pairs (descendant, ancestor)
        for i in range(0, len(keys) - 1, 2):
            desc_key = keys[i]
            anc_key = keys[i + 1]

            desc_persons = self._select_by_keys([desc_key])
            anc_persons = self._select_by_keys([anc_key])

            # Find path between descendant and ancestor
            for desc_iper in desc_persons:
                for anc_iper in anc_persons:
                    path_persons = self._find_parentship_path(desc_iper, anc_iper)
                    selected.update(path_persons)

        return selected

    def _find_parentship_path(self, desc_iper: Iper, anc_iper: Iper) -> set[Iper]:
        """
        Find all persons in the path from descendant to ancestor.

        Args:
            desc_iper: Descendant person ID
            anc_iper: Ancestor person ID

        Returns:
            Set of person IDs in the path
        """
        # Use a list to preserve order and track the path correctly
        path_list: list[Iper] = []

        def find_path_upward(
            current_iper: Iper, target_iper: Iper, visited: set[Iper]
        ) -> bool:
            if current_iper == target_iper:
                path_list.append(current_iper)
                return True

            if current_iper in visited:
                return False

            visited.add(current_iper)
            path_list.append(current_iper)

            ascend = self.base.ascend(current_iper)
            if ascend and ascend.parents:
                # ascend.parents is Ifam (family ID), as per OCaml gen_ascend structure
                family_id = ascend.parents
                couple = self.base.couple(family_id)
                if couple:
                    if couple.father and couple.father != Iper(0):
                        if find_path_upward(couple.father, target_iper, visited):
                            return True
                    if couple.mother and couple.mother != Iper(0):
                        if find_path_upward(couple.mother, target_iper, visited):
                            return True

            # If we didn't find the target through this path, remove current from path
            path_list.pop()
            return False

        find_path_upward(desc_iper, anc_iper, set())
        # Return as set but always include both ends
        path = set(path_list)
        path.add(desc_iper)
        path.add(anc_iper)
        return path

    def _expand_with_family_members(
        self, selected_persons: set[Iper], selected_families: set[Ifam]
    ) -> set[Iper]:
        """
        Expand selected persons to include all family members (spouses and children).

        This follows OCaml behavior where selecting a person automatically includes:
        - Their spouses (from unions)
        - Their children (from families where they are parents)
        - Parents' spouses (from families where selected persons are children)

        Args:
            selected_persons: Set of initially selected person IDs
            selected_families: Set of family IDs already identified

        Returns:
            Expanded set of selected person IDs including family members
        """
        expanded = set(selected_persons)

        # Add spouses of selected persons
        for iper in selected_persons:
            union = self.base.union(iper)
            if union and union.family:
                for ifam in union.family:
                    couple = self.base.couple(ifam)
                    if couple:
                        if couple.father and couple.father != Iper(0):
                            expanded.add(couple.father)
                        if couple.mother and couple.mother != Iper(0):
                            expanded.add(couple.mother)

        # Add children of selected persons
        for iper in selected_persons:
            union = self.base.union(iper)
            if union and union.family:
                for ifam in union.family:
                    descend = self.base.descend(ifam)
                    if descend and descend.children:
                        for child_iper in descend.children:
                            if child_iper and child_iper != Iper(0):
                                expanded.add(child_iper)

        # Add spouses of persons whose families are included
        # (if a child is selected, include both parents)
        for ifam in selected_families:
            couple = self.base.couple(ifam)
            if couple:
                if couple.father and couple.father != Iper(0):
                    expanded.add(couple.father)
                if couple.mother and couple.mother != Iper(0):
                    expanded.add(couple.mother)

            # Also add children in these families
            descend = self.base.descend(ifam)
            if descend and descend.children:
                for child_iper in descend.children:
                    if child_iper and child_iper != Iper(0):
                        expanded.add(child_iper)

        # Add parents and their spouses (if a child is selected, include parents' spouses)
        for iper in list(expanded):  # Use list to avoid modifying during iteration
            ascend = self.base.ascend(iper)
            if ascend and ascend.parents:
                family_id = ascend.parents
                couple = self.base.couple(family_id)
                if couple:
                    if couple.father and couple.father != Iper(0):
                        expanded.add(couple.father)
                    if couple.mother and couple.mother != Iper(0):
                        expanded.add(couple.mother)

        return expanded

    def _collect_families(self, selected_persons: set[Iper]) -> set[Ifam]:
        """
        Collect all families that involve selected persons.

        Args:
            selected_persons: Set of selected person IDs

        Returns:
            Set of family IDs
        """
        selected_families: set[Ifam] = set()

        # Find families where selected persons are spouses
        for ifam in self.base.families().keys():
            couple = self.base.couple(ifam)
            if couple and (
                couple.father in selected_persons or couple.mother in selected_persons
            ):
                selected_families.add(ifam)

        # Find families where selected persons are children
        for ifam in self.base.families().keys():
            descend = self.base.descend(ifam)
            if descend and descend.children:
                for child_iper in descend.children:
                    if child_iper in selected_persons:
                        selected_families.add(ifam)
                        break
        return selected_families
