from abc import ABC, abstractmethod
from pathlib import Path

import zlib
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d

# TODO: Use encryption rather than merely obscuring the input


INPUT_FILE_NAME = "input.txt"
PART_ONE_ANSWER_FILE_NAME = "part-1-answer.txt"
PART_TWO_ANSWER_FILE_NAME = "part-2-answer.txt"


class PuzzleData:
    """Holds puzzle input and answer data."""

    def __init__(
        self, input: str, part_one_answer: str | None, part_two_answer: str | None
    ):
        self.input: str = input
        self.part_one_answer: str | None = part_one_answer
        self.part_two_answer: str | None = part_two_answer

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
    def set(self, day: int, input: str):
        """Stores puzzle data for the given day."""
        pass

    @abstractmethod
    def get(self, day: int) -> str:
        """Retrieve puzzle data for the given day or throws an exception."""
        pass

    @abstractmethod
    def has_day(self, day: int) -> bool:
        """Check if there is puzzle data for the given day"""

    @abstractmethod
    def days(self) -> list[int]:
        """Get a list of days with puzzle data sorted in ascending order."""
        pass


class PuzzleStoreFileMissing(Exception):
    def __init__(self, year: int, day: int, file_path: Path) -> None:
        super().__init__(
            f"Failed to open puzzle data file for year {year} day {day}, path = `{file_path}`"
        )


class FileBackedPuzzleStore:
    """Stores inputs on the file system and encrypts the data prior to storage."""

    def __init__(self, data_dir: Path, year: int) -> None:
        self.year: int = year
        self.repo_dir: Path = data_dir / f"y{year}"

    def set(self, day: int, data: PuzzleData):
        day_dir = self.repo_dir / str(day)

        # Create the directory for the day if it does not already exist.
        if not day_dir.exists():
            day_dir.mkdir(parents=True)

        # Write the puzzle data to disk.
        self._save_field(day, INPUT_FILE_NAME, data.input, obscure=True)

        if data.part_one_answer is not None:
            self._save_field(day, PART_ONE_ANSWER_FILE_NAME, data.part_one_answer)

        if data.part_two_answer is not None:
            self._save_field(day, PART_TWO_ANSWER_FILE_NAME, data.part_two_answer)

    def _save_field(
        self, day: int, field_file_name: str, value: str, obscure: bool = False
    ):
        with (self.repo_dir / str(day) / field_file_name).open("wb") as f:
            if obscure:
                f.write(b64e(zlib.compress(value.encode("utf-8"), 9)))
            else:
                f.write(value.encode("utf-8"))

    def get(self, day: int) -> PuzzleData:
        input = self._load_field(day, INPUT_FILE_NAME, unobscure=True)
        part_one_answer = self._load_field(day, PART_ONE_ANSWER_FILE_NAME)
        part_two_answer = self._load_field(day, PART_TWO_ANSWER_FILE_NAME)

        if input is None:
            raise PuzzleStoreFileMissing(
                year=self.year, day=day, file_path=self.repo_dir / str(day)
            )

        return PuzzleData(input, part_one_answer, part_two_answer)

    def _load_field(
        self, day: int, field_file_name: str, unobscure: bool = False
    ) -> str | None:
        input_path = self.repo_dir / str(day) / field_file_name

        if not input_path.exists():
            return None
        else:
            with input_path.open("rb") as f:
                file_bytes = f.read()

                if unobscure:
                    return zlib.decompress(b64d(file_bytes)).decode("utf-8")
                else:
                    return file_bytes.decode("utf-8")

    def has_day(self, day: int) -> bool:
        input_file = self.repo_dir / str(day) / INPUT_FILE_NAME
        return input_file.exists()

    def days(self) -> list[int]:
        d = [
            int(x.name)
            for x in self.repo_dir.iterdir()
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
