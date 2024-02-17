"""Make a word search."""

import functools
import operator
import random
import string
from collections.abc import Callable, Iterable, Iterator
from contextlib import suppress
from itertools import batched
from typing import Annotated, Final, Literal, ParamSpec, TypeVar, cast, overload

Direction = Literal[
    "up", "down", "left", "right", "down-left", "down-right", "up-left", "up-right"
]
GridIndex = tuple[Annotated[int, "row"], Annotated[int, "col"]]
StartingPositionGenerator = Callable[[int, int, int], Iterator[GridIndex]]
Operator = Callable[[int, int], int]
ALPHABET = tuple(string.ascii_uppercase)
STEP_OPERATORS: Final[dict[Direction, tuple[Operator | None, Operator | None]]] = {
    "up": (operator.sub, None),
    "down": (operator.add, None),
    "left": (None, operator.sub),
    "right": (None, operator.add),
    "down-left": (operator.add, operator.sub),
    "down-right": (operator.add, operator.add),
    "up-left": (operator.sub, operator.sub),
    "up-right": (operator.sub, operator.add),
}
DIRECTION_OPPOSITES: Final[dict[Direction, Direction]] = {
    "up": "down",
    "down": "up",
    "left": "right",
    "right": "left",
    "down-left": "up-right",
    "down-right": "up-left",
    "up-left": "down-right",
    "up-right": "down-left",
}
STARTING_POSITION_GENERATORS: Final[dict[Direction, StartingPositionGenerator]] = {
    "right": lambda w, h, length: (
        (r, c) for r in range(h) for c in range(w - length + 1)
    ),
    "left": lambda w, h, length: (
        (r, c) for r in range(h) for c in range(length - 1, w)
    ),
    "down": lambda w, h, length: (
        (r, c) for r in range(h - length + 1) for c in range(w)
    ),
    "up": lambda w, h, length: ((r, c) for r in range(length - 1, h) for c in range(w)),
    "up-right": lambda w, h, length: (
        (r, c) for r in range(length - 1, h) for c in range(w - length + 1)
    ),
    "up-left": lambda w, h, length: (
        (r, c) for r in range(length - 1, h) for c in range(length - 1, w)
    ),
    "down-right": lambda w, h, length: (
        (r, c) for r in range(h - length + 1) for c in range(w - length + 1)
    ),
    "down-left": lambda w, h, length: (
        (r, c) for r in range(h - length + 1) for c in range(length - 1, w)
    ),
}

P = ParamSpec("P")
R = TypeVar("R")


def cache(func: Callable[P, R]) -> Callable[P, R]:
    """Typed @functools.cache wrapper."""

    @functools.wraps(func)
    @functools.cache
    def _wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)

    return cast(Callable[P, R], _wrapper)


class PlacementError(Exception):
    """Raised when a word cannot be placed on the grid."""


class WordSearch:
    """
    A word search, like the one that that sub for Mrs. Morris's class yelled at me for
    striking through the words instead of circling them in fourth grade.
    """

    def __init__(
        self,
        bank: Iterable[str] | None = None,
        width: int | None = None,
        height: int | None = None,
        max_attempts: int = 300,
        title: str | None = None,
        autoexpand: bool = True,
        _fill_empty: bool = True,
        _connection_coefficient: float | None = None,  # chance of trying to intersect
    ) -> None:
        """Create a word search of a specified size from a bank of terms."""
        bank = [] if bank is None else list(bank)
        self.bank = [word.upper() for word in bank]
        if width is None or height is None:
            width, height = self._infer_dimensions()
        self.grid = self._make_grid(width, height)
        self.width = width
        self.height = height
        self.title = title
        self._case_sensitive_bank = bank
        self._connection_coefficient = _connection_coefficient
        self._placed_letters: dict[str, dict[GridIndex, set[Direction]]] = {}
        if len(bank) == 0:
            return None
        if not autoexpand:
            self.populate_grid(max_attempts)
        else:
            max_len = max(len(word) for word in self.bank)
            if max_len > self.width:
                self.width = max_len
            if max_len > self.height:
                self.height = max_len
            success = False
            while not success:
                try:
                    self.populate_grid(3)
                    success = True
                except (PlacementError, ValueError, IndexError):
                    self.width += 1
                    self.height += 1
                    self.grid = self._make_grid(self.width, self.height)
        if _fill_empty:
            self._fill_empty_with_random()

    def __repr__(self) -> str:
        """Represent WordSearch as a string."""
        result = ""
        for row in self.grid:
            for char in row:
                result += f" {char}" if char is not None else " -"
            result += " \n"
        return result

    @overload
    def __getitem__(self, idx: int) -> list[str | None]: ...

    @overload
    def __getitem__(self, idx: GridIndex) -> str | None: ...

    def __getitem__(self, idx: int | GridIndex) -> list[str | None] | str | None:
        """Fetch a row or cell."""
        return self.grid[idx[0]][idx[1]] if isinstance(idx, tuple) else self.grid[idx]

    @overload
    def __setitem__(self, idx: int, val: list[str | None]) -> None: ...

    @overload
    def __setitem__(self, idx: GridIndex, val: str | None) -> None: ...

    def __setitem__(
        self, idx: int | GridIndex, val: list[str | None] | str | None
    ) -> None:
        """Set a row or cell."""
        if isinstance(idx, tuple) and not isinstance(val, list):
            self.grid[idx[0]][idx[1]] = val
        elif isinstance(idx, int) and isinstance(val, list):
            self.grid[idx] = val
        else:
            raise ValueError(
                "must set `int` index to `list[str | None]` or `GridIndex` "
                "to `str | None`"
            )

    @property
    def connection_coefficient(self) -> float:
        """Chance of trying to attach a word to an existing word vs. place randomly."""
        if self._connection_coefficient is not None:
            return self._connection_coefficient
        coefficient = sum(len(word) for word in self.bank) / (self.width * self.height)
        return coefficient if coefficient < 0.85 else 0.85

    @connection_coefficient.setter
    def connection_coefficient(self, value: float) -> None:
        """Set connection coefficient to a value."""
        self._connection_coefficient = value

    def _infer_dimensions(self) -> tuple[int, int]:
        """Infer grid dimensions based on grid size."""
        m = 0.2019348819251314
        b = 17.616929879377363  # Line of best fit + 1 (for performance)
        return (int(m * len(self.bank) + b),) * 2

    @staticmethod
    def _make_grid(width: int, height: int) -> list[list[str | None]]:
        """Make an empty grid (a list of lists of chars)."""
        return [[None for _ in range(width)] for _ in range(height)]

    def _fill_empty_with_random(self) -> None:
        """Fill all grid values set to None to a random letter."""
        for i_r, row in enumerate(self.grid):
            for i_c, cell in enumerate(row):
                if cell is None:
                    self.grid[i_r][i_c] = random.choice(ALPHABET)

    def _place_word(
        self,
        word: str,
        starting_position: GridIndex,
        direction: Direction,
        *,
        force: bool = False,
    ) -> None:
        """Place a word on the grid."""
        indexes = tuple(
            WordSearch._iter_idxs(self.width, self.height, starting_position, direction)
        )
        if len(indexes) < len(word):
            raise PlacementError("word does not fit in grid")
        for idx, char in zip(indexes, word, strict=False):
            if force or self[idx] in (None, char):
                self[idx] = char
                if self._placed_letters.get(char) is None:
                    self._placed_letters[char] = {idx: {direction}}
                elif self._placed_letters[char].get(idx) is None:
                    self._placed_letters[char][idx] = {direction}
                else:
                    self._placed_letters[char][idx].add(direction)
            else:
                raise PlacementError("failed to place word")

    def _can_place_word(
        self, word: str, starting_position: GridIndex, direction: Direction
    ) -> bool:
        """Whether a word can be placed at a certain position."""
        indexes = tuple(
            WordSearch._iter_idxs(self.width, self.height, starting_position, direction)
        )
        if len(indexes) < len(word):
            return False
        not_already_placed = False
        for idx, char in zip(indexes, word, strict=False):
            val = self[idx]
            if val is None:
                not_already_placed = True
            if self._grid_index_is_in_bounds(idx) and val not in (None, char):
                return False
        return not_already_placed

    @cache
    @staticmethod
    def _iter_idxs(
        width: int, height: int, starting_position: GridIndex, direction: Direction
    ) -> list[GridIndex]:
        operators = STEP_OPERATORS[direction]
        if not WordSearch._grid_index_is_in_param_bounds(
            width, height, starting_position
        ):
            raise ValueError(f"starting_position {starting_position} is out of bounds")
        cursor = starting_position
        result = []
        first_pass = True
        while first_pass or WordSearch._grid_index_is_in_param_bounds(
            width, height, cursor
        ):
            first_pass = False
            result.append(cursor)
            if (op := operators[0]) is not None:
                cursor = op(cursor[0], 1), cursor[1]
            if (op := operators[1]) is not None:
                cursor = cursor[0], op(cursor[1], 1)
        return result

    @cache
    def _step(
        self, starting_position: GridIndex, steps: int, direction: Direction
    ) -> GridIndex:
        if steps == 0:
            return starting_position
        width_op, height_op = STEP_OPERATORS[direction]
        result = (
            starting_position[0]
            if width_op is None
            else width_op(starting_position[0], steps),
            starting_position[1]
            if height_op is None
            else height_op(starting_position[1], steps),
        )
        if WordSearch._grid_index_is_in_param_bounds(self.width, self.height, result):
            return result
        raise ValueError("GridIndex is out of bounds")

    def _grid_index_is_in_bounds(self, index: GridIndex) -> bool:
        return WordSearch._grid_index_is_in_param_bounds(self.width, self.height, index)

    @staticmethod
    def _grid_index_is_in_param_bounds(
        width: int, height: int, index: GridIndex
    ) -> bool:
        return 0 <= index[0] < height and 0 <= index[1] < width

    @cache
    @staticmethod
    def _starting_positions(
        width: int, height: int, length: int
    ) -> tuple[tuple[GridIndex, Direction], ...]:
        """Get starting positions on an empty grid for a word of a certain length."""
        result: list[tuple[GridIndex, Direction]] = []
        for direction, generator in STARTING_POSITION_GENERATORS.items():
            result.extend((idx, direction) for idx in generator(width, height, length))
        return tuple(result)

    def populate_grid(self, max_attempts: int) -> None:
        """Populate the grid with the words in the bank."""
        if len(self.bank) == 0:
            return None
        if max(len(word) for word in self.bank) > min((self.height, self.width)):
            raise ValueError("max word length cannot exceed height or width")
        for _ in range(max_attempts):
            failed = False
            for word in self.bank:
                place_random = True
                if random.random() < self.connection_coefficient:
                    with suppress(PlacementError):
                        self.intersect_with_existing_word(word)
                        place_random = False
                        continue
                if place_random:
                    try:
                        self.place_random(word)
                    except PlacementError:
                        successfully_placed_word = False
                    else:
                        successfully_placed_word = True
                if not successfully_placed_word:
                    failed = True
                    break
            if not failed:
                break
        if failed:
            raise PlacementError(
                f"failed to create word search in {max_attempts} attempts"
            )

    def place_random(self, word: str) -> None:
        """Place a word on the board randomly."""
        starting_positions = list(
            WordSearch._starting_positions(self.width, self.height, len(word))
        )
        length = len(starting_positions)
        successfully_placed_word = False
        while length > 0:
            idx = random.randint(0, length - 1)
            position = starting_positions.pop(idx)
            length -= 1
            if self._can_place_word(word, *position):
                self._place_word(word, *position, force=True)
                successfully_placed_word = True
                break
        if not successfully_placed_word:
            raise PlacementError(f"no suitable placements for word '{word}'")

    def intersect_with_existing_word(self, word: str) -> None:
        """Place a word in intersection with an existing word if possible."""
        common_letters = list(set(word) & self._placed_letters.keys())
        directions = list(DIRECTION_OPPOSITES)
        random.shuffle(common_letters)
        for letter in common_letters:
            random.shuffle(directions)
            placed_letter_idxs = list(self._placed_letters[letter].items())
            random.shuffle(placed_letter_idxs)
            char_idxs_in_word = [i for i, char in enumerate(word) if char == letter]
            for direction in directions:
                for grid_index, original_directions in placed_letter_idxs:
                    if direction in [
                        DIRECTION_OPPOSITES[o_d] for o_d in original_directions
                    ] + list(original_directions):
                        continue
                    for char_idx in char_idxs_in_word:
                        try:
                            starting_position = self._step(
                                grid_index, char_idx, DIRECTION_OPPOSITES[direction]
                            )
                        except ValueError:
                            pass
                        else:
                            if self._can_place_word(word, starting_position, direction):
                                self._place_word(
                                    word, starting_position, direction, force=True
                                )
                                return None
        raise PlacementError("could not place word in intersection with existing word")

    def to_html(self) -> str:
        """Output word search as HTML table."""
        result = (
            "<!DOCTYPE html><style>table {font-family: Courier; font-size: 16pt; "
            "margin: auto;} td {padding-left: 8pt;} h1 {margin: auto; padding: 15pt; "
            'font-family: "Arial", "Helvetica", sans-serif; text-align: center;} '
            "#bank {font-size: 12pt; margin: auto; padding-top: 10pt; font-family: "
            '"Arial", "Helvetica", sans-serif;}  #bank td {padding-left: 15pt; '
            "padding-right: 15pt; }</style><html><body>"
        )
        if self.title is not None:
            result += f"<h1>{self.title}</h1>"
        result += "<table>"
        for row in self.grid:
            result += "<tr>"
            for cell in row:
                result += f"<td>{cell}</td>"
            result += "</tr>"
        result += "</table>"
        result += '<table id="bank">'
        for row_ in batched(self._case_sensitive_bank, 4):
            result += "<tr>"
            for word in row_:
                result += f"<td>{word}</td>"
            result += "</tr>"
        result += "</table>"
        result += "</body></html>"
        return result

    def write_html(self, path: str, *, overwrite: bool = False) -> None:
        """Write word search to an HTML file."""
        with open(path, "w" if overwrite else "x") as file:
            file.write(self.to_html())
