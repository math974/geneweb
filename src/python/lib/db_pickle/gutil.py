from .database import driver, PickleBase

# let designation base p =
#   let first_name = Driver.p_first_name base p in
#   let nom = Driver.p_surname base p in
#   first_name ^ "." ^ string_of_int (Driver.get_occ p) ^ " " ^ nom


def designation(base: PickleBase, p: driver.DriverPerson) -> str:
    if p is not None:
        first_name = driver.p_first_name(base, p)
        nom = driver.p_surname(base, p)
        return f"{first_name}.{driver.get_occ(p)} {nom}"
    return "<unknown>.0 <unknown>"
