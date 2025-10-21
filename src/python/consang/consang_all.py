"""
Consanguinity computation for GeneWeb databases.
Original copyright (c) 1998-2007 INRIA
"""

import sys
from typing import Tuple, Optional, Callable, Any

from lib.db_pickle.database.base import PickleBase

# from geneweb_db import driver, Collection, Gutil
# from geneweb_db.adef import fix_of_float, no_consang
from .consang import (
    topological_sort,
    make_relationship_info,
    relationship_and_links,
)
from lib.util import progr_bar as ProgrBar
from lib.db_pickle.database import driver
from lib.db_pickle import gutil, collection
from lib.defs import adef

# from ..lib.db_pickle import adef


def relationship(base: Any, tab: Any, ip1: int, ip2: int) -> float:
    """Calculate relationship coefficient between two individuals."""
    return relationship_and_links(base, tab, False, ip1, ip2)[0]


def trace(verbosity: int, cnt: int, max_cnt: int) -> None:
    """Display progress information based on verbosity level."""
    if verbosity >= 2:
        print(f"\r{cnt:7d}", end="", flush=True, file=sys.stderr)
    elif verbosity >= 1:
        ProgrBar.run(max_cnt - cnt, max_cnt)


def consang_array(
    base: Any,
) -> Tuple[
    Callable[[int], Optional[int]],  # fget
    Callable[[int], float],  # cget
    Callable[[int, float], None],  # cset
    bool,  # patched reference
]:
    """Create functions for accessing and modifying consanguinity data."""
    patched = False

    def fget(i: int) -> Optional[int]:
        return driver.get_parents(driver.poi(base, i))

    def cget(i: int) -> float:
        return driver.get_consang(driver.poi(base, i))

    def cset(i: int, v: float) -> None:
        nonlocal patched
        patched = True
        person = driver.poi(base, i)
        asc = driver.gen_ascend_of_person(person)
        asc.consang = v
        driver.patch_ascend(base, i, asc)

    return fget, cget, cset, patched


def compute(base: PickleBase, from_scratch: bool = False, verbosity: int = 2) -> bool:
    """
    Compute consanguinity values for all individuals in the database.

    Args:
        base: The database to process
        from_scratch: Whether to recompute all values
        verbosity: Output verbosity level (0-2)

    Returns:
        bool: Whether any values were changed
    """
    import sys

    # driver.load_ascends_array(base)
    # driver.load_couples_array(base)
    fget, cget, cset, patched = consang_array(base)

    try:
        # Create topological sort and relationship info
        ts = topological_sort(base, driver.poi)
        tab = make_relationship_info(base, ts)

        persons = driver.ipers(base)
        families = driver.ifams(base)
        consang_tab = driver.ifam_marker(families, adef.no_consang)

        # Initialize counts and process existing values
        cnt = 0
        for i in persons:
            if from_scratch:
                cset(i, adef.no_consang)
                cnt += 1
            else:
                cg = cget(i)
                ifam = fget(i)
                if ifam is not None:
                    consang_tab[ifam] = cg
                if cg == adef.no_consang:
                    cnt += 1

        # Progress display
        max_cnt = cnt
        most = None
        if verbosity >= 1:
            print(f"To do: {max_cnt} persons", file=sys.stderr)
        if max_cnt != 0:
            if verbosity >= 2:
                print("Computing consanguinity...", end="", flush=True, file=sys.stderr)
            elif verbosity >= 1:
                ProgrBar.start()

        # Main computation loop
        running = True
        while running:
            running = False
            for i in persons:
                if cget(i) != adef.no_consang:
                    continue
                ifam = fget(i)
                if ifam is None:
                    trace(verbosity, cnt, max_cnt)
                    cnt -= 1
                    cset(i, adef.fix_of_float(0.0))
                    continue
                pconsang = consang_tab[ifam]
                if pconsang is None:
                    continue
                if pconsang != adef.no_consang:
                    trace(verbosity, cnt, max_cnt)
                    cnt -= 1
                    cset(i, adef.float_of_fix(pconsang))
                    continue
                cpl = driver.foi(base, ifam)
                ifath = driver.get_father(cpl)
                imoth = driver.get_mother(cpl)

                if not (
                    ifath is not None
                    and imoth is not None
                    and cget(ifath) != adef.no_consang
                    and cget(imoth) != adef.no_consang
                ):
                    running = True
                    continue
                consang = relationship(base, tab, ifath, imoth)
                trace(verbosity, cnt, max_cnt)
                cnt -= 1
                cg = adef.fix_of_float(consang)
                cset(i, cg)
                consang_tab[ifam] = cg

                if verbosity >= 2:
                    if most is None or cg > cget(most):
                        print(
                            f"\nMax consanguinity {consang} for "
                            f"{gutil.designation(base, driver.poi(base, i))}... ",
                            end="",
                            flush=True,
                            file=sys.stderr,
                        )
                        most = i

        if max_cnt != 0:
            if verbosity >= 2:
                print(" done   ", file=sys.stderr)
            elif verbosity >= 1:
                ProgrBar.finish()

    except KeyboardInterrupt:
        if verbosity > 0:
            print(file=sys.stderr)

    if patched:
        # driver.commit_patches(base)
        driver.sync(base)

    return patched
