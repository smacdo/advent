from typing import List, Optional
from bs4 import BeautifulSoup
import logging
import re
import requests


logger = logging.getLogger(__name__)


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


class AocClient:
    """Interacts with the Advent of Code website."""

    def __init__(self, login_config: AocLoginConfig):
        self.headers = {
            "cookie": f"session={login_config.session_id}",
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

        for element in soup.find(class_="calendar").find_all("a"):
            result = re.search("(\\d+)$", element["href"])
            day = int(result[1])

            part_one_solved = (
                True if element["aria-label"].find("one star") != -1 else False
            )

            part_two_solved = (
                True if element["aria-label"].find("two star") != -1 else False
            )

            days.append(AocCalendarDay(day, part_one_solved, part_two_solved))

        days.sort(key=lambda x: x.day)
        return days
