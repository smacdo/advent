from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from enum import Enum

import logging
import os
import re
import requests

from donner.solution import Part


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


class ClientException(Exception):
    pass


class HttpError(ClientException):
    result_code: int

    def __init__(self, result_code: int, message: str | None = None):
        self.result_code = result_code

        if message is None:
            message = f"Unexpected HTTP {result_code}"

        super().__init__(message)


_AOC_HTTP_INVALID_SESSION = 400
_AOC_HTTP_NOT_FOUND = 404


class ResourceNotFound(HttpError):
    def __init__(self):
        super().__init__(
            message="the requested http resource was not found",
            result_code=_AOC_HTTP_NOT_FOUND,
        )


class InvalidSession(HttpError):
    def __init__(self):
        super().__init__(
            message="authentication failed - check the session id in `.aoc_config`",
            result_code=_AOC_HTTP_INVALID_SESSION,
        )


class ExpectedConfigKeyMissing(ClientException):
    key: str
    config_path: str | None

    def __init__(self, key: str, config_path: str | None):
        super().__init__(f"{key} config value must be set in {config_path}")
        self.key = key
        self.config_path = config_path


class UnknownPostAnswerError(ClientException):
    def __init__(self, response_text: str):
        super().__init__(
            f"answer submission endpoint returned unexpected response\n```{response_text}\n```\n"
        )


def parse_http_response(response: requests.Response) -> str:
    if response.status_code == _AOC_HTTP_INVALID_SESSION:
        raise InvalidSession()
    elif response.status_code == _AOC_HTTP_NOT_FOUND:
        raise ResourceNotFound()
    elif response.status_code > 400:
        raise HttpError(response.status_code)
    return response.text.strip()


class AocClientConfig:
    """Stores a username and Advent of Code session id used by the Advent of Code
    client class."""

    password: str
    session_id: str
    pretend_submit: bool

    def __init__(self, password: str, session_id: str):
        self.password = password
        self.session_id = session_id
        self.pretend_submit = True

    @staticmethod
    def load_from_str(
        file_text: str, config_path: str | None = None
    ) -> "AocClientConfig":
        """Create a client config from the contents of a file like string"""

        # Iterate through the lines in the file with the expectation each line
        # has the format `KEY = VALUE`. Extract the password and session_id
        # key values - any other key should be ignored.
        password: str | None = None
        session_id: str | None = None

        for line in file_text.splitlines():
            line = line.strip()

            if line == "" or line.startswith("#"):
                continue

            name, value = line.split("=", maxsplit=1)

            name = name.strip()
            value = value.strip()

            if name == "password":
                password = value
            elif name == "session_id":
                session_id = value
            else:
                logger.info(f"unknown config key `{name}`")

        # Make sure the password and session_id were loaded
        if password is None or password == "":
            raise ExpectedConfigKeyMissing("password", config_path=config_path)

        if session_id is None or session_id == "":
            raise ExpectedConfigKeyMissing("session_id", config_path=config_path)

        return AocClientConfig(password=password, session_id=session_id)

    @staticmethod
    def load_from_file(file_name: str = ".aoc_login") -> "AocClientConfig":
        """Tries to load the login configuration from the provided file path"""
        with open(file_name, "r") as file:
            return AocClientConfig.load_from_str(
                file.read(), config_path=os.path.abspath(file_name)
            )


class AocDay:
    """An Advent of Calendar code puzzle day."""

    year: int
    day: int
    part_one_solved: bool
    part_two_solved: bool

    def __init__(
        self, year: int, day: int, part_one_solved: bool, part_two_solved: bool
    ):
        self.year = year
        self.day = day
        self.part_one_solved = part_one_solved
        self.part_two_solved = part_two_solved

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
    def fetch_days(self, year: int) -> list[AocDay]:
        pass

    @abstractmethod
    def submit_answer(
        self, year: int, day: int, part: Part, answer: str
    ) -> SubmitResponse:
        pass


class AocWebClient(AocClient):
    """Interacts with the Advent of Code website."""

    config: AocClientConfig

    def __init__(self, config: AocClientConfig):
        self.config = config
        self.headers = {
            "Cookie": f"session={config.session_id}",
            "user-agent": "github.com/smacdo/advent [email: dev@smacdo.com]",
        }

    def fetch_input_for(self, year: int, day: int) -> str:
        """Returns the input data for the given day and year. Input data is unique to each user and
        should not be stored in plaintext at the request of the Advent of Code creator."""
        url = f"https://adventofcode.com/{year}/day/{day}/input"
        return parse_http_response(requests.get(url, headers=self.headers))

    def fetch_days(self, year: int) -> list[AocDay]:
        """Fetches a list of available Advent of Code days for a given year along with information
        showing if each day was partially or fully completed."""
        url = f"https://adventofcode.com/{year}/"
        page = parse_http_response(requests.get(url, headers=self.headers))
        soup = BeautifulSoup(page, "html.parser")
        days = []

        for element in soup.find(class_="calendar").fincd_all("a"):  # type: ignore
            result = re.search("(\\d+)$", element["href"])
            day = int(result[1])  # type: ignore

            part_one_solved = (
                True if element["aria-label"].find("one star") != -1 else False
            )

            part_two_solved = (
                True if element["aria-label"].find("two star") != -1 else False
            )

            days.append(
                AocDay(
                    year=year,
                    day=day,
                    part_one_solved=part_one_solved,
                    part_two_solved=part_two_solved,
                )
            )

        days.sort(key=lambda x: x.day)
        return days

    def submit_answer(
        self, year: int, day: int, part: Part, answer: str
    ) -> SubmitResponse:
        logger.info(f"submitting answer `{answer}` for year {year} day {day}")

        if self.config.pretend_submit:
            raise ClientException("cannot submit answer if `pretend_submit` = False!")

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

        raise UnknownPostAnswerError(soup.prettify())
