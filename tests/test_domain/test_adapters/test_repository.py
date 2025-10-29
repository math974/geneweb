"""Tests pour MessagePackBaseRepository - 20 lignes max par fonction"""
import sys
from pathlib import Path
import pytest
try:
    import msgpack
except Exception:
    msgpack = None
    pytest.skip("msgpack non installé - skip repository tests", allow_module_level=True)

# PYTHONPATH -> src/python
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src" / "python"))

from gwd.adapters.database.base_repository import MessagePackBaseRepository
from gwd.domain.entities.person import Person


def make_msgpack_base(tmpdir: Path, base_name: str):
    persons = [
        {"id": 1, "first_name": "Jean", "surname": "Dupont"},
        {"id": 2, "first_name": "Marie", "surname": "Martin"},
    ]
    data = {"title": "Base Test", "persons": persons}
    file_path = tmpdir / f"{base_name}.msgpack"
    file_path.write_bytes(msgpack.packb(data, use_bin_type=True))
    return file_path


def test_load_base_and_get_person(tmp_path):
    base_name = "test"
    make_msgpack_base(Path(tmp_path), base_name)
    repo = MessagePackBaseRepository(str(tmp_path))
    base = repo.load_base(base_name)
    assert base is not None
    person = repo.get_person_by_id(base_name, 1)
    assert isinstance(person, Person)
    assert person.first_name == "Jean"


def test_search_persons(tmp_path):
    base_name = "test"
    make_msgpack_base(Path(tmp_path), base_name)
    repo = MessagePackBaseRepository(str(tmp_path))
    results = repo.search_persons(base_name, "Jean")
    assert len(results) == 1
    assert results[0].surname == "Dupont"
