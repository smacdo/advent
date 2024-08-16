from dataclasses import dataclass
from pathlib import Path
from typing import Generator

import importlib
import os
import re


@dataclass
class SolutionPlugin:
    module_path: Path
    year: int
    day: int

    def __init__(self, module_path: Path, year: int, day: int):
        self.module_path = module_path
        self.year = year
        self.day = day

    def __str__(self) -> str:
        return str(self.module_path)


def enumerate_solution_plugins() -> Generator[SolutionPlugin, None, None]:
    """
    Yields all of the solution plugins in the project.

    A solution plugin is a python file located in `advent/solutions/yYYYY/dayDD.py`
    with YYYY being the solution year and DD being the solution day.
    """
    # Look for all the years located in the solutions directory.
    year_dir_re = re.compile("^y(\\d{4,4})$")
    day_dir_re = re.compile("^day(\\d{1,2})\\.py$")

    solver_plugin_dir = Path("advent/solutions")

    for plugin_dir_entry in os.listdir(solver_plugin_dir):
        match = year_dir_re.match(plugin_dir_entry)
        path = solver_plugin_dir / plugin_dir_entry

        # Only enumerate directories that match the years naming pattern.
        if match and os.path.isdir(path):
            # This is a solutions directory for a specific year! Extract the
            # actual year value from the match.
            year = int(match.group(1))

            # Enumerate this directory and look for python modules that match
            # the per-day naming pattern.
            for year_dir_entry in os.listdir(solver_plugin_dir / plugin_dir_entry):
                path = solver_plugin_dir / plugin_dir_entry / year_dir_entry
                match = day_dir_re.match(year_dir_entry)

                if match:
                    day = int(match.group(1))
                    yield SolutionPlugin(path, year, day)


def load_all_solutions():
    """
    Loads all of the solution plugins that are located in the package advent.solutions.yNNNN.dNN
    """
    for plugin in enumerate_solution_plugins():
        importlib.import_module(f"advent.solutions.y{plugin.year}.day{plugin.day}")
