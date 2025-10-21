from dataclasses import dataclass
from typing import Generic, TypeVar, Union
from ..db_pickle.models.relations import GenCouple

T = TypeVar("T")
fix = int


@dataclass
class GenParents(Generic[T]):
    parent: list[T]


# let float_of_fix x = float x /. 1000000.0
def float_of_fix(x: int) -> float:
    return float(x) / 1000000.0


# let fix_of_float x = truncate ((x *. 1000000.0) +. 0.5)
def fix_of_float(x: float) -> int:
    return int(x * 1000000.0 + 0.5)


no_consang = fix(-1)


# let parent_array cpl =
#   if Obj.size (Obj.repr cpl) = 2 then [| cpl.father; cpl.mother |]
#   else (Obj.magic cpl).parent
def parent_array(cpl: Union[GenCouple, GenParents[T]]):
    if isinstance(cpl, GenCouple):
        return [cpl.father, cpl.mother]
    return cpl.parent
