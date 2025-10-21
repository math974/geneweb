"""Progress bar utility module.

Original OCaml module.
"""

import sys
import time
from dataclasses import dataclass

from typing import TextIO


# Bar configuration constants
SIZE = 60
DRAW_REP = 5
DRAW = "|/-\\"
DRAW_LEN = len(DRAW)
PB_CNT = SIZE * DRAW_REP * DRAW_LEN
DEFAULT_WIDTH = 60
DEFAULT_EMPTY = "."
DEFAULT_FULL = "#"


@dataclass
class ProgressBar:
    """Progress bar configuration and state."""

    ppf: TextIO  # Format.formatter equivalent in Python
    width: int
    empty: str
    full: str
    disabled: bool
    last_output: float = 0.0

    def progress(self, current: int, total: int) -> None:
        """Update the progress bar."""
        if not self.disabled:
            now = time.time()
            if now - self.last_output < 0.2:
                return

            self.last_output = now
            filled = current * self.width // total
            bar = (self.full * filled) + (self.empty * (self.width - filled))
            percentage = current * 100 // total

            print(f"\r[{bar}] {percentage}%", end="", file=self.ppf)
            self.ppf.flush()

    def finish(self) -> None:
        """Complete the progress bar."""
        print(f"\r[{self.full * self.width}] 100%", file=self.ppf)
        self.ppf.flush()


def create_progress_bar(
    ppf: TextIO = sys.stderr,
    *,
    width: int = DEFAULT_WIDTH,
    empty: str = DEFAULT_EMPTY,
    full: str = DEFAULT_FULL,
    disabled: bool = False,
) -> ProgressBar:
    """Create a new progress bar instance."""
    return ProgressBar(
        ppf=ppf, width=width, empty=empty, full=full, disabled=disabled, last_output=0.0
    )


# Legacy style progress bar functions
empty_char = DEFAULT_EMPTY
full_char = DEFAULT_FULL


def start() -> None:
    """Initialize the legacy progress bar."""
    print(empty_char * SIZE, end="\r", file=sys.stderr)
    sys.stderr.flush()


def run(cnt: int, max_cnt: int) -> None:
    """Update the legacy progress bar."""
    pb_cnt_local = SIZE * DRAW_LEN if max_cnt < PB_CNT else PB_CNT

    already_disp = cnt * SIZE // max_cnt
    to_disp = (cnt + 1) * SIZE // max_cnt

    # Update the bar
    for _ in range(already_disp + 1, to_disp + 1):
        print(full_char, end="", file=sys.stderr)

    # Update the spinner
    already_disp = cnt * pb_cnt_local // max_cnt
    to_disp = (cnt + 1) * pb_cnt_local // max_cnt

    if cnt == max_cnt - 1:
        print(" \b", end="", file=sys.stderr)
    elif to_disp > already_disp:
        k = to_disp % DRAW_LEN
        k = DRAW_LEN + k if k < 0 else k
        print(f"{DRAW[k]}\b", end="", file=sys.stderr)

    sys.stderr.flush()


def suspend() -> None:
    """Suspend the legacy progress bar."""
    print(f"{full_char}", file=sys.stderr)
    sys.stderr.flush()


def restart(cnt: int, max_cnt: int) -> None:
    """Restart the legacy progress bar from a given position."""
    start()
    for i in range(cnt + 1):
        run(i, max_cnt)


def finish() -> None:
    """Complete the legacy progress bar."""
    print(file=sys.stderr)
    sys.stderr.flush()
