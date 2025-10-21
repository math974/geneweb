from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Callable, Optional, TypeVar

from lib.db_pickle.core.types import Istr
from lib.db_pickle.database.base_data import PickleBaseData
from lib.db_pickle.models.person import GenPerson
from lib.db_pickle.models.family import GenFamily
from lib.db_pickle.models.family import GenFamily
from lib.db_pickle.models.relations import (
    GenAscend,
    GenUnion,
    GenCouple,
    GenDescend,
)
from lib.db_pickle import collection
from lib.defs import adef

from .base import open_database, PickleBase
from lib.util import mutil


class Iper(int):
    @staticmethod
    def is_dummy(iper: int) -> bool:
        """Check if the given person ID is a dummy"""
        return iper == -1


@dataclass
class DriverPerson:
    """Person representation"""

    base: PickleBaseData
    iper: int
    p: Optional[GenPerson]
    a: Optional[GenAscend]
    u: Optional[GenUnion]


@contextmanager
def with_database(path: str):
    """Context manager to open and close a pickle database"""
    db = open_database(path)

    yield db


def sync(db: PickleBase) -> None:
    """Synchronize database to disk"""
    import pickle

    with open(f"{db.data.bdir}.pkl", "wb") as f:
        pickle.dump(db.data, f)


def bname(db: PickleBase) -> str:
    """Get base name of the database"""
    return db.bname()


def nb_of_persons(db: PickleBase) -> int:
    """Get number of persons in the database"""
    return db.nb_of_persons()


def nb_of_families(db: PickleBase) -> int:
    """Get number of families in the database"""
    return db.nb_of_families()


def poi(db: PickleBaseData, iper: int) -> DriverPerson:
    """Get person by ID"""
    if Iper.is_dummy(iper):
        # return empty_person(db, iper)
        return DriverPerson(base=db, iper=iper, p=None, a=None, u=None)
    return DriverPerson(base=db, iper=iper, p=None, a=None, u=None)


def sou(base: PickleBase, istr: Istr) -> str:
    """Get string by ID"""
    raise NotImplementedError(
        "sou function not implemented because there is no use for it since we load"
        " strings from gedcom and not geneweb database anymore"
    )
    # if istr in base.data.strings:
    #     return base.data.strings[istr]
    # return ""


T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


def cache(
    f: Callable[[T], Optional[U]],
    a: T,
    get: Callable[[V], Optional[U]],
    set: Callable[[V, Optional[U]], None],
    x: V,
) -> U:
    """Cache data for a person"""
    match get(x):
        case None:
            v = f(a)
            set(x, v)
            return v
        case _ as v:
            return v


def cache_per(f: Callable[[GenPerson], T], p: DriverPerson) -> T:
    """Cache person data"""
    base = p.base
    iper = p.iper
    return f(
        cache(
            lambda iper: base.persons.get(iper),
            iper,
            lambda p: p.p,
            lambda p, v: setattr(p, "p", v),
            p,
        )
    )


def cache_asc(f: Callable[[GenAscend], T], p: DriverPerson) -> T:
    """Cache ascend data"""
    base = p.base
    iper = p.iper
    print(f"{type(p)=}")
    return f(
        cache(
            lambda iper: base.ascends.get(iper),
            iper,
            lambda p: p.a,
            lambda p, v: setattr(p, "a", v),
            p,
        )
    )


def cache_uni(f: Callable[[GenUnion], T], p: DriverPerson) -> T:
    """Cache union data"""
    base = p.base
    iper = p.iper
    return f(
        cache(
            lambda iper: base.unions.get(iper),
            iper,
            lambda p: p.u,
            lambda p, v: setattr(p, "u", v),
            p,
        )
    )


# let get_access = cache_per (fun p -> p.Def.access)
# let get_aliases = cache_per (fun p -> p.Def.aliases)
# let get_baptism = cache_per (fun p -> p.Def.baptism)
def get_baptism(p: DriverPerson):
    """Get the baptism event of a person"""
    return cache_per(lambda p: p.baptism, p)


# let get_baptism_note = cache_per (fun p -> p.Def.baptism_note)
# let get_baptism_place = cache_per (fun p -> p.Def.baptism_place)
# let get_baptism_src = cache_per (fun p -> p.Def.baptism_src)
# let get_birth = cache_per (fun p -> p.Def.birth)
def get_birth(p: DriverPerson):
    """Get the birth event of a person"""
    return cache_per(lambda p: p.birth, p)


# let get_birth_note = cache_per (fun p -> p.Def.birth_note)
# let get_birth_place = cache_per (fun p -> p.Def.birth_place)
# let get_birth_src = cache_per (fun p -> p.Def.birth_src)
# let get_burial = cache_per (fun p -> p.Def.burial)
def get_burial(p: DriverPerson):
    """Get the burial event of a person"""
    return cache_per(lambda p: p.burial, p)


# let get_burial_note = cache_per (fun p -> p.Def.burial_note)
# let get_burial_place = cache_per (fun p -> p.Def.burial_place)
# let get_burial_src = cache_per (fun p -> p.Def.burial_src)
# let get_consang = cache_asc (fun a -> a.Def.consang)
def get_consang(p: DriverPerson) -> float:
    """Get the consanguinity value of a person"""
    return cache_asc(lambda a: a.consang, p)


# let get_death = cache_per (fun p -> p.Def.death)
def get_death(p: DriverPerson):
    """Get the death event of a person"""
    return cache_per(lambda p: p.death, p)


# let get_death_note = cache_per (fun p -> p.Def.death_note)
# let get_death_place = cache_per (fun p -> p.Def.death_place)
# let get_death_src = cache_per (fun p -> p.Def.death_src)
# let get_family = cache_uni (fun u -> u.Def.family)
def get_family(p: DriverPerson) -> list[int]:
    """Get the family IDs of a person"""
    return cache_uni(lambda u: u.family, p)


# let get_first_name = cache_per (fun p -> p.Def.first_name)
def get_first_name(p: DriverPerson) -> str:
    """Get the first name string ID of a person"""
    return cache_per(lambda p: p.first_name, p)


# let get_first_names_aliases = cache_per (fun p -> p.Def.first_names_aliases)
# let get_image = cache_per (fun p -> p.Def.image)
# let get_iper = cache_per (fun p -> p.Def.key_index)
def get_iper(p: DriverPerson) -> int:
    """Get the person ID of a person"""
    return cache_per(lambda p: p.key_index, p)


# let get_notes = cache_per (fun p -> p.Def.notes)
def get_notes(p: DriverPerson) -> str:
    """Get the notes of a person"""
    return cache_per(lambda p: p.notes, p)


# let get_occ = cache_per (fun p -> p.Def.occ)
def get_occ(p: DriverPerson) -> int:
    """Get the occurrence number of a person"""
    return cache_per(lambda p: p.occ, p)


# let get_occupation = cache_per (fun p -> p.Def.occupation)
# let get_parents = cache_asc (fun a -> a.Def.parents)
def get_parents(p: DriverPerson):
    """Get the parents of a person"""
    return cache_asc(lambda a: a.parents, p)


# let get_pevents = cache_per (fun p -> p.Def.pevents)
# let get_psources = cache_per (fun p -> p.Def.psources)
# let get_public_name = cache_per (fun p -> p.Def.public_name)
# let get_qualifiers = cache_per (fun p -> p.Def.qualifiers)
# let get_related = cache_per (fun p -> p.Def.related)
# let get_rparents = cache_per (fun p -> p.Def.rparents)
# let get_sex = cache_per (fun p -> p.Def.sex)
def get_sex(p: DriverPerson):
    """Get the sex of a person"""
    return cache_per(lambda p: p.sex, p)


# let get_surname = cache_per (fun p -> p.Def.surname)
def get_surname(p: DriverPerson) -> str:
    """Get the surname string ID of a person"""
    return cache_per(lambda p: p.surname, p)


# let get_surnames_aliases = cache_per (fun p -> p.Def.surnames_aliases)
# let get_titles = cache_per (fun p -> p.Def.titles)
def get_titles(p: DriverPerson):
    """Get the titles of a person"""
    return cache_per(lambda p: p.titles, p)


# (** Families *)


# type family = {
#   base : base;
#   ifam : ifam;
#   mutable f : (iper, ifam, istr) Def.gen_family option;
#   mutable c : iper Def.gen_couple option;
#   mutable d : iper Def.gen_descend option;
# }
@dataclass
class DriverFamily:
    """Family representation"""

    base: PickleBase
    ifam: int
    f: Optional[GenFamily]  # GenFamily
    c: Optional[GenCouple]  # GenCouple
    d: Optional[GenDescend]  # GenDescend


# let cache_fam f ({ base; ifam; _ } as fam) =
#   f (cache base.data.families.get ifam (fun f -> f.f) (fun f v -> f.f <- v) fam)
def cache_fam(f: Callable[[GenFamily], T], fam: DriverFamily) -> T:
    """Cache family data"""
    base = fam.base
    ifam = fam.ifam
    return f(
        cache(
            lambda ifam: base.data.families.get(ifam),
            ifam,
            lambda f: f.f,
            lambda f, v: setattr(f, "f", v),
            fam,
        )
    )


# let cache_cpl f ({ base; ifam; _ } as fam) =
#   f (cache base.data.couples.get ifam (fun f -> f.c) (fun f v -> f.c <- v) fam)
def cache_cpl(f: Callable[[GenCouple], T], fam: DriverFamily) -> T:
    """Cache couple data"""
    base = fam.base
    ifam = fam.ifam
    return f(
        cache(
            lambda ifam: base.data.couples.get(ifam),
            ifam,
            lambda f: f.c,
            lambda f, v: setattr(f, "c", v),
            fam,
        )
    )


# let cache_des f ({ base; ifam; _ } as fam) =
#   f (cache base.data.descends.get ifam (fun f -> f.d) (fun f v -> f.d <- v) fam)
def cache_des(f: Callable[[GenDescend], T], fam: DriverFamily) -> T:
    """Cache descend data"""
    base = fam.base
    ifam = fam.ifam
    return f(
        cache(
            lambda ifam: base.data.descends.get(ifam),
            ifam,
            lambda f: f.d,
            lambda f, v: setattr(f, "d", v),
            fam,
        )
    )


# let gen_couple_of_family = cache_cpl (fun c -> c)
def get_couple(fam: DriverFamily) -> GenCouple:
    """Get the couple of a family"""
    return cache_cpl(lambda c: c, fam)


# let gen_descend_of_family = cache_des (fun d -> d)
def get_descend(fam: DriverFamily) -> GenDescend:
    """Get the descend of a family"""
    return cache_des(lambda d: d, fam)


# let gen_family_of_family = cache_fam (fun f -> f)
def get_family_record(fam: DriverFamily) -> GenFamily:
    """Get the family record of a family"""
    return cache_fam(lambda f: f, fam)


# let get_children = cache_des (fun d -> d.Def.children)
def get_children(fam: DriverFamily):
    """Get the children IDs of a family"""
    return cache_des(lambda d: d.children, fam)


# let get_comment = cache_fam (fun f -> f.Def.comment)
# let get_ifam = cache_fam (fun f -> f.Def.fam_index)
def get_ifam(fam: DriverFamily) -> int:
    """Get the family ID of a family"""
    return cache_fam(lambda f: f.fam_index, fam)


# (* let get_divorce = cache_fam (fun f -> f.Def.divorce) *)
def get_divorce(fam: DriverFamily):
    """Get the divorce event of a family"""
    return cache_fam(lambda f: f.divorce, fam)


# let get_father = cache_cpl (fun c -> Adef.father c)
def get_father(fam: DriverFamily) -> Optional[int]:
    """Get the father ID of a family"""
    return cache_cpl(lambda c: c.father, fam)


# let get_fevents = cache_fam (fun f -> f.Def.fevents)
# let get_fsources = cache_fam (fun f -> f.Def.fsources)
# let get_marriage = cache_fam (fun f -> f.Def.marriage)
def get_marriage(fam: DriverFamily):
    """Get the marriage event of a family"""
    return cache_fam(lambda f: f.marriage, fam)


# let get_marriage_note = cache_fam (fun f -> f.Def.marriage_note)
# let get_marriage_place = cache_fam (fun f -> f.Def.marriage_place)
# let get_marriage_src = cache_fam (fun f -> f.Def.marriage_src)
# let get_mother = cache_cpl (fun c -> Adef.mother c)
def get_mother(fam: DriverFamily) -> Optional[int]:
    """Get the mother ID of a family"""
    return cache_cpl(lambda c: c.mother, fam)


# let get_origin_file = cache_fam (fun f -> f.Def.origin_file)
# let get_parent_array = cache_cpl (fun c -> Adef.parent_array c)
def get_parent_array(fam: DriverFamily) -> list[int]:
    """Get the parent array of a family"""
    return cache_cpl(lambda c: adef.parent_array(c), fam)


# let get_relation = cache_fam (fun f -> f.Def.relation)
# let get_witnesses = cache_fam (fun f -> f.Def.witnesses)
# let empty_person = Mutil.empty_person Istr.empty Istr.empty
def empty_person(base: PickleBaseData, iper: int) -> GenPerson:
    """Create an empty person"""
    return mutil.empty_person("?", per_index=iper)


# let no_person ip = Def.{ empty_person with key_index = ip }
def no_person(ip: int) -> GenPerson:
    """Create a no-person placeholder"""
    return GenPerson(key_index=ip)


# let no_ascend = Def.{ parents = None; consang = Adef.no_consang }
def no_ascend() -> GenAscend:
    """Create a no-ascend placeholder"""
    return GenAscend(consang=-1.0)


# let no_union = Def.{ family = [||] }
def no_union() -> GenUnion:
    """Create a no-union placeholder"""
    return GenUnion()


def no_family(ifam: int) -> GenFamily:
    """Create a no-family placeholder"""
    return GenFamily(fam_index=ifam)


def empty_family(base: PickleBase, ifam: int) -> GenFamily:
    """Create an empty family"""
    return mutil.empty_family(fam_index=ifam)


def foi(base: PickleBase, ifam: int) -> DriverFamily:
    """Get family by ID"""
    return DriverFamily(base=base, ifam=ifam, f=None, c=None, d=None)


def ipers(base: PickleBase) -> list[int]:
    """Get all person IDs in the database"""
    return list(base.data.persons.keys())


# let ifams ?(select = fun _ -> true) base =
#   Collection.make ~len:(nb_of_families base) (fun i ->
#       if select i then
#         if get_ifam (foi base i) = Ifam.dummy then None else Some i
#       else None)
def ifams(
    base: PickleBase, select: Callable[[int], bool] = lambda x: True
) -> list[int]:
    """Get all family IDs in the database, optionally filtered by a selection function"""
    result = []
    for ifam in range(nb_of_families(base)):
        if select(ifam) and get_ifam(foi(base, ifam)) != -1:
            result.append(ifam)
    return result


def p_first_name(base: PickleBase, p: DriverPerson) -> str:
    mutil.nominative(get_first_name(p))


def p_surname(base: PickleBase, p: DriverPerson) -> str:
    """Get the surname string ID of a person"""
    return mutil.nominative(get_surname(p))


def ifam_marker(families: list[int], default: T) -> collection.Marker[int, T]:
    """Create a marker dictionary for families with a default value"""
    return collection.Marker(lambda x: int(x), len(families), default)
