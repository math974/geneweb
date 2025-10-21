"""Consanguinity calculation module.

Original OCaml module copyright (c) 1998-2007 INRIA
Algorithm relationship and links from Didier Remy
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Tuple, Any

from lib.db_pickle.database import driver as Driver
from lib.db_pickle.collection import Marker


class AncStat(Enum):
    """Ancestor status enumeration."""

    MAYBE_ANC = auto()
    IS_ANC = auto()


@dataclass
class Relationship:
    """Relationship data structure."""

    weight1: float = 0.0
    weight2: float = 0.0
    relationship: float = 0.0
    lens1: List[Tuple[int, int, List[Driver.Iper]]] = field(default_factory=list)
    lens2: List[Tuple[int, int, List[Driver.Iper]]] = field(default_factory=list)
    inserted: int = 0
    elim_ancestors: bool = False
    anc_stat1: AncStat = AncStat.MAYBE_ANC
    anc_stat2: AncStat = AncStat.MAYBE_ANC

    def __post_init__(self):
        pass  # All initialization is now handled by default values


@dataclass
class RelationshipInfo:
    """Relationship information container."""

    tstab: Marker[Driver.Iper, int]
    reltab: Marker[Driver.Iper, Relationship]
    queue: List[List[Driver.Iper]]


class Visit(Enum):
    """Visit status for graph traversal."""

    NOT_VISITED = auto()  # not visited person
    BEING_VISITED = auto()  # visited but ascendants haven't been terminated
    VISITED = auto()  # visited person and ascendants


def half(x: float) -> float:
    """Return half of the input value."""
    return x * 0.5


def noloop_aux(
    base: Driver.Base, error: Any, tab: Marker[Driver.Iper, Visit], i: Driver.Iper
) -> None:
    """Auxiliary function for cycle detection."""
    match tab.get(i):
        case Visit.NOT_VISITED:
            parents = Driver.get_parents(Driver.poi(base, i))
            if parents is not None:
                fam = Driver.foi(base, parents)
                fath = Driver.get_father(fam)
                moth = Driver.get_mother(fam)
                tab.set(i, Visit.BEING_VISITED)
                noloop_aux(base, error, tab, fath)
                noloop_aux(base, error, tab, moth)
            tab.set(i, Visit.VISITED)
        case Visit.BEING_VISITED:
            error(Driver.OwnAncestor(Driver.poi(base, i)))
        case Visit.VISITED:
            pass


def check_noloop(base: Driver.Base, error: Any) -> None:
    """Check for cycles in the genealogical tree."""
    tab = Driver.iper_marker(Driver.ipers(base), Visit.NOT_VISITED)
    Collection.iter(lambda i: noloop_aux(base, error, tab, i), Driver.ipers(base))


def check_noloop_for_person_list(
    base: Driver.Base, error: Any, person_list: List[Driver.Iper]
) -> None:
    """Check for cycles starting from a list of persons."""
    tab = Driver.iper_marker(Driver.ipers(base), Visit.NOT_VISITED)
    for person in person_list:
        noloop_aux(base, error, tab, person)


def topological_sort(base: Driver.Base, poi: Any) -> Marker[Driver.Iper, int]:
    """Return tab such that: i is ancestor of j => tab[i] > tab[j]."""
    persons = Driver.ipers(base)
    tab = Driver.iper_marker(Driver.ipers(base), 0)
    cnt = 0

    # Count children for each person
    for i in persons:
        a = poi(base, i)
        parents = Driver.get_parents(a)
        if parents is not None:
            cpl = Driver.foi(base, parents)
            ifath = Driver.get_father(cpl)
            imoth = Driver.get_mother(cpl)
            tab.set(ifath, tab.get(ifath) + 1)
            tab.set(imoth, tab.get(imoth) + 1)

    # Start from leaf vertices (persons without children)
    todo = [i for i in persons if tab.get(i) == 0]

    def loop(tval: int, curr_list: List[Driver.Iper]) -> None:
        nonlocal cnt
        if not curr_list:
            return

        new_list = []
        for i in curr_list:
            a = poi(base, i)
            tab.set(i, tval)
            cnt += 1
            parents = Driver.get_parents(a)
            if parents is not None:
                cpl = Driver.foi(base, parents)
                ifath = Driver.get_father(cpl)
                imoth = Driver.get_mother(cpl)
                tab.set(ifath, tab.get(ifath) - 1)
                tab.set(imoth, tab.get(imoth) - 1)
                if tab.get(ifath) == 0:
                    new_list.append(ifath)
                if tab.get(imoth) == 0:
                    new_list.append(imoth)

        loop(tval + 1, new_list)

    loop(0, todo)

    if cnt != Driver.nb_of_persons(base):
        check_noloop(
            base,
            lambda err: (
                raise_(TopologicalSortError(err.person))
                if isinstance(err, Driver.OwnAncestor)
                else None
            ),
        )

    return tab


# Global mark counter for unique identifiers
_mark = 0


def new_mark() -> int:
    """Generate a new unique mark."""
    global _mark
    _mark += 1
    return _mark


def insert_branch_len_rec(
    x: Tuple[int, int, Driver.Iper], lens: List[Tuple[int, int, List[Driver.Iper]]]
) -> List[Tuple[int, int, List[Driver.Iper]]]:
    """Recursively insert a branch length record."""
    length, n, ip = x
    if not lens:
        return [(length, n, [ip])]

    len1, n1, ipl1 = lens[0]
    if length == len1:
        n2 = n + n1
        if n < 0 or n1 < 0 or n2 < 0:
            n2 = -1
        return [(len1, n2, [ip] + ipl1)] + lens[1:]
    return [lens[0]] + insert_branch_len_rec(x, lens[1:])


def insert_branch_len(
    ip: Driver.Iper,
    lens: List[Tuple[int, int, List[Driver.Iper]]],
    branch: Tuple[int, int, List[Driver.Iper]],
) -> List[Tuple[int, int, List[Driver.Iper]]]:
    """Insert a branch length."""
    length, n, _ = branch
    return insert_branch_len_rec((length + 1, n, ip), lens)


def consang_of(p: Driver.Person) -> float:
    """Get the consanguinity coefficient of a person."""
    if Driver.get_consang(p) == Driver.no_consang:
        return 0.0
    return Driver.float_of_fix(Driver.get_consang(p))


def make_relationship_info(
    base: Driver.Base, tstab: Marker[Driver.Iper, int]
) -> RelationshipInfo:
    """Create a new relationship information structure."""
    phony_rel = Relationship()
    tab = Driver.iper_marker(Driver.ipers(base), phony_rel)
    return RelationshipInfo(tstab=tstab, reltab=tab, queue=[])


def relationship_and_links(
    base: Driver.Base, ri: RelationshipInfo, b: bool, ip1: Driver.Iper, ip2: Driver.Iper
) -> Tuple[float, List[Driver.Iper]]:
    """Calculate relationship between two persons and their common links."""
    if ip1 == ip2:
        return 1.0, []

    reltab = ri.reltab
    tstab = ri.tstab
    yes_inserted = new_mark()

    def reset(u: Driver.Iper) -> None:
        """Reset relationship information for a person."""
        tu = reltab.get(u)
        if tu == Relationship():
            reltab.set(u, Relationship(inserted=yes_inserted))
        else:
            tu.weight1 = 0.0
            tu.weight2 = 0.0
            tu.relationship = 0.0
            tu.lens1 = []
            tu.lens2 = []
            tu.inserted = yes_inserted
            tu.elim_ancestors = False
            tu.anc_stat1 = AncStat.MAYBE_ANC
            tu.anc_stat2 = AncStat.MAYBE_ANC

    qi = min(tstab.get(ip1), tstab.get(ip2))
    qmax = -1

    def insert(u: Driver.Iper) -> None:
        """Insert a person into the processing queue."""
        nonlocal qmax
        v = tstab.get(u)
        reset(u)

        # Ensure queue has enough capacity
        if v >= len(ri.queue):
            ri.queue.extend([[] for _ in range(v + 1 - len(ri.queue))])

        if qmax < 0:
            for i in range(qi, v):
                ri.queue[i] = []
            qmax = v
            ri.queue[v] = [u]
        else:
            if v > qmax:
                for i in range(qmax + 1, v + 1):
                    ri.queue[i] = []
                qmax = v
            ri.queue[v] = [u] + ri.queue[v]

    relationship = 0.0
    nb_anc1 = 1
    nb_anc2 = 1
    tops = []

    def treat_parent(ip_from: Driver.Iper, u: Relationship, y: Driver.Iper) -> None:
        """Process a parent in the relationship calculation."""
        nonlocal nb_anc1, nb_anc2
        if reltab.get(y).inserted != yes_inserted:
            insert(y)
        ty = reltab.get(y)
        p1 = half(u.weight1)
        p2 = half(u.weight2)

        if u.anc_stat1 == AncStat.IS_ANC and ty.anc_stat1 != AncStat.IS_ANC:
            ty.anc_stat1 = AncStat.IS_ANC
            nb_anc1 += 1
        if u.anc_stat2 == AncStat.IS_ANC and ty.anc_stat2 != AncStat.IS_ANC:
            ty.anc_stat2 = AncStat.IS_ANC
            nb_anc2 += 1

        ty.weight1 += p1
        ty.weight2 += p2
        ty.relationship += p1 * p2

        if u.elim_ancestors:
            ty.elim_ancestors = True
        if b and not ty.elim_ancestors:
            ty.lens1 = [
                branch
                for lens in u.lens1
                for branch in insert_branch_len(ip_from, ty.lens1, lens)
            ]
            ty.lens2 = [
                branch
                for lens in u.lens2
                for branch in insert_branch_len(ip_from, ty.lens2, lens)
            ]

    def treat_ancestor(u: Driver.Iper) -> None:
        """Process an ancestor in the relationship calculation."""
        nonlocal relationship, nb_anc1, nb_anc2
        tu = reltab.get(u)
        a = Driver.poi(base, u)
        contribution = (tu.weight1 * tu.weight2) - (
            tu.relationship * (1.0 + consang_of(a))
        )

        if tu.anc_stat1 == AncStat.IS_ANC:
            nb_anc1 -= 1
        if tu.anc_stat2 == AncStat.IS_ANC:
            nb_anc2 -= 1

        relationship += contribution

        if b and contribution != 0.0 and not tu.elim_ancestors:
            tops.append(u)
            tu.elim_ancestors = True

        parents = Driver.get_parents(a)
        if parents is not None:
            cpl = Driver.foi(base, parents)
            treat_parent(u, tu, Driver.get_father(cpl))
            treat_parent(u, tu, Driver.get_mother(cpl))

    # Initialize relationship calculation
    insert(ip1)
    insert(ip2)
    reltab.get(ip1).weight1 = 1.0
    reltab.get(ip2).weight2 = 1.0
    reltab.get(ip1).lens1 = [(0, 1, [])]
    reltab.get(ip2).lens2 = [(0, 1, [])]
    reltab.get(ip1).anc_stat1 = AncStat.IS_ANC
    reltab.get(ip2).anc_stat2 = AncStat.IS_ANC

    # Process ancestors until completion or exhaustion
    while qi <= qmax and nb_anc1 > 0 and nb_anc2 > 0:
        for ancestor in ri.queue[qi]:
            treat_ancestor(ancestor)
        qi += 1

    return half(relationship), tops


def raise_(ex: Exception) -> None:
    """Helper function to raise exceptions in lambda functions."""
    raise ex


class TopologicalSortError(Exception):
    """Exception raised when topological sort fails due to cycles."""

    def __init__(self, person: Driver.Person):
        self.person = person
        super().__init__(f"Topological sort failed due to cycle at person {person}")
