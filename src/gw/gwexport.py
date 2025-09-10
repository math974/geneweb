from enum import Enum
from typing import Optional, List, Tuple, Callable, Dict, Union
from dataclasses import dataclass


class GwexportCharset(Enum):
    ANSEL = "ansel"
    ANSI = "ansi"
    ASCII = "ascii"
    UTF8 = "utf8"


class NoNotes(Enum):
    NN = "nn"  # Placeholder for no notes option
    NNN = "nnn"  # Placeholder for extended no notes option
    NONE = "none"  # Placeholder for allowing notes


@dataclass
class GwexportOpts:
    """Options for Geneweb export operations"""

    # Maximum generation of the root's ascendants
    asc: Optional[int] = None

    # Maximum generation of the root's ascendants descendants
    ascdesc: Optional[int] = None

    # Censors the base for 'n' years
    censor: int = 0

    # The charset of the export
    charset: GwexportCharset = GwexportCharset.UTF8

    # Maximum generation of the root's descendants
    desc: Optional[int] = None

    # Unused by this module (and not set by options)
    img_base_path: str = ""

    # Key reference of additional persons to select
    keys: List[str] = None

    # Unused by this module
    mem: bool = False

    # Unused by this module
    no_notes: NoNotes = NoNotes.NONE

    # Unused by this module
    no_picture: bool = False

    # Unused by this module - (filename, write_func, close_func)
    oc: Tuple[str, Callable[[str], None], Callable[[], None]] = None

    # If asc, ascdesc and desc are not set & parenting = true,
    # then select individuals involved in parentship between pair of keys
    # (/!\ assumes the input are pairs of keys)
    parentship: bool = False

    # Unused by this module
    picture_path: bool = False

    # Unused by this module
    source: Optional[str] = None

    # Used to select persons by their surname
    surnames: List[str] = None

    # Unused by this module
    verbose: bool = False

    def __post_init__(self):
        if self.keys is None:
            self.keys = []
        if self.surnames is None:
            self.surnames = []
        if self.oc is None:
            # Default placeholder for output handlers
            self.oc = ("", lambda s: None, lambda: None)


# Default set of options
default_opts = GwexportOpts()


def select(
    base, opts: GwexportOpts, ips: List[int]
) -> Tuple[Callable[[int], bool], Callable[[int], bool]]:
    """
    Returns filters for iper and ifam to be used when exporting a portion of the base.

    Args:
        base: Database instance
        opts: Export options
        ips: List of person IDs

    Returns:
        Tuple of (person_filter, family_filter) functions
    """
    from .gwutil import Driver, Collection, person_of_string_key
    import time
    from typing import Any

    # Add persons from keys to the initial list
    additional_ips = [
        p for key in opts.keys if (p := person_of_string_key(base, key)) is not None
    ]
    ips = [*ips, *additional_ips]

    # Handle censorship
    if opts.censor != 0:
        pmark = Driver.iper_marker(Driver.ipers(base), 0)
        fmark = Driver.ifam_marker(Driver.ifams(base), 0)

        def is_censored_person(threshold: int, p: Any) -> bool:
            birth = Driver.get_birth(p)
            if birth is None:
                return False
            birth_year = birth.year  # Placeholder for actual date extraction
            return birth_year >= threshold and Driver.get_access(p) != "Public"

        def is_censored_couple(threshold: int, family: Any) -> bool:
            father = Driver.poi(base, Driver.get_father(family))
            mother = Driver.poi(base, Driver.get_mother(family))
            return is_censored_person(threshold, father) or is_censored_person(
                threshold, mother
            )

        def censor_person(threshold: int, pid: int, no_check: bool = False) -> None:
            person = Driver.poi(base, pid)
            if no_check or is_censored_person(threshold, person):
                Collection.Marker.set(pmark, pid, Collection.Marker.get(pmark, pid) | 1)

        def censor_family(threshold: int, fid: int, no_check: bool = False) -> None:
            if Collection.Marker.get(fmark, fid) == 0:
                family = Driver.foi(base, fid)
                if no_check or is_censored_couple(threshold, family):
                    # Mark family
                    Collection.Marker.set(
                        fmark, fid, Collection.Marker.get(fmark, fid) | 1
                    )

                    # Censor parents if all their families are censored
                    for parent_id in [
                        Driver.get_father(family),
                        Driver.get_mother(family),
                    ]:
                        parent = Driver.poi(base, parent_id)
                        if all(
                            Collection.Marker.get(fmark, f) == 0
                            for f in Driver.get_family(parent)
                        ):
                            Collection.Marker.set(
                                pmark,
                                parent_id,
                                Collection.Marker.get(pmark, parent_id) | 1,
                            )

                    # Censor descendants
                    for child_id in Driver.get_children(family):
                        if Collection.Marker.get(pmark, child_id) == 0:
                            child = Driver.poi(base, child_id)
                            for child_fam in Driver.get_family(child):
                                censor_family(threshold, child_fam, True)
                                censor_person(threshold, child_id, True)

        if opts.censor == -1:
            # Restrict base access
            for pid in Driver.ipers(base):
                if Driver.base_visible_get(base, lambda _: False, pid):
                    Collection.Marker.set(
                        pmark, pid, Collection.Marker.get(pmark, pid) | 1
                    )

            for fid in Driver.ifams(base):
                family = Driver.foi(base, fid)
                children = Driver.get_children(family)

                # Check if any children are visible
                children_visible = any(
                    Collection.Marker.get(pmark, c) == 0 for c in children
                )

                # Check if parents are visible
                parents_not_visible = (
                    Collection.Marker.get(pmark, Driver.get_father(family)) != 0
                    or Collection.Marker.get(pmark, Driver.get_mother(family)) != 0
                )

                if (not children_visible) and parents_not_visible:
                    Collection.Marker.set(
                        fmark, fid, Collection.Marker.get(fmark, fid) | 1
                    )
        else:
            # Censor based on year threshold
            current_year = time.localtime().tm_year
            threshold = 1900 + current_year - opts.censor

            # Censor all families and persons
            for fid in Driver.ifams(base):
                censor_family(threshold, fid, False)
            for pid in Driver.ipers(base):
                censor_person(threshold, pid, False)

        def not_censored_p(i: int) -> bool:
            return Collection.Marker.get(pmark, i) == 0

        def not_censored_f(i: int) -> bool:
            return Collection.Marker.get(fmark, i) == 0

    else:

        def not_censored_p(_: int) -> bool:
            return True

        def not_censored_f(_: int) -> bool:
            return True

    # Handle selection
    if opts.ascdesc is not None or opts.desc is not None:
        assert opts.censor == 0

        # TODO: Implement complex selection logic for ascdesc and desc
        def sel_per(i: int) -> bool:
            return True  # Placeholder

        def sel_fam(i: int) -> bool:
            return True  # Placeholder

    elif opts.asc is not None:
        # TODO: Implement ancestor selection
        def sel_per(i: int) -> bool:
            return True  # Placeholder

        def sel_fam(i: int) -> bool:
            return True  # Placeholder

    elif opts.surnames:
        # Select by surnames
        pmark = Driver.iper_marker(Driver.ipers(base), False)
        fmark = Driver.ifam_marker(Driver.ifams(base), False)

        def select_surname(surname: str) -> None:
            surname = surname.strip().lower()
            for fid in Driver.ifams(base):
                family = Driver.foi(base, fid)
                father = Driver.poi(base, Driver.get_father(family))
                mother = Driver.poi(base, Driver.get_mother(family))

                father_surname = (
                    Driver.sou(base, Driver.get_surname(father)).strip().lower()
                )
                mother_surname = (
                    Driver.sou(base, Driver.get_surname(mother)).strip().lower()
                )

                if father_surname == surname or mother_surname == surname:
                    Collection.Marker.set(fmark, fid, True)
                    Collection.Marker.set(pmark, Driver.get_father(family), True)
                    Collection.Marker.set(pmark, Driver.get_mother(family), True)

                    for child_id in Driver.get_children(family):
                        child = Driver.poi(base, child_id)
                        if (
                            not Collection.Marker.get(pmark, child_id)
                            and Driver.sou(base, Driver.get_surname(child))
                            .strip()
                            .lower()
                            == surname
                        ):
                            Collection.Marker.set(pmark, child_id, True)

        for surname in opts.surnames:
            select_surname(surname)

        def sel_per(i: int) -> bool:
            return bool(Collection.Marker.get(pmark, i))

        def sel_fam(i: int) -> bool:
            return bool(Collection.Marker.get(fmark, i))

    elif opts.parentship:
        # TODO: Implement parentship selection
        def sel_per(i: int) -> bool:
            return True  # Placeholder

        def sel_fam(i: int) -> bool:
            return True  # Placeholder

    else:

        def sel_per(_: int) -> bool:
            return True

        def sel_fam(_: int) -> bool:
            return True

    # Combine censorship and selection filters
    def person_filter(i: int) -> bool:
        return not_censored_p(i) and sel_per(i)

    def family_filter(i: int) -> bool:
        return not_censored_f(i) and sel_fam(i)

    return person_filter, family_filter


def add_arguments(parser) -> None:
    """
    Add export-related arguments to an ArgumentParser.
    This is equivalent to the OCaml speclist function.

    Args:
        parser: ArgumentParser instance to add arguments to
    """
    parser.add_argument(
        "-a",
        type=int,
        metavar="N",
        help="maximum generation of the root's ascendants",
        dest="asc",
    )

    parser.add_argument(
        "-ad",
        type=int,
        metavar="N",
        help="maximum generation of the root's ascendants descendants",
        dest="ascdesc",
    )

    parser.add_argument(
        "-key",
        action="append",
        metavar="KEY",
        help="key reference of root person. Used for -a/-d options. Can be used "
        'multiple times. Key format is "First Name.occ SURNAME"',
        dest="keys",
    )

    parser.add_argument(
        "-c",
        type=int,
        metavar="NUM",
        help="when a person is born less than <num> years ago, it is not "
        "exported unless it is Public. All the spouses and descendants are also "
        "censored.",
        dest="censor",
    )

    parser.add_argument(
        "-charset",
        type=str,
        choices=["ASCII", "ANSEL", "ANSI", "UTF-8"],
        help="set charset; default is UTF-8",
        dest="charset",
    )

    parser.add_argument(
        "-d",
        type=int,
        metavar="N",
        help="maximum generation of the root's descendants",
        dest="desc",
    )

    parser.add_argument(
        "-mem", action="store_true", help="save memory space, but slower", dest="mem"
    )

    parser.add_argument(
        "-nn", action="store_true", help="no (database) notes", dest="no_notes_nn"
    )

    parser.add_argument(
        "-nnn", action="store_true", help="no notes (implies -nn)", dest="no_notes_nnn"
    )

    parser.add_argument(
        "-nopicture",
        action="store_true",
        help="don't extract individual picture",
        dest="no_picture",
    )

    parser.add_argument(
        "-o",
        type=str,
        metavar="FILE",
        help="output file name (default: stdout)",
        dest="output_file",
    )

    parser.add_argument(
        "-parentship",
        action="store_true",
        help="select individuals involved in parentship computation between pairs of "
        "keys. Pairs must be defined with -key option, descendant first: e.g. "
        '-key "Descendant.0 SURNAME" -key "Ancestor.0 SURNAME". If multiple '
        "pairs are provided, union of persons are returned.",
        dest="parentship",
    )

    parser.add_argument(
        "-picture-path",
        action="store_true",
        help="extract pictures path",
        dest="picture_path",
    )

    parser.add_argument(
        "-s",
        action="append",
        metavar="SN",
        help="select this surname (option usable several times, union of "
        "surnames will be used)",
        dest="surnames",
    )

    parser.add_argument(
        "-source",
        type=str,
        metavar="SRC",
        help="replace individuals and families sources. Also delete event sources",
        dest="source",
    )

    parser.add_argument("-v", action="store_true", help="verbose", dest="verbose")


# Error message for argument parsing
errmsg = "Usage: program [options] database"
