from abc import ABC, abstractmethod
from typing import List, Optional
from bs4 import BeautifulSoup
from enum import Enum
import logging
import re
import requests

from advent.solution import Part


logger = logging.getLogger(__name__)


class SubmitResponse(Enum):
    """
    Response from the Advent of Code service when submitting an answer.

    Ok: The answer was accepted because it was correct.
    TooSoon: An answer was submitted recently. Please wait before trying again.
    AlreadyAnswered: A correct answer has already been accepted.
    Wrong: The answer is wrong. No hint is provided.
    TooLow: The answer is wrong because it is too low.
    TooHigh: The answer is wrong because it is too high.
    """

    Ok = 1
    TooSoon = 2
    AlreadyAnswered = 3
    Wrong = 4
    TooLow = 5
    TooHigh = 6

    def is_wrong(self):
        """Returns true if the response indicates the answer was incorrect."""
        return (
            self == SubmitResponse.Wrong
            or self == SubmitResponse.TooLow
            or self == SubmitResponse.TooHigh
        )


class HttpError(Exception):
    def __init__(self, error_code: int):
        super().__init__("Unexpected HTTP {error_code}")


class ResourceNotFound(Exception):
    def __init__(self):
        super().__init__("the requested http resource was not found")


class InvalidSession(Exception):
    def __init__(self):
        super().__init__(
            "authentication failed - check the session id in `.aoc_session`"
        )


def parse_http_response(response: requests.Response) -> str:
    if response.status_code == 400:
        raise InvalidSession()
    elif response.status_code == 404:
        raise ResourceNotFound()
    elif response.status_code > 400:
        raise HttpError(response.status_code)
    return response.text.strip()


class AocLoginConfig:
    """Stores a username and Advent of Code session id used by the Advent of Code
    client class."""

    def __init__(self, username: str, session_id: str):
        self.username: str = username
        self.session_id: str = session_id

    @staticmethod
    def parse_login_config(file_lines: List[str]) -> Optional["AocLoginConfig"]:
        """Parses the configuration file which is two lines. The first line is the username and the
        second line is the session id"""

        if len(file_lines) != 2:
            # TODO: Better error message?
            logging.error("expected two lines in login config file")
            return None

        username = file_lines[0].rstrip()
        session_id = file_lines[1].rstrip()

        return AocLoginConfig(username, session_id)

    @staticmethod
    def try_load_from_file(file_name: str = ".aoc_login") -> Optional["AocLoginConfig"]:
        """Tries to load the login configuration from the provided file path"""
        try:
            with open(file_name, "r") as file:
                lines = [line.rstrip() for line in file]
                return AocLoginConfig.parse_login_config(lines)
        except FileNotFoundError:
            return None


class AocCalendarDay:
    """Represents an Advent of Calendar day."""

    def __init__(self, day: int, part_one_solved: bool, part_two_solved: bool):
        self.day: int = day
        self.part_one_solved: bool = part_one_solved
        self.part_two_solved: bool = part_two_solved

    def __str__(self) -> str:
        if self.part_two_solved:
            return f"{self.day}**"
        elif self.part_one_solved:
            return f"{self.day}*"
        else:
            return f"{self.day}"


class AocClient(ABC):
    """Interacts with the Advent of Code website."""

    @abstractmethod
    def fetch_input_for(self, year: int, day: int) -> str:
        pass

    @abstractmethod
    def fetch_days(self, year: int) -> List[AocCalendarDay]:
        pass

    @abstractmethod
    def submit_answer(
        self, year: int, day: int, part: Part, answer: str
    ) -> SubmitResponse:
        pass


class AocWebClient(AocClient):
    """Interacts with the Advent of Code website."""

    def __init__(self, login_config: AocLoginConfig):
        self.headers = {
            "cookie": f"session={login_config.session_id}",
            "user-agent": "github.com/smacdo/advent [email: dev@smacdo.com]",
        }

    def fetch_input_for(self, year: int, day: int) -> str:
        """Returns the input data for the given day and year. Input data is unique to each user and
        should not be stored in plaintext at the request of the Advent of Code creator."""
        url = f"https://adventofcode.com/{year}/day/{day}/input"
        return parse_http_response(requests.get(url, headers=self.headers))

    def fetch_days(self, year: int) -> List[AocCalendarDay]:
        """Fetches a list of available Advent of Code days for a given year along with information
        showing if each day was partially or fully completed."""
        url = f"https://adventofcode.com/{year}/"
        page = parse_http_response(requests.get(url, headers=self.headers))
        soup = BeautifulSoup(page, "html.parser")
        days = []

        for element in soup.find(class_="calendar").find_all("a"):  # type: ignore
            result = re.search("(\\d+)$", element["href"])
            day = int(result[1])  # type: ignore

            part_one_solved = (
                True if element["aria-label"].find("one star") != -1 else False
            )

            part_two_solved = (
                True if element["aria-label"].find("two star") != -1 else False
            )

            days.append(AocCalendarDay(day, part_one_solved, part_two_solved))

        days.sort(key=lambda x: x.day)
        return days

    def submit_answer(
        self, year: int, day: int, part: Part, answer: str
    ) -> SubmitResponse:
        logger.info("submitting answer `{answer}` for year {year} day {day}")

        page = parse_http_response(
            requests.post(
                f"https://adventofcode.com/{year}/day/{day}/answer",
                data={"level": "1" if part == Part.One else "2", "answer": answer},
                headers=self.headers,
            )
        )

        soup = BeautifulSoup(page, "html.parser")
        article_elem = soup.find("article")

        if article_elem is not None:
            for message in article_elem.stripped_strings:
                message = message.lower()

                if "the right answer" in message:
                    return SubmitResponse.Ok
                elif "answer is too low" in message:
                    return SubmitResponse.TooLow
                elif "answer is too high" in message:
                    return SubmitResponse.TooHigh
                elif "not the right answer" in message:
                    return SubmitResponse.Wrong
                elif "gave an answer too recently" in message:
                    return SubmitResponse.TooSoon
                elif "already complete it" in message:
                    return SubmitResponse.AlreadyAnswered

        # TODO: report the HTML as well so it can be analyzed
        raise Exception("answer submission endpoint returned unexpected response")
