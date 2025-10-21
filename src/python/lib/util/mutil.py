from ..db_pickle.models.family import GenFamily, Date
from ..db_pickle.models.person import GenPerson


def nominative(s: str) -> str:
    """
    Get nominative form of a string.
    If string contains ':', use decline('n'),
    otherwise return string as-is.

    Args:
        s: Input string

    Returns:
        String in nominative form
    """
    try:
        _ = s.rindex(":")
        return decline("n", s)
    except ValueError:
        return s


def empty_person(what: str, *, per_index: int = -1) -> GenPerson:
    """Create an empty GenPerson instance."""
    return GenPerson(key_index=per_index, first_name=what, surname=what, occ=0)


def empty_family(*, fam_index: int = -1) -> GenFamily:
    """Create an empty GenFamily instance."""
    return GenFamily(
        fam_index=fam_index,
        marriage=Date.none(),
    )
