# -*- coding: utf-8 -*-
import pathlib
from json import loads
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import List, Tuple, Union
from .utils import strip_lower

__all__ = ["SprintScheduleStore"]


class SprintScheduleStore:
    def __init__(self) -> None:
        self.store: List[Tuple[str, int]] = []

    def load(self, content: str):
        """
        Load json string to generate the priority list

        :param content:
            JSON string content
        """
        if content is None:
            return

        try:
            raw_data = loads(content)
        except JSONDecodeError as e:
            raise SyntaxError(
                f"""The structure of sprint schedule file is wrong.
                Hint: {e.msg} in line {e.lineno}:{e.colno}."""
            ) from e

        priority = 0
        sprints: List[str] = []
        for raw_item in raw_data:
            for name, configuration in raw_item.items():
                if strip_lower(name) in strip_lower("priority"):
                    if configuration is None or not isinstance(configuration, int):
                        # Just skip invalid items.
                        continue
                    priority = configuration
                if strip_lower(name) in strip_lower("sprints"):
                    if configuration is None or not isinstance(configuration, list):
                        continue
                    for sprint in configuration:
                        if isinstance(sprint, str) and len(sprint) > 0:
                            sprints.append(sprint)

            for sprint in sprints:
                self.store.append((sprint, priority))
            sprints.clear()
            priority = 0

    def load_file(self, file: Union[str, Path]):
        """
        Load json file to generate the excel definition

        :param file:
            JSON file location
        """

        if (
            file is None
            or not pathlib.Path(file).is_absolute()
            or not pathlib.Path(file).exists()
        ):
            raise FileNotFoundError(
                f"""Please make sure the sprint schedule file exist 
                and the path should be absolute. File: {file}."""
            )

        with open(file=file, mode="r", encoding="utf-8") as schedule_file:
            try:
                self.load(schedule_file.read())
            finally:
                schedule_file.close()

    def get_priority(self, sprint: str) -> int:
        for item in self.store:
            if sprint.upper() in item[0].upper():
                return item[1]
        return 0

    def total_count(self) -> int:
        return len(self.store)
