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

    def __init__(self, input: str, part_one_answer: str, part_two_answer: str):
        self.input: str = input
        self.part_one_answer: str = part_one_answer
        self.part_two_answer: str = part_two_answer

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
    """Stores input data required by advent solutions"""

    @abstractmethod
    def set(self, day: int, input: str):
        """Stores input for the given day."""
        pass

    @abstractmethod
    def get(self, day: int) -> str:
        """Retrieve input for the given day or throws an exception if there is no input for the day."""
        pass

    @abstractmethod
    def days(self) -> list[int]:
        """Get a list of days with input sorted in ascending order."""
        pass


class FileBackedPuzzleStore:
    """Stores inputs on the file system and encrypts the data prior to storage."""

    def __init__(self, repo_dir: Path) -> None:
        self.repo_dir: Path = repo_dir

    def set(self, day: int, data: PuzzleData):
        day_dir = self.repo_dir / str(day)

        # Create the directory for the day if it does not already exist.
        if not day_dir.exists():
            day_dir.mkdir()

        # Write the puzzle data to disk.
        self._save_field(day, INPUT_FILE_NAME, data.input, obscure=True)
        self._save_field(day, PART_ONE_ANSWER_FILE_NAME, data.part_one_answer)
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

        return PuzzleData(input, part_one_answer, part_two_answer)

    def _load_field(
        self, day: int, field_file_name: str, unobscure: bool = False
    ) -> str:
        input_path = self.repo_dir / str(day) / field_file_name

        if not input_path.exists():
            raise Exception("TODO file does not exist")
        else:
            with input_path.open("rb") as f:
                file_bytes = f.read()

                if unobscure:
                    return zlib.decompress(b64d(file_bytes)).decode("utf-8")
                else:
                    return file_bytes.decode("utf-8")

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
