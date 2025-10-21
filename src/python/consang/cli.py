#!/usr/bin/env python3

"""
Consanguinity computation tool for GeneWeb databases.
Original copyright (c) 1998-2007 INRIA
"""

from dataclasses import dataclass
import argparse
import os
import sys
from typing import Any, Optional

# from geneweb_db import Outbase, Driver, Gutil
# from geneweb_db.consang import ConsangAll, Consang, TopologicalSortError
# from geneweb_db.mutil import verbose, lock_file
# from geneweb_db.secure import set_base_dir
# from geneweb_db.lock import Lock, pp_exception
from . import consang_all
from lib.util.lock import lock as global_lock
from lib.db_pickle.database import driver


@dataclass
class ArgumentParser:
    file_name: str
    verbosity: int = 2
    fast: bool = False
    scratch: bool = False
    save_mem: bool = False
    no_lock: bool = False


def main() -> None:
    """Main entry point for the consang command line tool."""

    parser = argparse.ArgumentParser()

    parser.add_argument("file_name", help="Database file name")

    parser.add_argument(
        "-q",
        dest="verbosity",
        action="store_const",
        const=1,
        default=2,
        help="quiet mode",
    )

    parser.add_argument(
        "-qq",
        dest="verbosity",
        action="store_const",
        const=0,
        default=2,
        help="very quiet mode",
    )

    parser.add_argument(
        "-fast", action="store_true", help="faster, but use more memory"
    )

    parser.add_argument("-scratch", action="store_true", help="from scratch")

    parser.add_argument(
        "-mem",
        action="store_true",
        help="Save memory, but slower when rewriting database",
        dest="save_mem",
    )

    parser.add_argument(
        "-nolock", action="store_true", help="do not lock database", dest="no_lock"
    )

    args: ArgumentParser = parser.parse_args()

    if args.verbosity == 0:
        print("Quiet mode activated.")
        # verbose.value = False

    # Set up paths and locks
    print("Setting base directory...")
    # set_base_dir(os.path.dirname(args.file_name))
    print(f"Lock file... {args.file_name}")
    # lock_file_path = lock_file(args.file_name)

    def on_lock_error(exn: Exception, bt: Any) -> None:
        """Handle lock-related errors"""
        print("Lock error encountered.")
        # print(pp_exception((exn, bt)), file=sys.stderr)
        sys.exit(2)

    def process_database(base: PickleBase) -> None:
        """Process the database with the given options"""
        if args.fast:
            # Preload arrays for faster access
            print("Driver.load_persons_array(base)")
            print("Driver.load_families_array(base)")
            print("Driver.load_ascends_array(base)")
            print("Driver.load_unions_array(base)")
            print("Driver.load_couples_array(base)")
            print("Driver.load_descends_array(base)")
            print("Driver.load_strings_array(base)")

        try:
            print("ConsangAll.compute(base, ...)")
            if consang_all.compute(
                base, verbosity=args.verbosity, from_scratch=args.scratch
            ):
                driver.sync(base)
        except Exception as e:  # TopologicalSortError as e:
            p = e.args[0]  # Get the person causing the error
            print(
                f"\nError: loop in database, {"Gutil.designation(base, p)"} is his/her own ancestor."
            )
            sys.exit(2)

    # Main execution with lock control
    print("Acquiring lock and processing database...")
    # with Lock(on_exn=on_lock_error, wait=True, lock_file=lock_file_path):
    with global_lock:
        with driver.with_database(args.file_name) as base:
            # if args.save_mem:
            #     Outbase.save_mem = True

            print("Printing initial consanguinity values...")
            print("Fetching persons...")
            persons = base.persons
            print(f"{type(persons)=} {len(persons)=}")
            print("Iterating over persons...")
            for iper, person in persons.items():
                print("Getting person info...")
                dp = driver.poi(base, iper)
                print(f"{dp.iper=}")
                print(
                    f"{person.first_name} {person.surname}({person.key_index}): consang={driver.get_consang(dp)}"
                )
            print("\nProcessing database for consanguinity computation...")
            process_database(base)
            print("saving changes...")
            driver.sync(base)
            print("Done.\n")
        with driver.with_database(args.file_name) as base:
            print("Final consanguinity values:")
            persons = base.persons()
            for iper, person in persons.items():
                dp = driver.poi(base, iper)
                print(
                    f"{person.first_name} {person.surname}({person.key_index}): consang={driver.get_consang(dp)}"
                )


if __name__ == "__main__":
    main()
