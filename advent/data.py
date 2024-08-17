from abc import ABC, abstractmethod
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import zlib

# TODO: Use encryption rather than merely obscuring the input


INPUT_FILE_NAME = "input.txt"
PART_ONE_ANSWER_FILE_NAME = "part-1-answer.txt"
PART_TWO_ANSWER_FILE_NAME = "part-2-answer.txt"


class AnswerResponse(Enum):
    Ok = 1
    Unknown = 2
    Wrong = 3
    TooLow = 4
    TooHigh = 5

    def is_ok(self) -> bool:
        return self == AnswerResponse.Ok

    def is_wrong(self) -> bool:
        return (
            self == AnswerResponse.Wrong
            or self == AnswerResponse.TooLow
            or self == AnswerResponse.TooHigh
        )


@dataclass
class PartAnswerCache:
    """Stores correct and incorrect answers for either part one or part two of
    a question.

    This class also supports setting optional low and high integer boundaries
    (eg, "12 is too high"). These boundaries will be checked in `check_answers`
    to reduce the number of additional checks needed.
    """

    correct_answer: str | None
    wrong_answers: set[str]
    low_boundary: int | None
    high_boundary: int | None

    def __init__(
        self,
        correct_answer: str | None = None,
        wrong_answers: set[str] | None = None,
        low_boundary: int | None = None,
        high_boundary: int | None = None,
    ):
        self.correct_answer = correct_answer
        self.wrong_answers = set() if wrong_answers is None else wrong_answers
        self.low_boundary = low_boundary
        self.high_boundary = high_boundary

    def check_answer(self, answer: str | int) -> AnswerResponse:
        """Check if the answer is known to be correct or incorrect. Answers that
        cannot be checked will be returned as `AnswerResponse.Unknown`."""
        maybe_int = PartAnswerCache._cast_int(answer)

        if maybe_int is not None:
            if self.low_boundary is not None and maybe_int <= self.low_boundary:
                return AnswerResponse.TooLow
            elif self.high_boundary is not None and maybe_int >= self.high_boundary:
                return AnswerResponse.TooHigh

        answer = str(answer)

        if answer in self.wrong_answers:
            return AnswerResponse.Wrong

        if self.correct_answer is not None:
            if answer == self.correct_answer:
                return AnswerResponse.Ok
            else:
                return AnswerResponse.Wrong
        else:
            return AnswerResponse.Unknown

    def add_wrong_answer(self, answer: str) -> int:
        """Adds a wrong answer entry to the cache."""
        self.wrong_answers.add(answer)
        return len(self.wrong_answers)

    def set_correct_answer(self, answer: str) -> None:
        """Sets the correct answer in the cache."""
        self.correct_answer = answer

    def set_high_boundary(self, answer: int) -> int:
        """
        Sets a high boundary value in the cache.

        If the cache has an existing high boundary then the lowest value will be
        used as the new high boundary.

        Any integer formatted answer in `check_answer` will be returned as
        `AnswerResponse.TooHigh` if it equals or is larger than the high boundary.
        """
        if self.high_boundary is None or answer < self.high_boundary:
            self.high_boundary = answer
        return self.high_boundary

    def set_low_boundary(self, answer: int) -> int:
        """
        Sets a low boundary value in the cache.

        If the cache has an existing low boundary then the highest value will be
        used as the new low boundary.

        Any integer formatted answer in `check_answer` will be returned as
        `AnswerResponse.TooLow` if it equals or is smaller than the low boundary.
        """

        if self.low_boundary is None or answer > self.low_boundary:
            self.low_boundary = answer
        return self.low_boundary

    @staticmethod
    def _cast_int(s: str | int) -> int | None:
        if isinstance(s, int):
            return s
        elif isinstance(s, str) and (
            s.isdigit() or (s.startswith("-") and s[1:].isdigit())
        ):
            return int(s)
        else:
            return None

    def serialize(self) -> str:
        """
        Writes the answer cache to a multi-line string that can be written to disk.
        """

        # Answers cannot have a newline!
        if self.correct_answer is not None and self.correct_answer.find("\n") != -1:
            raise ValueError("cannot serialize a correct answer that has a newline")

        for a in self.wrong_answers:
            if a.find("\n") != -1:
                raise ValueError("cannot serialize a wrong answer that has a newline")

        # Generate formatted strings for attributes in this class.
        # Wrong answers should be sorted so that are serialized in a stable order.
        correct_str = (
            f"= {self.correct_answer}\n" if self.correct_answer is not None else ""
        )
        low_bounds = f"[ {self.low_boundary}\n" if self.low_boundary is not None else ""
        high_bounds = (
            f"] {self.high_boundary}\n" if self.high_boundary is not None else ""
        )

        sorted_wrong_answers = list(self.wrong_answers)
        sorted_wrong_answers.sort()

        wrong_answers = "\n".join([f"X {x}" for x in sorted_wrong_answers])

        return f"{correct_str}{low_bounds}{high_bounds}{wrong_answers}"

    @staticmethod
    def deserialize(text: str) -> "PartAnswerCache":
        """
        Parses a serialized answer cache string as a new `PartAnswerCache` value.
        """

        pac = PartAnswerCache()

        for line in text.splitlines():
            ty, answer = line.split(" ", maxsplit=1)

            if answer is None:
                raise ValueError("answer was None or missing when deserializing")

            answer = answer.strip()

            if answer == "":
                raise ValueError(
                    "answer was blank after stripping whitespace when deserializing"
                )

            if ty == "=":
                pac.set_correct_answer(answer)
            elif ty == "X":
                pac.add_wrong_answer(answer)
            elif ty == "[":
                int_answer = PartAnswerCache._cast_int(answer)

                if int_answer is None:
                    raise ValueError(
                        "low boundary must be an integer when deserializing"
                    )
                else:
                    pac.set_low_boundary(int_answer)
            elif ty == "]":
                int_answer = PartAnswerCache._cast_int(answer)

                if int_answer is None:
                    raise ValueError(
                        "high boundary must be an integer when deserializing"
                    )
                else:
                    pac.set_high_boundary(int_answer)
            else:
                raise ValueError(
                    f"unknown or missing answer type `{ty}` when deserializing"
                )

        return pac


class PuzzleData:
    """Holds puzzle input and answer data."""

    def __init__(
        self,
        input: str,
        part_one_answer: PartAnswerCache,
        part_two_answer: PartAnswerCache,
    ):
        self.input: str = input
        self.part_one_answer: PartAnswerCache = part_one_answer
        self.part_two_answer: PartAnswerCache = part_two_answer

    def __eq__(self, value: object) -> bool:
        if type(value) is PuzzleData:
            return (
                self.input == value.input
                and self.part_one_answer == value.part_one_answer
                and self.part_two_answer == value.part_two_answer
            )
        else:
            return False


class PuzzleStore(ABC):
    """Stores puzzle data required by advent solutions"""

    @abstractmethod
    def get(self, year: int, day: int) -> PuzzleData:
        """Retrieve puzzle data for the given day or throws an exception."""
        pass

    @abstractmethod
    def set(self, year: int, day: int, input: PuzzleData):
        """Stores puzzle data for the given day."""
        pass

    @abstractmethod
    def add_day(self, year: int, day: int, input: str):
        """Sets input for the given day."""
        pass

    @abstractmethod
    def has_day(self, year: int, day: int) -> bool:
        """Check if there is puzzle data for the given day"""

    @abstractmethod
    def days(self, year: int) -> list[int]:
        """Get a list of days with puzzle data sorted in ascending order."""
        pass


class PuzzleStoreFileMissing(Exception):
    def __init__(self, year: int, day: int, file_path: Path) -> None:
        super().__init__(
            f"Failed to open puzzle data file for year {year} day {day}, path = `{file_path}`"
        )


class FileBackedPuzzleStore(PuzzleStore):
    """Stores inputs on the file system and encrypts the data prior to storage."""

    def __init__(self, data_dir: Path) -> None:
        self.repo_dir: Path = data_dir

    def get(self, year: int, day: int) -> PuzzleData:
        input = self._load_field(year, day, INPUT_FILE_NAME, unobscure=True)

        if input is None:
            raise PuzzleStoreFileMissing(
                year=year, day=day, file_path=self.repo_dir / f"y{year}" / str(day)
            )

        part_one_answer_data = self._load_field(year, day, PART_ONE_ANSWER_FILE_NAME)
        part_one_answer = (
            PartAnswerCache.deserialize(part_one_answer_data)
            if part_one_answer_data is not None
            else PartAnswerCache()
        )
        part_two_answer_data = self._load_field(year, day, PART_TWO_ANSWER_FILE_NAME)
        part_two_answer = (
            PartAnswerCache.deserialize(part_two_answer_data)
            if part_two_answer_data is not None
            else PartAnswerCache()
        )

        return PuzzleData(
            input,
            part_one_answer,
            part_two_answer,
        )

    def _load_field(
        self, year: int, day: int, field_file_name: str, unobscure: bool = False
    ) -> str | None:
        input_path = self.repo_dir / f"y{year}" / str(day) / field_file_name

        if not input_path.exists():
            return None
        else:
            with input_path.open("rb") as f:
                file_bytes = f.read()

                if unobscure:
                    return zlib.decompress(b64d(file_bytes)).decode("utf-8")
                else:
                    return file_bytes.decode("utf-8")

    def set(self, year: int, day: int, input: PuzzleData):
        day_dir = self.repo_dir / f"y{year}" / str(day)

        # Create the directory for the day if it does not already exist.
        if not day_dir.exists():
            day_dir.mkdir(parents=True)

        # Write the puzzle data to disk.
        self._save_field(year, day, INPUT_FILE_NAME, input.input, obscure=True)
        part_one_answer_data = input.part_one_answer.serialize()
        part_two_answer_data = input.part_two_answer.serialize()

        if part_one_answer_data != "":
            self._save_field(year, day, PART_ONE_ANSWER_FILE_NAME, part_one_answer_data)

        if part_two_answer_data != "":
            self._save_field(year, day, PART_TWO_ANSWER_FILE_NAME, part_two_answer_data)

    def _save_field(
        self,
        year: int,
        day: int,
        field_file_name: str,
        value: str,
        obscure: bool = False,
    ):
        with (self.repo_dir / f"y{year}" / str(day) / field_file_name).open("wb") as f:
            if obscure:
                f.write(b64e(zlib.compress(value.encode("utf-8"), 9)))
            else:
                f.write(value.encode("utf-8"))

    def add_day(self, year: int, day: int, input: str):
        self.set(year, day, PuzzleData(input, PartAnswerCache(), PartAnswerCache()))

    def has_day(self, year: int, day: int) -> bool:
        input_file = self.repo_dir / f"y{year}" / str(day) / INPUT_FILE_NAME
        return input_file.exists()

    def days(self, year: int) -> list[int]:
        d = [
            int(x.name)
            for x in (self.repo_dir / f"y{year}").iterdir()
            if x.is_dir() and x.name.isdigit()
        ]
        d.sort()
        return d


class MemoryBackedDataStore:
    """Stores inputs in memory without backing storage."""

    def __init__(self) -> None:
        super().__init__()
        self.inputs: dict[int, str] = dict()

    def set(self, day: int, input: str):
        self.inputs[day] = input

    def get(self, day: int) -> str:
        if day in self.inputs:
            return self.inputs[day]
        else:
            raise Exception("TODO: REPLACE ME")

    def days(self) -> list[int]:
        d = list(self.inputs.keys())
        d.sort()

        return d
